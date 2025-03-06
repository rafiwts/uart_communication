from pydantic import BaseModel


# Define a Pydantic model for the configuration
class ConfigUpdateRequest(BaseModel):
    frequency: int
    debug_mode: bool
