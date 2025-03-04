import argparse
import logging
import os
import time

import numpy as np
import serial

# Configure logs
log_file = "../logs/device.log"

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

parser = argparse.ArgumentParser(description="Embedded Device")
parser.add_argument("--port", type=str, default=os.getenv("PORT", "/tmp/virtual_uart2"))
args = parser.parse_args()

ser = serial.Serial(args.port, baudrate=115200, timeout=1)

streaming = False

while True:
    if ser.in_waiting > 0:
        command = ser.readline().decode().strip()
        logging.info(f"Received: {command}")

        if command == "$0":
            streaming = True
            start_response = "$0, 200\n"
            ser.write(start_response.encode())
            logging.info("Started sending data...")
        elif command == "$1":
            stop_response = "$0, 200\n"
            ser.write(stop_response.encode())
            streaming = False
            logging.info("Stopped sending data.")

    if streaming:
        # they have to be floats with one digit after comma
        data = np.float16(np.random.uniform(0.0, 1000.0, size=3))
        data_str = f"${data[0]},{data[1]},{data[2]}\n"

        ser.write(data_str.encode())
        logging.info(f"Sent data: {data_str.strip()}")

        # TODO: Frequency options to check
        time.sleep(1.0 / 256)
