import numpy as np
import tiktoken
import torch
import random

class OasstLoader:
    def __init__(self, split, batch_size=32, block_size=1024):
        assert split in {'train', 'val'}
        self.split = split
        self.batch_size = batch_size
        self.block_size = block_size
        
        self.convs = np.load(f"oasst2_{split}.npy", allow_pickle=True)
        
        self.idx = 0
        self.epoch = 0
        self.shuffle()

    def shuffle(self):
        np.random.shuffle(self.convs)

    def next_batch(self):
        batch_x = []
        batch_y = []
        for _ in range(self.batch_size):
            if self.idx >= len(self.convs):
                self.epoch += 1
                self.idx = 0
                self.shuffle()
            
            conv = []
            for message_group in self.convs[self.idx]:
                chosen = message_group[random.randint(0, len(message_group) - 1)]
                conv.extend(chosen)
            conv = np.array(conv)      
      
            x = conv[:-1]
            y = conv[1:]
            
            if len(x) > self.block_size:
                x = x[:self.block_size]
                y = y[:self.block_size]

            if len(x) < self.block_size:
                x = np.pad(x, (0, self.block_size - len(x)), 'constant', constant_values=10310)
                y = np.pad(y, (0, self.block_size - len(y)), 'constant', constant_values=10310)
            
            batch_x.append(x)
            batch_y.append(y)
            self.idx += 1

        x, y = np.array(batch_x, dtype=np.int64), np.array(batch_y, dtype=np.int64)
        x, y = torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long)
        return x, y

    def __len__(self):
        return len(self.convs)

if __name__ == "__main__":
    loader = OasstLoader('train')
    enc = tiktoken.get_encoding("gpt2")
    import time
    start = time.time()
    while loader.epoch == 0:
        x, y = loader.next_batch()
    print(enc.decode(x[0].tolist()))
    print(time.time() - start)