import torch
from torch.nn import functional as F
import re

from tokenizer import get_tokenizer

torch.manual_seed(42)

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
    tokens = enc.encode(text, allowed_special={"<|user|>", "<|assistant|>"})
    tokens = torch.tensor(tokens, dtype=torch.long).unsqueeze(0).to(next(model.parameters()).device) # use same device as model

    user_token = enc._special_tokens["<|user|>"]

    buffer = []
    num_errors = 0
    token_counts = {}

    while tokens.size(1) < max_length:
        with torch.no_grad():
            logits, _ = model(tokens)
            logits = logits[:, -1, :]

        latest_token = sample(logits, token_counts, temp, p, freq_pen)
        tokens = torch.cat((tokens, latest_token), dim=1)
        latest_token = latest_token.item()

        token_counts[latest_token] = token_counts.get(latest_token, 0) + 1
        buffer.append(latest_token)

        if latest_token == user_token:
            break
        
        decoded_codepoint = enc.decode(buffer)
        if "�" in decoded_codepoint:
            num_errors += 1
            if num_errors > 4:
                raise ValueError("Model produced invalid unicode")
        else:
            num_errors = 0
            buffer.clear()
            yield decoded_codepoint
        
    if tokens.size(1) >= max_length:
        yield "... Model can't generate any more. Maybe start a new chart?"