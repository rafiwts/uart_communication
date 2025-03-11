import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database.db import get_db
from app.database.models import DeviceConfig
from app.database.schemas import ConfigUpdateRequest
from app.handlers import (
    handle_config_response,
    handle_device_metadata,
    handle_latest_messages,
)
from app.serial_handler import serial_handler

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/start")
async def start_streaming(db: Session = Depends(get_db)):
    try:
        return await serial_handler.start_streaming(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stop")
async def stop_streaming():
    try:
        return await serial_handler.stop_streaming()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/device")
async def get_device_metadata(db: Session = Depends(get_db)):
    return handle_device_metadata(db)


@router.get("/device-display")
async def display_device_metadata(request: Request, db: Session = Depends(get_db)):
    device_metadata = handle_device_metadata(db)
    return templates.TemplateResponse(
        "device-metadata.html", {"request": request, "data": device_metadata}
    )


@router.get("/messages")
async def get_messages(limit: int, db: Session = Depends(get_db)):
    return handle_latest_messages(limit, db)


@router.get("/messages-display")
async def display_messages(request: Request):
    return templates.TemplateResponse("latest-messages.html", {"request": request})


@router.get("/status")
async def get_status():
    return {"streaming": serial_handler.streaming}


@router.patch("/config", status_code=202)
async def configure_device(config: ConfigUpdateRequest, db: Session = Depends(get_db)):
    message = f"$2,{config.frequency},{config.debug_mode}"
    serial_handler.ser.write(message.encode())
    logging.info(f"Client: {message.strip()}")

    await asyncio.sleep(1)

    if config.frequency > 0 and config.frequency <= 255:
        DeviceConfig.update_config(
            db, frequency=config.frequency, debug_mode=config.debug_mode
        )

    if not serial_handler.streaming:
        response = await asyncio.to_thread(serial_handler.ser.readline)
        response = response.decode().strip()
        handle_config_response(response)

    return config
