from datasets import load_dataset
from collections import defaultdict
import numpy as np
import tiktoken

enc = tiktoken.get_encoding("gpt2")
user = enc.encode('<|user|>')
assistant = enc.encode('<|assistant|>')

def tokenize(message):
    if message["role"] == "prompter":
        tokens = user.copy()
    else:
        tokens = assistant.copy()
    tokens.extend(enc.encode_ordinary(message["text"]))
    tokens_np = np.array(tokens)
    assert (0 <= tokens_np).all() and (tokens_np < 2**16).all(), "token dictionary too large for uint16"
    tokens_np_uint16 = tokens_np.astype(np.uint16)
    return tokens_np_uint16

def preprocess_open_assistant_data():
    dataset = load_dataset("OpenAssistant/oasst1")
    data = dataset['train']
    
    conversations = defaultdict(list)
    for message in data:
        if message['lang'] == 'en':  # Filter for English messages only
            conversations[message['message_tree_id']].append(message)

    processed_data = []
    for conversation in conversations.values():
        processed_conversation = []
        current_label = None
        current_messages = []

        for message in conversation:
            if message['role'] != current_label:
                if current_label is not None:
                    processed_conversation.append([current_label,current_messages])
                current_label = message['role']
                current_messages = [tokenize(message)]
            else:
                current_messages.append(tokenize(message))
        
        # Add the last group of messages
        if current_label is not None:
            processed_conversation.append([current_label,current_messages])

        processed_data.append(processed_conversation)

    # Convert to NumPy array
    np_data = np.array(processed_data, dtype=object)
    
    return np_data

# Run the preprocessing
preprocessed_data = preprocess_open_assistant_data()

# Save the preprocessed data to a NumPy file
output_file = 'oasst2.npy'
np.save(output_file, preprocessed_data)

print(f"Preprocessed data has been saved to {output_file}")

# Print some statistics
print(f"Total number of conversations: {len(preprocessed_data)}")
print(f"Average number of message groups per conversation: {np.mean([len(conv) for conv in preprocessed_data]):.2f}")

# Optionally, print a sample conversation
# print("\nHere's a sample conversation:")
# print(json.dumps(preprocessed_data[0], indent=2))

# To demonstrate how to load and use the data
loaded_data = np.load(output_file, allow_pickle=True)
print("\nLoaded data shape:", loaded_data.shape)
print("First conversation in loaded data:")
# print(json.dumps(loaded_data[0], indent=2))