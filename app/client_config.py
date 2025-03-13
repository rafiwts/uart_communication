import argparse
import logging
import os

parser = argparse.ArgumentParser(description="FastAPI UART Server")
parser.add_argument(
    "--host", type=str, default=os.getenv("HOST", "0.0.0.0"), help="Host address"
)
parser.add_argument(
    "--port", type=int, default=int(os.getenv("PORT", 7100)), help="Port number"
)
parser.add_argument("--baudrate", type=int, default=int(os.getenv("BAUDRATE", 115200)))
parser.add_argument(
    "--database", type=str, default=os.getenv("DATABASE_PATH", "database.db")
)
parser.add_argument("--device", type=str, default=os.getenv("DEVICE", "/dev/ttyUSB0"))


args = parser.parse_args()

logging.basicConfig(
    filename="logs/app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
