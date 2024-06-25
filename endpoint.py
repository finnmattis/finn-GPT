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
checkpoint_path = 'artifacts/model_60000.pt'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
    
    tokens = enc.encode(prompt)
    tokens = torch.tensor(tokens, dtype=torch.long).unsqueeze(0).to(device)

    MAX_LENGTH = 100

    def generate_tokens():
        nonlocal tokens
        start_time = time.time()
        while tokens.size(1) < MAX_LENGTH:
            try:
                # Check if the client has disconnected (5 seconds timeout)
                if time.time() - start_time > 5:
                    yield f"data: [TIMEOUT]\n\n"
                    break

                with torch.no_grad():
                    logits, _ = model(tokens)
                    logits = logits[:, -1, :]
                    probs = F.softmax(logits, dim=-1)
                    topk_probs, topk_indices = torch.topk(probs, 50, dim=-1)
                    ix = torch.multinomial(topk_probs, 1)
                    xcol = torch.gather(topk_indices, -1, ix)
                    tokens = torch.cat((tokens, xcol), dim=1)

                    latest_token = xcol.item()
                    yield f"data: {enc.decode([latest_token])}\n\n"
                    start_time = time.time()  # Reset the timer after each successful token generation
            except Exception as e:
                print(f"Error during token generation: {e}")
                yield f"data: [ERROR]\n\n"
                break

        yield "data: [DONE]\n\n"

    return Response(generate_tokens(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)