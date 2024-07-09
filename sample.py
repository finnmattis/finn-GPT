import torch
from torch.nn import functional as F

from tokenizer import get_tokenizer

enc = get_tokenizer()

def sample(logits, token_counts, temp, p, freq_pen):
    # Temperature
    if temp == 0:
        for token, count in token_counts.items():
            logits[0][token] -= freq_pen * count
        return torch.argmax(logits, dim=-1).unsqueeze(-1)
    logits = logits / temp
    
    # Apply frequency penalty
    for token, count in token_counts.items():
        logits[0][token] -= freq_pen * count
    
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

def get_response(model, text, isChat, max_length, temp, p, freq_pen):
    tokens = torch.tensor(enc.encode(text), dtype=torch.long).unsqueeze(0).to(next(model.parameters()).device) # use same device as model

    buffer = []
    num_errors = 0
    token_counts = {}

    user_token_stages = [enc.encode("<"), enc.encode("<|"), enc.encode("<|user"), enc.encode("<|user|")] # since user token is actually multiple, don't print early stages of it

    while tokens.size(1) < max_length:
        with torch.no_grad():
            logits, _ = model(tokens)
            logits = logits[:, -1, :]

        latest_token = sample(logits, token_counts, temp, p, freq_pen)
        tokens = torch.cat((tokens, latest_token), dim=1)
        latest_token = latest_token.item()

        token_counts[latest_token] = token_counts.get(latest_token, 0) + 1
        buffer.append(latest_token)
        
        decoded_token = enc.decode(buffer)
        if "�" in decoded_token:
            num_errors += 1
            if num_errors > 4:
                raise ValueError("Model produced invalid unicode")
        elif buffer not in user_token_stages: # since user token is actually multiple, don't print early stages of it
            num_errors = 0
            text += decoded_token
            buffer.clear()
            yield decoded_token
        
        if not isChat and "<|endoftext|>" in text:
            break
        if isChat and text.endswith("<|user|>"):
            break
    if tokens.size(1) >= max_length:
        yield "... Model can't generate any more. Maybe start a new chart?"