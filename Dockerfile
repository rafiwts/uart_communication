FROM python:3.13-slim

RUN apt-get update && apt-get install -y socat

RUN apt-get update && apt-get install -y sqlite3

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/logs

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to start the device.py script (can be changed based on your requirements)
CMD ["bash", "-c", "socat PTY,link=/tmp/virtual_uart1,raw,echo=0 PTY,link=/tmp/virtual_uart2,raw,echo=0 & python -m app.device & python -m app.main"]
