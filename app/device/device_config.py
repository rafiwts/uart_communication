import argparse
import logging
import os

from app.database.db import get_db
from app.database.models import DeviceConfig

START_STREAMING_CMD = "$0"
STOP_STREAMING_CMD = "$1"
UPDATE_CONFIG_CMD = "$2"

logging.basicConfig(
    filename="logs/app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

parser = argparse.ArgumentParser(description="Embedded Device")
parser.add_argument(
    "--device_port", type=str, default=os.getenv("DEVICE_PORT", "/tmp/virtual_uart2")
)
parser.add_argument(
    "--database", type=str, default=os.getenv("DATABASE_PATH", "database.db")
)
args = parser.parse_args()


def load_config():
    db = next(get_db())
    parameters = DeviceConfig.get_config(db)
    return parameters
