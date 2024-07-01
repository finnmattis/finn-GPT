import math
import os
import time

import numpy as np
import tiktoken
import torch
import torch.distributed as dist
from torch.distributed import destroy_process_group, init_process_group
from torch.nn import functional as F
from torch.nn.parallel import DistributedDataParallel as DDP

from model import GPT, GPTConfig

####################################################################################################
#                                        Hyperparameters                                           #
####################################################################################################

# Batch
TOTAL_BATCH_SIZE = 524288 # 2**19 (nice number), ~0.5M, in number of tokens as in GPT-3 paper
MINI_BATCH_SIZE = 64 # micro batch size
BATCH_SEQ_LENGTH = 1024 # normally same as context_size - 1024 for GPT-2 - 2048 for GPT-3

# Learning Rate
MAX_LR = 6e-4 * 2 # 6e-4 for GPT-3 but prob conservative - could go up to 3x
MIN_LR = MAX_LR * 0.1
WARMUP_STEPS = 715
MAX_STEPS = 19073*5 # 19,073 steps is ~1 epoch, if data is 10B tokens and batch size 0.5M tokens

# Eval
EVAL_INTERVAL = 250
CHECKPOINT_INTERVAL = 500

SEED = 6+9+14+14 # FINN

####################################################################################################
#                                        Pytorch Setup                                             #
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
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"
    print(f"using device: {device}")

device_type = "cuda" if device.startswith("cuda") else "cpu"

torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed(SEED)

torch.set_float32_matmul_precision('high')

####################################################################################################
#                                        Data and Eval                                             #
####################################################################################################

def load_tokens(filename):
    tokens = np.load(filename)
    tokens = tokens.astype(np.int32)
    return torch.tensor(tokens, dtype=torch.long)

class DataLoader:
    def __init__(self, process_rank, num_processes, split):
        assert split in {'train', 'val'}
        self.process_rank = process_rank
        self.num_processes = num_processes

        # get the shard filenames
        data_root = "edu_fineweb10B"
        shards = os.listdir(data_root)
        shards = [s for s in shards if split in s]
        shards = sorted(shards)
        shards = [os.path.join(data_root, s) for s in shards]
        self.shards = shards
        assert len(shards) > 0, f"no shards found for split {split}"
        if master_process:
            print(f"found {len(shards)} shards for split {split}")
        self.reset()

    def reset(self):
        self.current_shard = 0
        self.tokens = load_tokens(self.shards[self.current_shard])
        self.current_position = MINI_BATCH_SIZE * BATCH_SEQ_LENGTH * self.process_rank

    def next_batch(self):
        B, T = MINI_BATCH_SIZE, BATCH_SEQ_LENGTH
        buf = self.tokens[self.current_position : self.current_position+B*T+1]
        x = (buf[:-1]).view(B, T)
        y = (buf[1:]).view(B, T)

        # advance the position in the tensor
        self.current_position += B * T * self.num_processes
        # if loading the next batch would be out of bounds, advance to next shard
        if self.current_position + (B * T * self.num_processes + 1) > len(self.tokens):
            self.current_shard = (self.current_shard + 1) % len(self.shards)
            self.tokens = load_tokens(self.shards[self.current_shard])
            self.current_position = B * T * self.process_rank
        return x, y

# helper function for HellaSwag eval
# takes tokens, mask, and logits, returns the index of the completion with the lowest loss
def get_most_likely_row(tokens, mask, logits):
    # evaluate the autoregressive loss at all positions
    shift_logits = (logits[..., :-1, :]).contiguous()
    shift_tokens = (tokens[..., 1:]).contiguous()
    flat_shift_logits = shift_logits.view(-1, shift_logits.size(-1))
    flat_shift_tokens = shift_tokens.view(-1)
    shift_losses = F.cross_entropy(flat_shift_logits, flat_shift_tokens, reduction='none')
    shift_losses = shift_losses.view(tokens.size(0), -1)

    # now get the average loss just for the completion region (where mask == 1), in each row
    shift_mask = (mask[..., 1:]).contiguous() # we must shift mask, so we start at the last prompt token
    masked_shift_losses = shift_losses * shift_mask

    # sum and divide by the number of 1s in the mask
    sum_loss = masked_shift_losses.sum(dim=1)
    avg_loss = sum_loss / shift_mask.sum(dim=1)

    # now we have a loss for each of the 4 completions the one with the lowest loss should be the most likely
    pred_norm = avg_loss.argmin().item()
    return pred_norm

####################################################################################################
#                                        Setup Train                                               #
####################################################################################################

enc = tiktoken.get_encoding("gpt2")

# create data loaders
assert TOTAL_BATCH_SIZE % (MINI_BATCH_SIZE * BATCH_SEQ_LENGTH * ddp_world_size) == 0, "make sure total_batch_size is divisible by B * T * ddp_world_size"
grad_accum_steps = TOTAL_BATCH_SIZE // (MINI_BATCH_SIZE * BATCH_SEQ_LENGTH * ddp_world_size)
if master_process:
    print(f"total desired batch size: {TOTAL_BATCH_SIZE}")
    print(f"=> calculated gradient accumulation steps: {grad_accum_steps}")
train_loader = DataLoader(process_rank=ddp_rank, num_processes=ddp_world_size, split="train")
val_loader = DataLoader(process_rank=ddp_rank, num_processes=ddp_world_size, split="val")

# create model
model = GPT(GPTConfig(vocab_size=50304)) # "nice" number
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
    if step % EVAL_INTERVAL == 0 or last_step:
        eval_val_loss()

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