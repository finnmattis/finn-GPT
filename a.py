import torch
from model import GPT, GPTConfig

# autodetect device
device = "cpu"
if torch.cuda.is_available():
    device = "cuda"
print(f"using device: {device}")

# get model from checkpoint
model = GPT(GPTConfig)

model = model.from_pretrained("planto73/finn-gpt")
print(model)