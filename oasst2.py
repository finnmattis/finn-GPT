from datasets import load_dataset
from collections import defaultdict
import json

def preprocess_open_assistant_data():
    dataset = load_dataset("OpenAssistant/oasst1")
    data = dataset['train']
    
    conversations = defaultdict(list)
    for message in data:
        if message['lang'] == 'en':
            conversations[message['message_tree_id']].append(message)

    # for conversation in conversations.values():
    #     conversation.sort(key=lambda x: x['created_date'])

    processed_data = []
    for conversation in conversations.values():
        processed_conversation = []
        current_label = None
        current_messages = []

        for message in conversation:
            if message['role'] != current_label:
                if current_label is not None:
                    processed_conversation.append({
                        'label': current_label,
                        'message': current_messages
                    })
                current_label = message['role']
                current_messages = [message['text']]
            else:
                current_messages.append(message['text'])
        
        # Add the last group of messages
        if current_label is not None:
            processed_conversation.append({
                'label': current_label,
                'message': current_messages
            })

        processed_data.append(processed_conversation)

    return processed_data

preprocessed_data = preprocess_open_assistant_data()

# Save the preprocessed data to a JSON file
output_file = 'preprocessed_open_assistant_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(preprocessed_data, f, ensure_ascii=False, indent=2)

print(f"Preprocessed data has been saved to {output_file}")

# Print some statistics
print(f"Total number of conversations: {len(preprocessed_data)}")
print(f"Average number of message groups per conversation: {sum(len(conv) for conv in preprocessed_data) / len(preprocessed_data):.2f}")

# Optionally, print a sample conversation
print("\nHere's a sample conversation:")
print(json.dumps(preprocessed_data[0], indent=2))