to run train the model without DDP: use "python train.py"
with DDP: "nohup python -m torch.distributed.launch --use-env --standalone --nproc_per_node=8 train.py > output.log 2>&1 & disown"

cd ~/downloads; rsync -avz -e "ssh -i finn.pem" ubuntu@164.152.108.16:finn-GPT/log/model_xxxxx.pt ~/Desktop