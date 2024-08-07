import numpy as np
import torch
import random
import os

import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # give acess to parent dir
from tokenizer import get_tokenizer

enc = get_tokenizer()

def load_tokens(filename):
    tokens = np.load(filename)
    tokens = tokens.astype(np.int32)
    return torch.tensor(tokens, dtype=torch.long)

class PreTrainLoader:
    def __init__(self, split, batch_size, block_size, process_rank, num_processes):
        assert split in {'train', 'val'}
        self.batch_size = batch_size
        self.block_size = block_size
        self.process_rank = process_rank
        self.num_processes = num_processes

        # get the shard filenames
        data_root = "train/data/edu_fineweb10B"
        shards = os.listdir(data_root)
        shards = [s for s in shards if split in s]
        shards = sorted(shards)
        shards = [os.path.join(data_root, s) for s in shards]
        self.shards = shards
        assert len(shards) > 0, f"no shards found for split {split}"
        if process_rank == 0:
            print(f"found {len(shards)} shards for split {split}")
        self.reset()

    def reset(self):
        self.current_shard = 0
        self.tokens = load_tokens(self.shards[self.current_shard])
        self.current_position = self.batch_size * self.block_size * self.process_rank

    def next_batch(self):
        B, T = self.batch_size, self.block_size
        buf = self.tokens[self.current_position : self.current_position+B*T+1]
        x = (buf[:-1]).view(B, T)
        y = (buf[1:]).view(B, T)

        # advance the position in the tensor
        self.current_position += B * T * self.num_processes
        # if loading the next batch would be out of bounds, advance to next shard
        if self.current_position + (B * T * self.num_processes + 1) > len(self.tokens):
            self.current_shard = (self.current_shard + 1) % len(self.shards)
            self.tokens = load_tokens(self.shards[self.current_shard])
            self.current_position = B * T * self.process_rank
        return x, y

class FineTuneLoader:
    def __init__(self, split, batch_size, block_size):
        assert split in {'train', 'val'}
        self.split = split
        self.batch_size = batch_size
        self.block_size = block_size
        
        self.convs = np.load(f"train/data/oasst2_{split}.npy", allow_pickle=True)
        
        self.idx = 0
        self.epoch = 0

        np.random.shuffle(self.convs)

    def next_batch(self):
        batch_x = []
        batch_y = []
        
        num_mathqa = round(self.batch_size * 0.5)
        num_oasst = self.batch_size - num_mathqa
        # oast
        for _ in range(num_oasst):
            if self.idx >= len(self.convs):
                self.epoch += 1
                self.idx = 0
                np.random.shuffle(self.convs)
            
            conv = []
            for message_group in self.convs[self.idx]:
                chosen = message_group[random.randint(0, len(message_group) - 1)]
                conv.extend(chosen)
            conv.append(50258) # append final user tok
            conv = np.array(conv)      
      
            x = conv[:-1]
            y = conv[1:]
            
            if len(x) > self.block_size:
                x = x[:self.block_size]
                y = y[:self.block_size]

            if len(x) < self.block_size:
                x = np.pad(x, (0, self.block_size - len(x)), 'constant', constant_values=enc._special_tokens["<|pad|>"])
                y = np.pad(y, (0, self.block_size - len(y)), 'constant', constant_values=enc._special_tokens["<|pad|>"])
            
            batch_x.append(x)
            batch_y.append(y)
            self.idx += 1
        
        x, y = np.array(batch_x, dtype=np.int64), np.array(batch_y, dtype=np.int64)
        x, y = torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long)
        return x, y

    def __len__(self):
        return len(self.convs)

if __name__ == "__main__":
    loader = FineTuneLoader('train', 8, 1024)
    x, y = loader.next_batch()
    print(enc.decode(y[7].tolist()))