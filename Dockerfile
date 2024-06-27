FROM python:3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY endpoint.py ./
COPY model.py ./
COPY artifacts/model_70000.pt ./artifacts/model_70000.pt

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "endpoint:app"]
