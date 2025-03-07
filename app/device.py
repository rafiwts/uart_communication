import argparse
import logging
import os
import time

import numpy as np
import serial

from app.database import get_db
from app.models import DeviceConfig

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

ser = serial.Serial(args.port, baudrate=115200, timeout=2)

# global variables
streaming = False
frequency, debug_mode = None, None

db = next(get_db())
frequency, debug_mode = DeviceConfig.get_config(db)

while True:
    if ser.in_waiting > 0:
        command = ser.readline().decode().strip()
        logging.info(f"Received: {command}")

        if command == "$0":
            streaming = True
            start_response = f"{command},ok\n"
            ser.write(start_response.encode())
            logging.info("Started sending data...")
        elif command == "$1":
            stop_response = f"{command},ok\n"
            ser.write(stop_response.encode())
            streaming = False
            logging.info("Stopped sending data.")
        elif command.startswith("$2"):
            _, freq_str, debug_str = command.split(",")

            new_frequency = int(freq_str)
            new_debug_mode = debug_str == "True"

            if new_frequency <= 0 or new_frequency > 255:
                response = f"$2,{new_frequency},invalid command\n"
            else:
                DeviceConfig.udpdate_config(
                    db, frequency=new_frequency, debug_mode=new_debug_mode
                )

                frequency = new_frequency
                debug_mode = new_debug_mode

                response = f"$2,{new_frequency},{new_debug_mode},ok\n"

            ser.write(response.encode())

    if streaming:
        # they have to be floats with one digit after comma
        data = np.float16(np.random.uniform(0.0, 1000.0, size=3))
        data_str = f"${data[0]},{data[1]},{data[2]}\n"

        ser.write(data_str.encode())

        time.sleep(1.0 / frequency)
