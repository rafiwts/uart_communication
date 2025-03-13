FROM python:3.13-slim

RUN apt-get update && apt-get install -y socat sqlite3

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app

COPY . /app

RUN mkdir -p /app/logs && chmod -R 777 /app/logs

RUN chmod +x /app/start-app.sh
ENTRYPOINT ["/app/start-app.sh"]
