import logging
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func

from app.database.models import DeviceConfig, SensorData


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
            logging.info(f"Sensor: {response}")
        elif response.startswith("$2") and "invalid" in response:
            logging.error(f"Sensor: {response}")
            raise HTTPException(status_code=400, detail="Invalid data")
        else:
            raise HTTPException(status_code=400, detail="Invalid data")
    else:
        logging.warning("Client: No response received from the sensor.")


def handle_device_metadata(db):
    device_config = db.query(DeviceConfig).first()

    if not device_config:
        raise HTTPException(status_code=400, detail="No device configuration found")

    latest_data = (
        db.query(
            func.avg(SensorData.pressure).label("avg_pressure"),
            func.avg(SensorData.temperature).label("avg_temperature"),
            func.avg(SensorData.velocity).label("avg_velocity"),
        )
        .order_by(SensorData.timestamp.desc())
        .limit(10)
        .all()
    )

    avg_pressure, avg_temperature, avg_velocity = None, None, None
    latest_record = None

    if latest_data and not all(value is None for value in latest_data[0]):
        avg_pressure, avg_temperature, avg_velocity = latest_data[0]
        latest_record = (
            db.query(SensorData).order_by(SensorData.timestamp.desc()).first()
        )

    return {
        "debug": device_config.debug_mode,
        "curr_config": {
            "frequency": device_config.frequency,
            "debug": device_config.debug_mode,
        },
        "mean_last_10": {
            "pressure": avg_pressure,
            "temperature": avg_temperature,
            "velocity": avg_velocity,
        },
        "latest": {
            "pressure": latest_record.pressure if latest_record else None,
            "temperature": latest_record.temperature if latest_record else None,
            "velocity": latest_record.velocity if latest_record else None,
        },
    }


def handle_latest_messages(limit, db):
    if limit <= 0:
        raise HTTPException(status_code=400, detail="The limit number must be positive")

    latest_messages = (
        db.query(SensorData).order_by(SensorData.timestamp.desc()).limit(limit).all()
    )

    if not latest_messages:
        return {"messages": latest_messages}

    messages_response = [
        {
            "pressure": message.pressure,
            "temperature": message.temperature,
            "velocity": message.velocity,
            "timestamp": message.timestamp,
        }
        for message in latest_messages
    ]

    return {"messages": messages_response}
