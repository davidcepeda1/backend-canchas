from datetime import date, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator


class ErrorDetail(BaseModel):
    error: str
    mensaje: str


# ── Cancha ──────────────────────────────────────────────────────────────────

class CanchaBase(BaseModel):
    nombre: str
    tipo: str
    precio_por_hora: float
    imagen_url: Optional[str] = ""
    esta_disponible: Optional[bool] = True


class CanchaCreate(CanchaBase):
    @field_validator("precio_por_hora")
    @classmethod
    def precio_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("El precio por hora debe ser mayor a 0")
        return v


class CanchaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    precio_por_hora: Optional[float] = None
    imagen_url: Optional[str] = None
    esta_disponible: Optional[bool] = None


class CanchaResponse(CanchaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ── Reserva ─────────────────────────────────────────────────────────────────

class ReservaBase(BaseModel):
    cancha_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    nombre_cliente: str


class ReservaCreate(ReservaBase):
    pass


class ReservaUpdate(BaseModel):
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    nombre_cliente: Optional[str] = None


class ReservaResponse(ReservaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    total: Optional[float] = None
