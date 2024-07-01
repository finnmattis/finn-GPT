# conversation, message, role/texts, text

# human and assistant tokens

import numpy as np
import tiktoken
enc = tiktoken.get_encoding("gpt2")

loaded_data = np.load("oasst2.npy", allow_pickle=True)
print("\nLoaded data shape:", loaded_data.shape)
print("First conversation in loaded data:")
print(loaded_data[0])
print(enc.decode(loaded_data[0][1][1][0]))