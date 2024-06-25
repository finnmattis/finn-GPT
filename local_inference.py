import torch
from model import GPT
import tiktoken
from torch.nn import functional as F
import os
import time

start = time.time()

# Params:
MAX_LENGTH = 30

# autodetect device
device = "cpu"
if torch.cuda.is_available():
    device = "cuda"
print(f"using device: {device}")

# get model from checkpoint
checkpoint_path = 'artifacts/model_60000.pt'
checkpoint = torch.load(checkpoint_path, map_location=torch.device(device))
print(f"Loading finn-GPT step {checkpoint['step']}")
print(f"val loss: {checkpoint['val_loss']}")
model = GPT(checkpoint["config"])
state_dict = checkpoint["model"]
model.load_state_dict({key.replace('_orig_mod.', ''): value for key, value in state_dict.items()})
model.eval()

# prompt -> tokens
print("Enter a prompt: ")
prompt = input()
os.system("clear")
print(prompt, end="")
enc = tiktoken.get_encoding("gpt2")
tokens = enc.encode(prompt)
tokens = torch.tensor(tokens, dtype=torch.long)
tokens = tokens.unsqueeze(0)
xgen = tokens.to(device)

while xgen.size(1) < MAX_LENGTH:
    with torch.no_grad():
        with torch.autocast(device_type=device, dtype=torch.bfloat16):
            logits, _ = model(xgen) # (1, T, vocab_size)
        # take the logits at the last position
        logits = logits[:, -1, :] # (1, vocab_size)
        # get the probabilities
        probs = F.softmax(logits, dim=-1)
        # do top-k sampling of 50
        topk_probs, topk_indices = torch.topk(probs, 50, dim=-1)
        # sample
        ix = torch.multinomial(topk_probs, 1) # (1, 1)
        # gather the corresponding indices
        xcol = torch.gather(topk_indices, -1, ix) # (1, 1)
        new_tok = enc.decode(xcol[0].tolist())
        print(enc.decode(xcol[0].tolist()), end="")
        # append to the sequence
        xgen = torch.cat((xgen, xcol), dim=1)

print(time.time() - start)