FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y sqlite3 && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt 

COPY . .

CMD ["python", "app.py"]