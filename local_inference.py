import torch
from model import GPT
import tiktoken
from torch.nn import functional as F
import os
import sys

# Params:
MAX_LENGTH = 100
TEMPERATURE = .7
TOP_P = .9
FREQUENCY_PENALTY = .3

models = []

# Get model_num

filenames = os.listdir("artifacts")
for filename in filenames:
    if filename.startswith("model_") and filename.endswith(".pt"):
        models.append(f"{filename[6:-3]}")
models = sorted(models)
models_str = ""
for index, model in enumerate(models):
    models_str += f"finnGPT-{model}"
    if index == len(models) - 2:
        models_str += ", and "
    elif index < len(models) - 2:
        models_str += ", "

print(f"Here are the models in your artifacts folder: {models_str}. What finn-GPT checkpoint would you like to use? Please input the desired training step.")
while True:
    model_num = input()
    if model_num in models:
        break
    print("Please enter a valid training step")

# autodetect device
device = "cpu"
if torch.cuda.is_available():
    device = "cuda"
print(f"using device: {device}")

# get model from checkpoint
checkpoint_path = f"artifacts/model_{model_num}.pt"
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
sys.stdout.write(prompt)
sys.stdout.flush()
enc = tiktoken.get_encoding("gpt2")
tokens = enc.encode(prompt)
tokens = torch.tensor(tokens, dtype=torch.long)
tokens = tokens.unsqueeze(0)
xgen = tokens.to(device)

def top_p_sampling(logits, p, temperature, frequency_penalty, token_counts):
    # Temperature
    logits = logits / temperature
    
    # Apply frequency penalty
    for token, count in token_counts.items():
        logits[0][token] -= frequency_penalty * count
    
    # Top-P sampling
    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
    sorted_indices_to_remove = cumulative_probs > p
    
    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
    sorted_indices_to_remove[..., 0] = 0
    
    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
    logits[indices_to_remove] = float('-inf')
    
    # Sample
    probs = F.softmax(logits, dim=-1)
    return torch.multinomial(probs, 1)

token_counts = {}

while xgen.size(1) < MAX_LENGTH:
    with torch.no_grad():
        logits, _ = model(xgen)
        logits = logits[:, -1, :]
        
        xcol = top_p_sampling(logits, TOP_P, TEMPERATURE, 
                                FREQUENCY_PENALTY, token_counts)
        
        xgen = torch.cat((xgen, xcol), dim=1)

        latest_token = xcol.item()
        token_counts[latest_token] = token_counts.get(latest_token, 0) + 1
        
        decoded_token = enc.decode([latest_token])
        if decoded_token == "<|endoftext|>":
            break
        sys.stdout.write(decoded_token)
        sys.stdout.flush()