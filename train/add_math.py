import numpy as np
import os

import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # give acess to parent dir
from tokenizer import get_tokenizer

enc = get_tokenizer()

array1 = np.load(f"oasst2_train.npy", allow_pickle=True)
array2 = np.load(f"math_finetune.npy", allow_pickle=True)

print(enc.decode(array2[50][0][0]))

# concatenated_array = np.concatenate((array1, array2))
# print(concatenated_array.shape)
# np.save('math_oasst2.npy', concatenated_array)