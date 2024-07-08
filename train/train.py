import math
import os
import time

import tiktoken
import torch
import torch.distributed as dist
from torch.distributed import destroy_process_group, init_process_group
from torch.nn.parallel import DistributedDataParallel as DDP

import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # give acess to parent dir
from model import GPT, GPTConfig
from data_loader import FineWebLoader, OasstLoader
from tokenizer import get_tokenizer

TRAIN_STAGE = "finetune"
assert TRAIN_STAGE in ["pretrain", "finetune"]

####################################################################################################
#                                         Hyperparameters                                          #
####################################################################################################

if TRAIN_STAGE == "pretrain":
    # Batch
    TOTAL_BATCH_SIZE = 524288 # 2**19 (nice number), ~0.5M, in number of tokens as in GPT-3 paper
    MINI_BATCH_SIZE = 64 # micro batch size
    BATCH_SEQ_LENGTH = 1024 # normally same as context_size - 1024 for GPT-2 - 2048 for GPT-3

    # Learning Rate
    MAX_LR = 6e-4 * 2 # 6e-4 for GPT-3 but prob conservative - could go up to 3x
    MIN_LR = MAX_LR * 0.1
    WARMUP_STEPS = 715
    MAX_STEPS = 19073*5 # 19,073 steps is ~1 epoch, if data is 10B tokens and batch size 0.5M tokens
else:
    # Batch
    TOTAL_BATCH_SIZE = 16384 # fine-tune has much smaller batches so train on smth like A10
    MINI_BATCH_SIZE = 16 # micro batch size
    BATCH_SEQ_LENGTH = 1024 # need to maintain same from pretrain

    # Learning Rate
    MAX_LR = 3e-5 # Much slower learning rate for small adjustments
    MIN_LR = MAX_LR * 0.1
    WARMUP_STEPS = 50
    MAX_STEPS = 2000 # ~ 5 epochs

# Eval
EVAL_INTERVAL = 250
CHECKPOINT_INTERVAL = 500

SEED = 6+9+14+14 # FINN

####################################################################################################
#                                         Torch Setup                                              #
####################################################################################################


# torchrun command sets the env variables RANK, LOCAL_RANK, and WORLD_SIZE
ddp = int(os.environ.get('RANK', -1)) != -1 # is this a ddp run?
if ddp:
    assert torch.cuda.is_available(), "nedd CUDA"
    init_process_group(backend='nccl')
    ddp_rank = int(os.environ['RANK'])
    ddp_local_rank = int(os.environ['LOCAL_RANK'])
    ddp_world_size = int(os.environ['WORLD_SIZE'])
    device = f'cuda:{ddp_local_rank}'
    torch.cuda.set_device(device)
    master_process = ddp_rank == 0 # this process will do logging, checkpointing etc.
else:
    # vanilla, non-DDP run
    ddp_rank = 0
    ddp_local_rank = 0
    ddp_world_size = 1
    master_process = True
    # attempt to autodetect device
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
    print(f"using device: {device}")

device_type = "cuda" if device.startswith("cuda") else "cpu"

torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed(SEED)

torch.set_float32_matmul_precision('high')

enc = get_tokenizer()

# create data loaders
assert TOTAL_BATCH_SIZE % (MINI_BATCH_SIZE * BATCH_SEQ_LENGTH * ddp_world_size) == 0, "make sure total_batch_size is divisible by B * T * ddp_world_size"
grad_accum_steps = TOTAL_BATCH_SIZE // (MINI_BATCH_SIZE * BATCH_SEQ_LENGTH * ddp_world_size)
if master_process:
    print(f"total desired batch size: {TOTAL_BATCH_SIZE}")
    print(f"=> calculated gradient accumulation steps: {grad_accum_steps}")

if TRAIN_STAGE == "pretrain":
    train_loader = FineWebLoader(split="train", batch_size=MINI_BATCH_SIZE, block_size=BATCH_SEQ_LENGTH, process_rank=ddp_rank, num_processes=ddp_world_size)
    val_loader = FineWebLoader(split="val", batch_size=MINI_BATCH_SIZE, block_size=BATCH_SEQ_LENGTH, process_rank=ddp_rank, num_processes=ddp_world_size)

train_loader = OasstLoader(split="train", batch_size=MINI_BATCH_SIZE, block_size=BATCH_SEQ_LENGTH)
val_loader = OasstLoader(split="val", batch_size=MINI_BATCH_SIZE, block_size=BATCH_SEQ_LENGTH)

if TRAIN_STAGE == "pretrain":
    # from scratch
    model = GPT(GPTConfig(vocab_size=50304)) # "nice" number
