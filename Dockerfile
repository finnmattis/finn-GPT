FROM python:3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY base_endpoint.py ./
# COPY chat_endpoint.py ./
COPY model.py ./
COPY artifacts/base_model_70000.pt ./artifacts/base_model_70000.pt
# COPY artifacts/chat_model_02000.pt ./artifacts/chat_model_02000.pt

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "base_endpoint:app"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8080", "chat_endpoint:app"]
