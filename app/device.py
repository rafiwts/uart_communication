import argparse
import logging
import os
import random
import time

import serial

# Configure logs
log_file = "logs/device.log"

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

        if command == "START":
            streaming = True
            logging.info("Started sending data...")
        elif command == "STOP":
            streaming = False
            logging.info("Stopped sending data.")

    if streaming:
        data = [random.randint(0, 1000) for _ in range(3)]
        data_str = f"${data[0]},{data[1]},{data[2]}\n"

        ser.write(data_str.encode())
        logging.info(f"Sent data: {data_str.strip()}")

        # TODO: Frequency options to check
        time.sleep(3)
