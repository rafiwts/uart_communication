import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.client_config import args
from app.db_init import init_db
from app.routes import router

app = FastAPI()

app.include_router(router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

init_db()

if __name__ == "__main__":
    logging.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
