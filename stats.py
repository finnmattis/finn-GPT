import numpy as np
import matplotlib.pyplot as plt

gpt_loss_baseline = 3.2924 # GPT-2 124M baseline

with open("artifacts/log.txt", "r") as file:
    lines = file.readlines()

#get streams
streams = {}
for line in lines:
    step, stream, val = line.strip().split()
    if stream not in streams:
        streams[stream] = {}
    streams[stream][int(step)] = float(val)

streams_xy = {}
for k, v in streams.items():
    xy = sorted(list(v.items()))
    streams_xy[k] = list(zip(*xy))

# create plot
plt.figure(figsize=(16, 6))
plt.subplot(121)
xs, ys = streams_xy["train"]
ys = np.array(ys)
plt.plot(xs, ys, label=f'finn-GPT (124M) train loss')
xs, ys = streams_xy["val"]
plt.plot(xs, ys, label=f'finn-GPT (124M) val loss')
if gpt_loss_baseline is not None:
    plt.axhline(y=gpt_loss_baseline, color='r', linestyle='--', label=f"OpenAI GPT-2 (124M) checkpoint val loss")
plt.xlabel("steps")
plt.ylabel("loss")
plt.yscale('log')
plt.ylim(0.0, 4.0)
plt.legend()
plt.title("Loss")
plt.savefig('loss.png')