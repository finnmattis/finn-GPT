import torch
from model import GPT
import tiktoken
from torch.nn import functional as F
import os
import sys

# Params:
MAX_LENGTH = 1024
TEMPERATURE = .7
P = .9
FREQUENCY_PENALTY = .3

enc = tiktoken.get_encoding("gpt2")

# Get device
device = "cpu"
if torch.cuda.is_available():
    device = "cuda"
print(f"Using device: {device}")


print("Would you like to use a base model or a chat model")
while True:
    model_type = input()
    if model_type in ["base", "chat"]:
        break
    print("Please answer with either base or chat")

isChat = model_type == "chat"

models = []

# Get model_num
filenames = os.listdir("artifacts")
for filename in filenames:
    if filename.startswith(f"{model_type}_model_") and filename.endswith(".pt"):
        models.append(f"{filename[11:-3]}")
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

# Get model from checkpoint
checkpoint_path = f"artifacts/{model_type}_model_{model_num}.pt"
checkpoint = torch.load(checkpoint_path, map_location=torch.device(device))
print(f"Validation loss: {checkpoint['val_loss']}")
model = GPT(checkpoint["config"])
state_dict = checkpoint["model"]
model.load_state_dict({key.replace('_orig_mod.', ''): value for key, value in state_dict.items()})
model.eval()
model.to(device)

# Get advanced settings

while True:
    print("Would you like to tinker with the advanced settings[y\\n]?")
    answer = input()
    if answer in ["y", "n"]:
        break

if answer == "y":
    while True:
        print("What would you like the maximum number of tokens to be?")
        answer = input()
        try:
            answer = int(answer)
            if answer < 1024:
                MAX_LENGTH = answer
                break
            print("Answer must be less than 1024.")
        except:
            print("Answer must be an integer.")
    
    while True:
        print("What would you like the temperature to be?")
        answer = input()
        try:
            answer = float(answer)
            if answer >= 0 and answer <= 1:
                TEMPERATURE = answer
                break
            print("Answer must be greater or equal to 0 and less or equal to 1.")
        except:
            print("Answer must be a number.")
    
    while True:
        print("What would you like the p to be for top-p sampling?")
        answer = input()
        try:
            answer = float(answer)
            if answer > 0 and answer <= 1:
                P = answer
                break
            print("Answer must be greater than 0 and less than or equal to 1.")
        except:
            print("Answer must be a number.")
    
    while True:
        print("What would you like the frequency penalty to be?")
        answer = input()
        try:
            answer = float(answer)
            if answer >= 0 and answer <= 1:
                FREQUENCY_PENALTY = answer
                break
            print("Answer must be greater than or equal to 0 and less than or equal to 1.")
        except:
            print("Answer must be a number.")
    

def sample(logits, token_counts):
    # Temperature
    if TEMPERATURE == 0:
        for token, count in token_counts.items():
            logits[0][token] -= FREQUENCY_PENALTY * count
        return torch.argmax(logits, dim=-1).unsqueeze(-1)
    logits = logits / TEMPERATURE
    
    # Apply frequency penalty
    for token, count in token_counts.items():
        logits[0][token] -= FREQUENCY_PENALTY * count
    
    # Top-P sampling
    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
    sorted_indices_to_remove = cumulative_probs > P
    
    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
    sorted_indices_to_remove[..., 0] = 0
    
    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
    logits[indices_to_remove] = float('-inf')
    
    # Sample
    probs = F.softmax(logits, dim=-1)
    return torch.multinomial(probs, 1)

def get_response(text, isChat):
    os.system("clear")
    if isChat:
        printable = text.replace("<|user|>", "\n\nUser: ")
        printable = printable.replace("<|assistant|>", "\n\nAssistant: ")
        sys.stdout.write(printable[2:]) # The first user will have a \n before it
    else:
        sys.stdout.write(text)
    sys.stdout.flush()

    tokens = enc.encode(text)
    tokens = torch.tensor(tokens, dtype=torch.long)
    tokens = tokens.unsqueeze(0)
    xgen = tokens.to(device)
    token_counts = {}

    while xgen.size(1) < MAX_LENGTH:
        with torch.no_grad():
            logits, _ = model(xgen)
            logits = logits[:, -1, :]
            
            xcol = sample(logits, token_counts)
            
            xgen = torch.cat((xgen, xcol), dim=1)

            latest_token = xcol.item()
            token_counts[latest_token] = token_counts.get(latest_token, 0) + 1
            
            decoded_token = enc.decode([latest_token])
            text += decoded_token
            
            if not isChat and decoded_token == "<|endoftext|>":
                break

            if isChat and text.endswith("<|user|>"):
                # get rid of <|user|>
                sys.stdout.write('\b' * 8)
                sys.stdout.write(' ' * 8)
                sys.stdout.write('\b' * 8)
                sys.stdout.flush()
                break
            sys.stdout.write(decoded_token)
            sys.stdout.flush()
    return text

if isChat:
    conv = "<|user|>"
    print("Enter a prompt or type exit: ")
    while True:
        prompt = input()
        if prompt == "exit":
            break
        conv += f"{prompt}<|assistant|>"
        conv = get_response(conv, isChat)
        print("\n\n\nEnter a prompt or type exit: ")
else:
    while True:
        print("Enter a prompt or type exit: ")
        prompt = input()
        if prompt == "exit":
            break
        get_response(prompt, isChat)
        
        while True:
            print("\n\nType \"continue\" to move on")
            answer = input()
            if answer == "continue":
                os.system("clear")
                break