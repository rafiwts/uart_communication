import asyncio
import logging

import serial

from app.client_config import args
from app.handlers import (
    handle_config_response,
    handle_sensor_parameters,
    is_valid_sensor_data,
)


class SerialHandler:
    def __init__(self, device):
        self.ser = serial.Serial(device, baudrate=115200, timeout=2)
        self.streaming = False

    async def read_serial_data(self, db):
        """Reads data from serial in an async loop"""
        while self.streaming:
            try:
                response = await asyncio.to_thread(self.ser.readline)
                response = response.decode().strip()

                if not response:
                    logging.warning("Skipping empty timeout response")
                    continue

                if is_valid_sensor_data(response):
                    handle_sensor_parameters(db, response)
                    logging.info(f"Received: {response}")
                    continue

                if response.startswith(("$0", "$1")):
                    logging.info(response)
                    continue

                handle_config_response(response)

            except Exception as e:
                logging.error(f"Serial Error: {e}")

    async def start_streaming(self, db):
        """Starts data streaming"""
        if not self.streaming:
            self.streaming = True
            self.ser.write(b"$0\n")
            logging.info("Sent: START")
            asyncio.create_task(self.read_serial_data(db))
            return {"message": "Data streaming started"}
        raise Exception("Data streaming already started")

    async def stop_streaming(self):
        """Stops data streaming"""
        if self.streaming:
            self.streaming = False
            self.ser.write(b"$1\n")
            logging.info("Sent: STOP")
            return {"message": "Data streaming stopped"}
        raise Exception("Data streaming already stopped")


serial_handler = SerialHandler(args.device)
