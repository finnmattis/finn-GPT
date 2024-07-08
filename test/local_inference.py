import torch
from torch.nn import functional as F
import os

import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # give acess to parent dir
from model import GPT
from sample import get_response

# Params:
MAX_LENGTH = 1024
TEMPERATURE = .7
P = .9
FREQUENCY_PENALTY = .3

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
    models_str += f"{model_type}-finnGPT-{model}"
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

if isChat:
    conv = "<|user|>"
    while True:
        print("Enter a prompt or type exit: ")
        # Get prompt
        prompt = input()
        if prompt == "exit":
            break
        conv += f"{prompt}<|assistant|>"

        # Print conv
        os.system("clear")
        printable = conv.replace("<|user|>", "\n\nUser: ")
        printable = printable.replace("<|assistant|>", "\n\nAssistant: ")
        sys.stdout.write(printable[2:]) # Get rid of \n before first "User:"

        # Print generation
        for token in get_response(model, conv, isChat, MAX_LENGTH, TEMPERATURE, P, FREQUENCY_PENALTY):
            sys.stdout.write(token)
            sys.stdout.flush()
            conv += token

        # Get rid of <|user|> and add newlines
        sys.stdout.write('\b' * 8 + ' ' * 8 + '\b' * 8 + '\n' * 3)
else:
    while True:
        print("Enter a prompt or type exit: ")
        # Get prompt
        prompt = input()
        if prompt == "exit":
            break

        # Print prompt
        os.system("clear")
        sys.stdout.write(prompt)

        # Print generation
        for token in get_response(model, prompt, isChat, MAX_LENGTH, TEMPERATURE, P, FREQUENCY_PENALTY):
            sys.stdout.write(token)
            sys.stdout.flush()
        
        print("\n\n\n")
