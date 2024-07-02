from flask import Flask, request, Response, jsonify
import torch
from model import GPT
import tiktoken
from torch.nn import functional as F
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Load model and tokenizer once at startup
enc = tiktoken.get_encoding("gpt2")
checkpoint_path = 'artifacts/base_model_70000.pt'
device = torch.device("cpu")

try:
    checkpoint = torch.load(checkpoint_path, map_location=device)
    print(f"Loading finn-GPT step {checkpoint['step']}")
    print(f"val loss: {checkpoint['val_loss']}")
    model = GPT(checkpoint["config"])
    state_dict = checkpoint["model"]
    model.load_state_dict({key.replace('_orig_mod.', ''): value for key, value in state_dict.items()})
    model.to(device)
    model.eval()
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

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

@app.route('/', methods=['GET', 'OPTIONS'])
def inference():
    if request.method == 'OPTIONS':
        # Preflight request. Reply successfully:
        return app.make_default_options_response()

    if model is None:
        return jsonify({"error": "Model not loaded. Please check server logs."}), 500

    prompt = request.args.get('context', default='', type=str)
    if not prompt:
        return jsonify({"error": "The 'context' parameter is required and cannot be empty."}), 400
    
    # Get optional parameters with default values
    max_tokens = request.args.get('max_tokens', default=100, type=int)
    temperature = request.args.get('temperature', default=0.7, type=float)
    top_p = request.args.get('top_p', default=0.9, type=float)
    frequency_penalty = request.args.get('frequency_penalty', default=0.3, type=float)

    # Validate parameters
    if max_tokens <= 0:
        return jsonify({"error": "max_tokens must be greater than 0"}), 400
    if temperature <= 0:
        return jsonify({"error": "temperature must be greater than 0"}), 400
    if top_p <= 0 or top_p > 1:
        return jsonify({"error": "top_p must be between 0 and 1"}), 400
    if frequency_penalty < 0:
        return jsonify({"error": "frequency_penalty must be non-negative"}), 400
    
    tokens = enc.encode(prompt)
    tokens = torch.tensor(tokens, dtype=torch.long).unsqueeze(0).to(device)

    def generate_tokens():
        nonlocal tokens
        start_time = time.time()
        token_counts = {}
        while tokens.size(1) < len(tokens[0]) + max_tokens:
            try:
                # Check if the client has disconnected (5 seconds timeout)
                if time.time() - start_time > 5:
                    yield f"data: [TIMEOUT]\n\n"
                    break

                with torch.no_grad():
                    logits, _ = model(tokens)
                    logits = logits[:, -1, :]
                    
                    # Apply top-p sampling with temperature and frequency penalty
                    xcol = top_p_sampling(logits, p=top_p, temperature=temperature, 
                                          frequency_penalty=frequency_penalty, token_counts=token_counts)
                    
                    tokens = torch.cat((tokens, xcol), dim=1)

                    latest_token = xcol.item()
                    token_counts[latest_token] = token_counts.get(latest_token, 0) + 1
                    
                    decoded_token = enc.decode([latest_token])
                    
                    # Replace newline characters with a special token
                    if decoded_token == '\n':
                        yield f"data: <newline>\n\n"
                    else:
                        yield f"data: {decoded_token}\n\n"

                    if decoded_token == "<|endoftext|>":
                        break
                    
                    start_time = time.time()  # Reset the timer after each successful token generation
            except Exception as e:
                print(f"Error during token generation: {e}")
                yield f"data: [ERROR]\n\n{e}"
                break

        yield "data: [DONE]"

    return Response(generate_tokens(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)