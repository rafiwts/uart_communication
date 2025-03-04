import argparse
import asyncio
import logging
import os
from datetime import datetime

import serial
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.models import Base, SensorData
from app.schema import SensorDataSchema

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
                logging.info("Skipping empty response")

            if response.startswith("$"):
                logging.info(f"Device response: {response}")
                parameters = list(map(float, response[1:].split(",")))
                if len(parameters) == 3:
                    sensor_data = SensorDataSchema(
                        pressure=parameters[0],
                        temperature=parameters[1],
                        velocity=parameters[2],
                        # rounded to two digits
                        timestamp=round(datetime.now().timestamp(), 2),
                    )

                    data = SensorData(**sensor_data.model_dump())

                    db.add(data)
                    db.commit()

                    logging.info(
                        f"Saved to database: {data.pressure}, "
                        f"{data.temperature}, "
                        f"{data.velocity}, "
                        f"{data.timestamp}"
                    )
                    # TODO: handle exception if the response has different values
                else:
                    logging.info("Skipping device's response to command...")
                    continue

        except Exception as e:
            logging.error(f"Error: {e}")


@app.get("/start")
async def start_streaming(db: Session = Depends(get_db)):
    global streaming
    if not streaming:
        streaming = True
        ser.write(b"$0\n")
        logging.info("Sent START to device")

        # create a coroutine for serial reading and add to database
        asyncio.create_task(read_serial_data(db))

        return {"message": "Data streaming started"}

    # TODO: Handle it when you start while streaming
    logging.warning("Attempted to start while already streaming.")
    return {"message": "Already streaming"}


@app.get("/stop")
async def stop_streaming():
    global streaming
    if streaming:
        streaming = False
        ser.write(b"$1\n")
        logging.info("Sent STOP to device")

        return {"message": "Data streaming stopped"}

    # TODO: Handle it when you stop while not streaming
    logging.warning("Attempted to stop while not streaming.")
    return {"message": "Data streaming already stopped"}


if __name__ == "__main__":
    import uvicorn

    logging.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