else:
    # from checkpoint
    checkpoint_path = f"artifacts/base_model_70000.pt"
    checkpoint = torch.load(checkpoint_path, map_location=torch.device(device))
    print(f"Validation loss: {checkpoint['val_loss']}")
    model = GPT(checkpoint["config"])
    state_dict = checkpoint["model"]
    model.load_state_dict({key.replace('_orig_mod.', ''): value for key, value in state_dict.items()})


model.to(device)
use_compile = True
if use_compile:
    model = torch.compile(model)
if ddp:
    model = DDP(model, device_ids=[ddp_local_rank])
raw_model = model.module if ddp else model # always contains the "raw" unwrapped model

# setup logging
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"log.txt")
with open(log_file, "w") as f: # open for writing to clear the file
    pass

# lr function
def get_lr(it):
    if it < WARMUP_STEPS:
        return MAX_LR * (it+1) / WARMUP_STEPS # linear warmup
    if it > MAX_STEPS:
        return MIN_LR
    # cosine decay
    decay_ratio = (it - WARMUP_STEPS) / (MAX_STEPS - WARMUP_STEPS)
    assert 0 <= decay_ratio <= 1
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio)) # coeff starts at 1 and goes to 0
    return MIN_LR + coeff * (MAX_LR - MIN_LR)

# Eval val loss
def eval_val_loss():
    model.eval()
    if TRAIN_STAGE == "pretrain":
        val_loader.reset()
    with torch.no_grad():
        val_loss_accum = 0.0
        val_loss_steps = 20
        for _ in range(val_loss_steps):
            x, y = val_loader.next_batch()
            x, y = x.to(device), y.to(device)
            with torch.autocast(device_type=device_type, dtype=torch.bfloat16):
                logits, loss = model(x, y)
            loss = loss / val_loss_steps
            val_loss_accum += loss.detach()
    if ddp:
        dist.all_reduce(val_loss_accum, op=dist.ReduceOp.AVG)
    if master_process:
        print(f"validation loss: {val_loss_accum.item():.4f}")
        with open(log_file, "a") as f:
            f.write(f"{step} val {val_loss_accum.item():.4f}\n")
        if (step % CHECKPOINT_INTERVAL == 0 or last_step):
            print("checkpoint time!!!")
            checkpoint_path = os.path.join(log_dir, f"model_{step:05d}.pt")
            checkpoint = {
                'model': raw_model.state_dict(),
                'config': raw_model.config,
                'step': step,
                'val_loss': val_loss_accum.item()
            }
            torch.save(checkpoint, checkpoint_path)

####################################################################################################
#                                        Train                                                     #
####################################################################################################

optimizer = raw_model.configure_optimizers(weight_decay=0.1, learning_rate=6e-4, device_type=device_type, is_master_process=master_process)

for step in range(MAX_STEPS):
    t0 = time.time()
    last_step = (step == MAX_STEPS - 1)

    # once in a while evaluate our validation loss
    # if step % EVAL_INTERVAL == 0 or last_step:
        # eval_val_loss()

    # optim step
    model.train()
    optimizer.zero_grad()

    loss_accum = 0.0
    for micro_step in range(grad_accum_steps):
        x, y = train_loader.next_batch()
        x, y = x.to(device), y.to(device)

        with torch.autocast(device_type=device_type, dtype=torch.bfloat16):
            logits, loss = model(x, y)
        
        loss = loss / grad_accum_steps # we want mean not sum and loss accumulates with each minibatch
        loss_accum += loss.detach()
        if ddp:
            model.require_backward_grad_sync = (micro_step == grad_accum_steps - 1)
        loss.backward()

    if ddp:
        dist.all_reduce(loss_accum, op=dist.ReduceOp.AVG)

    # optimizer step
    norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    lr = get_lr(step)
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
    optimizer.step()

    # Stats
    torch.cuda.synchronize() # wait for the GPU to finish work
    dt = time.time() - t0
    tokens_processed = MINI_BATCH_SIZE * BATCH_SEQ_LENGTH * grad_accum_steps * ddp_world_size
    tokens_per_sec = tokens_processed / dt
    if master_process:
        print(f"step {step:5d} | loss: {loss_accum.item():.6f} | lr {lr:.4e} | norm: {norm:.4f} | dt: {dt*1000:.2f}ms | tok/sec: {tokens_per_sec:.2f}")
        with open(log_file, "a") as f:
            f.write(f"{step} train {loss_accum.item():.6f}\n")

if ddp:
    destroy_process_group()