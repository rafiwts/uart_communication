import argparse
import logging
import os

START_STREAMING_CMD = "$0"
STOP_STREAMING_CMD = "$1"
UPDATE_CONFIG_CMD = "$2"

logging.basicConfig(
    filename="logs/device.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

parser = argparse.ArgumentParser(description="Embedded Device")
parser.add_argument("--port", type=str, default=os.getenv("PORT", "/tmp/virtual_uart2"))
args = parser.parse_args()
