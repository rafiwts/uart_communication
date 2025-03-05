import argparse
import asyncio
import logging
import os

import serial
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.handlers import (
    handle_config_response,
    handle_sensor_parameters,
    is_valid_sensor_data,
)
from app.models import Base

# start app
app = FastAPI()

# Argument parser for CLI commands and environment variables
parser = argparse.ArgumentParser(description="FastAPI UART Server")
parser.add_argument(
    "--host", type=str, default=os.getenv("HOST", "localhost"), help="Host address"
)
parser.add_argument(
    "--port", type=int, default=int(os.getenv("PORT", 7100)), help="Port number"
)
parser.add_argument(
    "--device", type=str, default=os.getenv("PORT", "/tmp/virtual_uart1")
)
# FIXME: Fix argument parsing
# parser.add_argument("--baudrate", type=int, default=os.getenv("BAUDRATE", 115000))

args = parser.parse_args()

# Configure logs
log_file = "logs/client.log"

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# create database
Base.metadata.create_all(bind=engine)

# create a serial device
ser = serial.Serial(args.device, baudrate=115200, timeout=1)
streaming = False


async def read_serial_data(db: Session):
    global streaming
    while streaming:
        try:
            # run the streaming in background so that other requests are handled
            response = await asyncio.to_thread(ser.readline)
            response = response.decode().strip()

            # if response is empty
            if not response:
                logging.warning("Skipping empty timout response")
                continue

            # if this is validated stream data
            if is_valid_sensor_data(response):
                handle_sensor_parameters(db, response)
                logging.info(f"Received: {response}")
                continue

            # other responses
            if response.startswith(("$0", "$1")):
                logging.info(response)
                continue

            handle_config_response(response)

        except Exception as e:
            logging.error(f"Error: {e}")


@app.get("/start")
async def start_streaming(db: Session = Depends(get_db)):
    global streaming
    if not streaming:
        streaming = True
        ser.write(b"$0\n")
        logging.info("Sent: START")

        # create a coroutine for serial reading and add to database
        asyncio.create_task(read_serial_data(db))

        return {"message": "Data streaming started"}

    # TODO: Handle it when you start while streaming
    return {"message": "Already streaming"}


@app.get("/stop")
async def stop_streaming():
    global streaming
    if streaming:
        streaming = False
        ser.write(b"$1\n")
        logging.info("Sent: STOP")

        return {"message": "Data streaming stopped"}

    # TODO: Handle it when you stop while not streaming
    return {"message": "Data streaming already stopped"}


@app.post("/config")
async def configure_device(
    frequency: int, debug_mode: bool, db: Session = Depends(get_db)
):
    message = f"$2,{frequency},{debug_mode}"
    ser.write(message.encode())
    logging.info(f"Sent: {message.strip()}")

    # wait for response so it is not empty
    await asyncio.sleep(1)

    # handle response if not streaming separately
    if not streaming:
        response = await asyncio.to_thread(ser.readline)
        response = response.decode().strip()

        handle_config_response(response)

    return {"message": "Configuration command sent, and response processed."}


if __name__ == "__main__":
    import uvicorn

    logging.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
