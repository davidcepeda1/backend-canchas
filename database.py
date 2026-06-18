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
DB_TENANT   = os.environ.get("DB_TENANT", "").strip()

port_env    = os.environ.get("DB_PORT", "6543").strip()
DB_PORT     = int(port_env) if port_env.isdigit() else 6543

def _resolve_ipv4(host: str) -> str:
    """Resuelve el host por IPv4 con fallback seguro a la IP directa de Supabase."""
    # Si el host viene vacío o corrupto por un retraso de Render, usamos la IP directa de Supabase en AWS
    if not host or not isinstance(host, str) or host.strip() == "":
        return "44.216.29.125"
        
    clean_host = host.strip().replace('"', '').replace("'", "")
    
    try:
        results = socket.getaddrinfo(clean_host, None, socket.AF_INET, socket.SOCK_STREAM)
        return results[0][4][0]
    except socket.gaierror:
        # Fallback si el DNS del contenedor aún no está listo en el arranque de Render
        return "44.216.29.125"

def _make_connection():
    ipv4 = _resolve_ipv4(DB_HOST)
    
    # Si por un retraso de Render DB_TENANT viene vacío, usamos tu ID real de respaldo
    tenant = DB_TENANT if DB_TENANT else "gjcckbkihtjczkuutixa"
    
    # Formato oficial universal de Supabase para conexiones por IP
    user_with_tenant = f"{DB_USER}.{tenant}"

    return psycopg2.connect(
        host=ipv4,
        port=DB_PORT,
        user=user_with_tenant,
        password=DB_PASSWORD,
        database=DB_NAME,
        connect_timeout=10,
        sslmode="require"
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
