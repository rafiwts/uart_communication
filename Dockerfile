FROM python:3.13-slim

RUN apt-get update && apt-get install -y socat sqlite3

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app

COPY . /app

RUN mkdir -p /app/logs

CMD bash -c "socat PTY,link=/tmp/virtual_uart1,raw,echo=0 PTY,link=/tmp/virtual_uart2,raw,echo=0 & \
    python -m app.device.device & \
    python -m app.main"
