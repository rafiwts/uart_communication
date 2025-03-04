from sqlalchemy import Column, Float, Integer

from .database import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    pressure = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    velocity = Column(Float, nullable=False)
    timestamp = Column(Float, nullable=False)

    def __str__(self):
        return (
            f"SensorData(id={self.id}, "
            f"pressure={self.pressure}, "
            f"temperature={self.temperature}, "
            f"velocity={self.velocity}, "
            f"timestamp={self.timestamp})"
        )
