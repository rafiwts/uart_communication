import argparse
import logging
import os

parser = argparse.ArgumentParser(description="FastAPI UART Server")
parser.add_argument(
    "--host", type=str, default=os.getenv("HOST", "localhost"), help="Host address"
)
parser.add_argument(
    "--port", type=int, default=int(os.getenv("PORT", 7100)), help="Port number"
)
parser.add_argument(
    "--device", type=str, default=os.getenv("DEVICE", "/tmp/virtual_uart1")
)

args = parser.parse_args()

logging.basicConfig(
    filename="logs/client.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
