import random

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.database.models import DeviceConfig, SensorData
from app.main import app

SQLITE_DATABASE_URL = "sqlite:///./app/tests/test_db.db"

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def frequency():
    return random.randint(1, 255)


@pytest.fixture()
def config_payload(frequency):
    return {"frequency": frequency, "debug_mode": True}


@pytest.fixture(scope="function")
def device_config(db_session):
    config = DeviceConfig(frequency=100, debug_mode=True)
    db_session.add(config)
    db_session.commit()
    return config


@pytest.fixture(scope="function")
def sensor_data_record(db_session):
    record = SensorData(
        pressure=np.random.uniform(0.0, 1000.0),
        temperature=np.random.uniform(0.0, 1000.0),
        velocity=np.random.uniform(0.0, 1000.0),
        timestamp=random.randint(1600000000, 1700000000),
    )

    db_session.add(record)
    db_session.commit()
    return record


@pytest.fixture(scope="function")
def sensor_data_records(db_session):
    records = [
        SensorData(
            pressure=np.random.uniform(0.0, 1000.0),
            temperature=np.random.uniform(0.0, 1000.0),
            velocity=np.random.uniform(0.0, 1000.0),
            timestamp=random.randint(1600000000, 1700000000),
        )
        for _ in range(10)
    ]
    db_session.add_all(records)
    db_session.commit()

    return records


@pytest.fixture
def get_messages(db_session, sensor_data_records):
    all_messages = db_session.query(SensorData).all()
    latest_message = (
        db_session.query(SensorData).order_by(SensorData.timestamp.desc()).first()
    )

    return all_messages, latest_message
