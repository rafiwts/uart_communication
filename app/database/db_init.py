from app.database.db import Base, SessionLocal, engine

from .models import DeviceConfig


def init_db():
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        config = db.query(DeviceConfig).first()
        if not config:
            default_config = DeviceConfig(frequency=10, debug_mode=True)
            db.add(default_config)
            db.commit()
