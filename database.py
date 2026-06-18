import os
import socket
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_HOST     = os.environ.get("DB_HOST", "").strip()
DB_USER     = os.environ.get("DB_USER", "").strip()
DB_PASSWORD = os.environ.get("DB_PASSWORD", "").strip()
DB_NAME     = os.environ.get("DB_NAME", "").strip()
DB_PORT     = int(os.environ.get("DB_PORT", 5432))

def _resolve_ipv4(host: str) -> str:
    """Resuelve el host estrictamente por IPv4, previniendo strings vacíos o nulos."""
    if not host or not isinstance(host, str):
        raise ValueError("El Host de la base de datos no está configurado correctamente en el entorno.")
    
    # Limpiamos posibles espacios o comillas accidentales
    clean_host = host.strip().replace('"', '').replace("'", "")
    
    results = socket.getaddrinfo(clean_host, None, socket.AF_INET, socket.SOCK_STREAM)
    return results[0][4][0]

def _make_connection():
    ipv4 = _resolve_ipv4(DB_HOST)
    return psycopg2.connect(
        host=ipv4,
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
