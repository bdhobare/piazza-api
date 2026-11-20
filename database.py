from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_PATH = Path(__file__).resolve().parent / "piazza.db" # TODO, move this to volume
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class _Base:
    # Keep classic Column()/relationship() declarations with plain type hints.
    __allow_unmapped__ = True

Base = declarative_base(cls=_Base)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()