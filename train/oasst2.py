from datasets import load_dataset
from collections import defaultdict
import numpy as np
from tqdm import tqdm
import re
import os

import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # give acess to parent dir
from tokenizer import get_tokenizer

enc = get_tokenizer()
user = enc._special_tokens["<|user|>"]
assistant = enc._special_tokens["<|assistant|>"]

def tokenize(message):
    if message["role"] == "prompter":
        tokens = [user]
    else:
        tokens = [assistant]
    tokens.extend(enc.encode_ordinary(message["text"]))
    tokens_np = np.array(tokens)
    assert (0 <= tokens_np).all() and (tokens_np < 2**16).all(), "token dictionary too large for uint16"
    tokens_np_uint16 = tokens_np.astype(np.uint16)
    return tokens_np_uint16

def preprocess_open_assistant_data(split):
    dataset = load_dataset("OpenAssistant/oasst2")
    data = dataset[split]
    conversations = defaultdict(list)
    for message in tqdm(data, desc=f"Grouping messages ({split})"):
        if message['lang'] == 'en':
            conversations[message['message_tree_id']].append(message)
    
    processed_data = []
    for conversation in tqdm(list(conversations.values()), desc=f"Processing conversations ({split})"):
        conv = []
        current_label = None
        current_messages = []
        for message in conversation:
            message["text"] = re.sub(re.escape("open assistant"), "finn-GPT", message["text"], flags=re.IGNORECASE)
            if message['role'] != current_label:
                if current_label is not None:
                    conv.append(current_messages)
                current_label = message['role']
                current_messages = [tokenize(message)]
            else:
                current_messages.append(tokenize(message))
        
        if current_label is not None:
            conv.append(current_messages)
        processed_data.append(conv)
    
    return np.array(processed_data, dtype=object)

print("Starting preprocessing...")

# Process train data
train_data = preprocess_open_assistant_data('train')
train_output_file = 'oasst2_train.npy'
np.save(train_output_file, train_data)
print(f"Train data has been saved to {train_output_file}")

# Process validation data
val_data = preprocess_open_assistant_data('validation')
val_output_file = 'oasst2_val.npy'
np.save(val_output_file, val_data)
print(f"Validation data has been saved to {val_output_file}")

# Print statistics for train data
print(f"Total number of conversations in train set: {len(train_data)}")
print(f"Average number of message groups per conversation in train set: {np.mean([len(conv) for conv in train_data]):.2f}")

# Print statistics for validation data
print(f"Total number of conversations in validation set: {len(val_data)}")
print(f"Average number of message groups per conversation in validation set: {np.mean([len(conv) for conv in val_data]):.2f}")