from pydantic import BaseModel


class SensorDataSchema(BaseModel):
    pressure: float
    temperature: float
    velocity: float
    timestamp: float
