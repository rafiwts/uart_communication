import argparse
import asyncio
import logging
import os

import serial
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database import engine, get_db
from app.handlers import (
    handle_config_response,
    handle_device_metadata,
    handle_latest_messages,
    handle_sensor_parameters,
    is_valid_sensor_data,
)
from app.models import Base
from app.schemas import ConfigUpdateRequest

app = FastAPI()

# add templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# parsing arguments from CLI or environment variables
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

args = parser.parse_args()

# configure log file
log_file = "logs/client.log"

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# create database
Base.metadata.create_all(bind=engine)

# create a serial device
ser = serial.Serial(args.device, baudrate=115200, timeout=2)
streaming = False


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Render the 'index.html' template and pass some context data
    return templates.TemplateResponse("index.html", {"request": request})


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
    raise HTTPException(status_code=400, detail="Data streaming already started")


@app.get("/stop")
async def stop_streaming():
    global streaming
    if streaming:
        streaming = False
        ser.write(b"$1\n")
        logging.info("Sent: STOP")

        return {"message": "Data streaming stopped"}

    raise HTTPException(status_code=400, detail="Data streaming already stopped")


@app.get("/device")
async def get_device_metadata(db: Session = Depends(get_db)):
    device_metadata = handle_device_metadata(db)

    return device_metadata


@app.get("/messages")
async def get_messages(limit: int, db: Session = Depends(get_db)):
    latest_messages = handle_latest_messages(limit, db)

    return latest_messages


@app.post("/config")
async def configure_device(config: ConfigUpdateRequest, db: Session = Depends(get_db)):
    frequency = config.frequency
    debug_mode = config.debug_mode

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
