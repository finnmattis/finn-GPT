import torch
from model import GPT, GPTConfig
import tiktoken
from torch.nn import functional as F

# TODO Add GPU function later - scared to interept GPUS


# get model
checkpoint_path = 'log/model_02000.pt'
checkpoint = torch.load(checkpoint_path)
print(f"val loss: {checkpoint['val_loss']}")
model = GPT(checkpoint["config"])
state_dict = checkpoint["model"]
state_dict = {key.replace('_orig_mod.', ''): value for key, value in state_dict.items()}
model.load_state_dict(state_dict)

# model = GPT.from_pretrained("gpt2")


enc = tiktoken.get_encoding("gpt2")
device = "cpu"

model.eval()
num_return_sequences = 1
max_length = 30
print("Enter a prompt: ")
prompt = input()
tokens = enc.encode(prompt)
tokens = torch.tensor(tokens, dtype=torch.long)
tokens = tokens.unsqueeze(0).repeat(num_return_sequences, 1)
xgen = tokens.to(device)
sample_rng = torch.Generator(device=device)
sample_rng.manual_seed(43)

while xgen.size(1) < max_length:
    # forward the model to get the logits
    with torch.no_grad():
        with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
            logits, loss = model(xgen) # (B, T, vocab_size)
        # take the logits at the last position
        logits = logits[:, -1, :] # (B, vocab_size)
        # get the probabilities
        probs = F.softmax(logits, dim=-1)
        # do top-k sampling of 50 (huggingface pipeline default)
        # topk_probs here becomes (5, 50), topk_indices is (5, 50)
        topk_probs, topk_indices = torch.topk(probs, 50, dim=-1)
        # select a token from the top-k probabilities
        # note: multinomial does not demand the input to sum to 1
        ix = torch.multinomial(topk_probs, 1, generator=sample_rng) # (B, 1)
        # gather the corresponding indices
        xcol = torch.gather(topk_indices, -1, ix) # (B, 1)
        # append to the sequence
        xgen = torch.cat((xgen, xcol), dim=1)


for i in range(num_return_sequences):
    tokens = xgen[i, :max_length].tolist()
    decoded = enc.decode(tokens)
    print(decoded)