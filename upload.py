import torch
from model import GPT

# autodetect device
device = "cpu"
if torch.cuda.is_available():
    device = "cuda"
print(f"using device: {device}")

# get model from checkpoint
checkpoint_path = 'artifacts/model_60000.pt'
checkpoint = torch.load(checkpoint_path, map_location=torch.device(device))
print(f"Loading finnGPT step {checkpoint['step']}")
print(f"val loss: {checkpoint['val_loss']}")
model = GPT(checkpoint["config"])
state_dict = checkpoint["model"]
model.load_state_dict({key.replace('_orig_mod.', ''): value for key, value in state_dict.items()}) # something to do with placing model in DDP and getting raw model

model.save_pretrained("finn-GPT")

# model.push_to_hub("finn-GPT")

print(model.config)

print("done")