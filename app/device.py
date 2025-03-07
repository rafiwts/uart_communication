import logging
import time

import numpy as np
import serial

from app.database import get_db
from app.device_config import (
    START_STREAMING_CMD,
    STOP_STREAMING_CMD,
    UPDATE_CONFIG_CMD,
    args,
)
from app.models import DeviceConfig

ser = serial.Serial(args.port, baudrate=115200, timeout=2)

# global variables
streaming = False
frequency, debug_mode = None, None


def load_config():
    db = next(get_db())
    parameters = DeviceConfig.get_config(db)
    return parameters


frequency, debug_mode = load_config()


# global streaming it will not be moved to handlers.py
def handle_streaming_commands(command: str):
    global streaming

    if command == START_STREAMING_CMD:
        streaming = True
        response = f"{START_STREAMING_CMD},ok\n"
        logging.info("Started sending data...")

    elif command == STOP_STREAMING_CMD:
        streaming = False
        response = f"{STOP_STREAMING_CMD},ok\n"
        logging.info("Stopped sending data.")
    else:
        response = None

    if response:
        ser.write(response.encode())


def handle_update_config(command: str):
    global frequency, debug_mode
    _, freq_str, debug_str = command.split(",")

    new_frequency = int(freq_str)
    new_debug_mode = debug_str == "True"

    if new_frequency <= 0 or new_frequency > 255:
        # bool is handled by fastapi, frequency by device
        response = f"{UPDATE_CONFIG_CMD},{new_frequency},invalid command\n"
    else:
        db = next(get_db())
        DeviceConfig.update_config(
            db, frequency=new_frequency, debug_mode=new_debug_mode
        )

        frequency = new_frequency
        debug_mode = new_debug_mode

        response = f"{UPDATE_CONFIG_CMD},{new_frequency},{new_debug_mode},ok\n"

    ser.write(response.encode())


def stream_sensor_data():
    if streaming:
        data = np.float16(np.random.uniform(0.0, 1000.0, size=3))
        data_str = f"${data[0]},{data[1]},{data[2]}\n"
        ser.write(data_str.encode())
        time.sleep(1.0 / frequency)


def main():
    global streaming

    while True:
        try:
            if ser.in_waiting > 0:
                command = ser.readline().decode().strip()
                logging.info(f"Received: {command}")

                if command == START_STREAMING_CMD or command == STOP_STREAMING_CMD:
                    handle_streaming_commands(command)
                elif command.startswith(UPDATE_CONFIG_CMD):
                    handle_update_config(command)

            stream_sensor_data()

        # when I press exit from terminal
        except KeyboardInterrupt:
            logging.info("Shutting down...")
            break

        except Exception as e:
            logging.error(e)


if __name__ == "__main__":
    load_config()
    main()
