import argparse
import logging
import os

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
    "--database", type=str, default=os.getenv("DATABASE_PATH", "app/database.db")
)
args = parser.parse_args()
