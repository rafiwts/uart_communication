from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer
from sqlalchemy.orm import Session

from app.database import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    pressure = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    velocity = Column(Float, nullable=False)
    timestamp = Column(Float, nullable=False)

    @classmethod
    def add_record(
        cls,
        db: Session,
        pressure: float,
        temperature: float,
        velocity: float,
        timestamp: float,
    ):
        sensor_data = cls(
            pressure=pressure,
            temperature=temperature,
            velocity=velocity,
            timestamp=timestamp,
        )

        db.add(sensor_data)
        db.commit()
        db.refresh(sensor_data)

        return sensor_data

    def __str__(self):
        return (
            f"SensorData(id={self.id}, "
            f"pressure={self.pressure}, "
            f"temperature={self.temperature}, "
            f"velocity={self.velocity}, "
            f"timestamp={self.timestamp})"
        )


class DeviceConfig(Base):
    __tablename__ = "device_config"

    DEFAULT_FREQUENCY = 1
    DEBUG_MODE = False

    id = Column(Integer, primary_key=True, index=True)
    frequency = Column(Integer, nullable=False)
    debug_mode = Column(Boolean)
    updated_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def get_config(cls, db: Session):
        config = db.query(cls).first()
        if not config:
            config = cls(frequency=cls.DEFAULT_FREQUENCY, debug_mode=cls.DEBUG_MODE)
            db.add(config)
            db.commit()
            db.refresh(config)

        return config.frequency, config.debug_mode

    @classmethod
    def udpdate_config(cls, db: Session, frequency, debug_mode):
        config = db.query(cls).first()
        if config:
            config.frequency = frequency
            config.debug_mode = debug_mode
            config.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(config)
