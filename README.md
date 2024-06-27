to run train the model without DDP: use "python train.py"
with DDP: "nohup python -m torch.distributed.launch --use-env --standalone --nproc_per_node=8 train.py > output.log 2>&1 & disown"

cd ~/downloads; rsync -avz -e "ssh -i finn.pem" ubuntu@164.152.108.16:finn-GPT/log/model_xxxxx.pt ~/Desktop

model intellegience:
finn-GPT has advanced math skills:

one plus three equals **\_**.
4

started training ~1:15 a.m.
finish at ~11:13 a.m.

docker build --platform linux/amd64 -t finn-gpt .
docker tag finn-gpt us-central1-docker.pkg.dev/finngpt-427606/models/finn-gpt
docker push us-central1-docker.pkg.dev/finngpt-427606/models/finn-gpt

todo:

final:
clean up code
