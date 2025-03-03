import argparse
import asyncio
import logging
import os

import serial
from fastapi import FastAPI

# Configure logs
log_file = "logs/client.log"

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

parser = argparse.ArgumentParser(description="FastAPI UART Server")
parser.add_argument("--port", type=str, default=os.getenv("PORT", "/tmp/virtual_uart1"))
# TODO: Fix argument parsing
# parser.add_argument("--baudrate", type=int, default=os.getenv("BAUDRATE", 115000))
args = parser.parse_args()

app = FastAPI()

ser = serial.Serial(args.port, baudrate=115200, timeout=1)

streaming = False


async def read_serial_data():
    global streaming
    while streaming:
        try:
            # run the streaming in background so that other requests are handled
            response = await asyncio.to_thread(ser.readline)
            response = response.decode().strip()
            if response:
                # TODO: add adding to database later
                logging.info(f"Received: {response}")
        except Exception as e:
            logging.error(f"Error: {e}")


@app.post("/start")
async def start_streaming():
    global streaming
    if not streaming:
        streaming = True
        ser.write(b"START\n")
        logging.info("Sent START to device")

        # create a coroutine for serial reading and add to database
        asyncio.create_task(read_serial_data())

        return {"message": "Data streaming started"}

    # TODO: Handle it when you start while streaming
    logging.warning("Attempted to start while already streaming.")
    return {"message": "Already streaming"}


@app.post("/stop")
async def stop_streaming():
    global streaming
    if streaming:
        streaming = False
        ser.write(b"STOP\n")
        logging.info("Sent STOP to device")

        return {"message": "Data streaming stopped"}

    # TODO: Handle it when you stop while not streaming
    logging.warning("Attempted to stop while not streaming.")
    return {"message": "Data streaming already stopped"}


if __name__ == "__main__":
    import uvicorn

    logging.info("Starting FastAPI server...")
    uvicorn.run(app, host="localhost", port=8080)
