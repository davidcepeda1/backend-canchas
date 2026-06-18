import os
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Lectura directa y limpia del entorno de producción o desarrollo local
DB_HOST     = os.environ.get("DB_HOST", "").strip()
DB_USER     = os.environ.get("DB_USER", "").strip()
DB_PASSWORD = os.environ.get("DB_PASSWORD", "").strip()
DB_NAME     = os.environ.get("DB_NAME", "").strip()
DB_PORT     = int(os.environ.get("DB_PORT", 6543))

def _make_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        connect_timeout=10,
        sslmode="require",
    )

engine = create_engine(
    "postgresql+psycopg2://",
    creator=_make_connection,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()