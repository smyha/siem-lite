from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from siem_lite.infrastructure.models import Base  # Importa Base desde models.py

DATABASE_URL = "sqlite:///siem_lite.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Creates all tables in the database."""
    Base.metadata.create_all(bind=engine)
