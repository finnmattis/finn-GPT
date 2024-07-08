import torch
from torch.nn import functional as F
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import os

import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # give acess to parent dir
from model import GPT
from sample import get_response

app = Flask(__name__)
CORS(app)

# Load model once at startup
if os.getenv("isChat") == "0":
    checkpoint_path = 'artifacts/base_model_70000.pt'
else:
    checkpoint_path = 'artifacts/chat_model_02000.pt' # default if no env var
device = torch.device("cpu")

try:
    checkpoint = torch.load(checkpoint_path, map_location=device)
    print(f"Loading finn-GPT step {checkpoint['step']}")
    print(f"Val loss: {checkpoint['val_loss']}")
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
    
    def generate_wrapper():
        try:
            for token in get_response(model, prompt, True, max_tokens, temperature, top_p, frequency_penalty):
                if token == '\n':
                    yield f"data: <newline>\n\n"
                else:
                    yield f"data: {token}\n\n"
        except Exception as e:
            print(f"Error during token generation: {e}")
            yield f"data: [ERROR]\n\n{e}"

        yield "data: [DONE]"

    return Response(generate_wrapper(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)