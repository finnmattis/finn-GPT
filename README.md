# finn-GPT

finn-GPT is a 124M parameter GPT model that outperforms OpenAI's GPT-2 124M. This README provides information on how to train, build, and deploy the model.

## Training

### Without Distributed Data Parallel (DDP)

To train the model without DDP, use:

```
python train.py
```

### With DDP

To train the model with DDP:

```
python -m torch.distributed.launch --use-env --standalone --nproc_per_node=8 train.py
```

### With DDP and nohup (recommended)

To train the model with DDP and keep it running after closing the terminal:

```
nohup python -m torch.distributed.launch --use-env --standalone --nproc_per_node=8 train.py > output.log 2>&1 & disown
```

## Local Inference

This model is small enough to likely run well on your own computer:

```
python local_inference.py
```

## Backend Docker Build and Deployment (Google Cloud Run)

To build the Docker image:

```
docker build --platform linux/amd64 -t base-finn-gpt .
```

Tag the Docker image:

```
docker tag finn-gpt us-central1-docker.pkg.dev/finngpt-427606/models/base-finn-gpt
```

Push the Docker image to the repository:

```
docker push us-central1-docker.pkg.dev/finngpt-427606/models/base-finn-gpt
```

## Frontend Deployment

To deploy the website:

```
cd website; sudo rm -r dist; npm run build; firebase deploy
```

## Pre-Training Run Information

- Training start time: ~1:15 a.m.
- Training end time: ~11:15 a.m.
- Elapsed time: 10 hours

## Performance

finn-GPT, despite having the same number of parameters (124M) as OpenAI's GPT-2 124M, outperforms it in various language tasks.

Todo:
get pretrain log - more stats - benchmark
responsive website
calculator/datetime use with <calc>, <day>, <time> tokens - another fine-tune (better special tokens this time)

rsync -av -e "ssh -i /Users/finnmattis/.ssh/finn.pem" \
  --progress \
  ubuntu@129.159.46.166:/home/ubuntu/finn-GPT/artifacts/chat_model_01999.pt /Users/finnmattis/Desktop/finn-gpt/artifacts/chat_model_2000.pt