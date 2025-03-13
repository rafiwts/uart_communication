import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.client_config import args
from app.routes import router

app = FastAPI()

app.include_router(router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    logging.info(f"Start server on {args.host}:{args.port}")
    logging.info(f"Device serial port: {args.device}")
    logging.info(f"Database path: {args.database}")
    logging.info(f"Baudrate: {args.baudrate}")
    uvicorn.run(app, host=args.host, port=args.port)
