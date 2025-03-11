from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.client_config import args

SQLITE_DATABASE_URL = f"sqlite:///{args.database}"

engine = create_engine(
    SQLITE_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# (bad request - it should work only if there
# are messages to display, js takes data about
# frequency from metadata
# to one place /database folder
# add bauldrate
