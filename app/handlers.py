import logging
from datetime import datetime

from app.models import SensorData


def handle_sensor_parameters(db, response):
    parameters = list(map(float, response[1:].split(",")))
    pressure = parameters[0]
    temperature = parameters[1]
    velocity = parameters[2]
    timestamp = datetime.now().timestamp()

    SensorData.add_record(
        db,
        pressure=pressure,
        temperature=temperature,
        velocity=velocity,
        timestamp=timestamp,
    )


def is_valid_sensor_data(response):
    if not response.startswith("$"):
        return False

    parts = response[1:].split(",")

    if len(parts) != 3:
        return False

    try:
        pressure = float(parts[0])
        temperature = float(parts[1])
        velocity = float(parts[2])
    except ValueError:
        return False

    if not (0 < pressure < 1000 and 0 < temperature < 1000 and 0 < velocity < 1000):
        return False

    return True


def handle_config_response(response):
    if response:
        if response.startswith("$2") and "ok" in response:
            logging.info(f"Received: {response}")
        elif response.startswith("$2") and "invalid" in response:
            logging.error(f"Received: {response}")
        else:
            logging.error(f"Received: {response}")
    else:
        logging.warning("No response received from the device.")
