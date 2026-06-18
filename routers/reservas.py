from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/reservas", tags=["reservas"])


def _calcular_total(hora_inicio, hora_fin, precio_por_hora: float) -> float:
    inicio_dt = datetime.combine(date.today(), hora_inicio)
    fin_dt = datetime.combine(date.today(), hora_fin)
    horas = (fin_dt - inicio_dt).total_seconds() / 3600
    return round(horas * precio_por_hora, 2)


def _validar_reserva(payload_fecha, payload_hora_inicio, payload_hora_fin, cancha, db: Session, exclude_id: int = None):
    if payload_fecha < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "FECHA_PASADA", "mensaje": "No se puede reservar en una fecha pasada"},
        )

    if payload_hora_fin <= payload_hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "HORARIO_INVALIDO", "mensaje": "La hora de fin debe ser mayor a la hora de inicio"},
        )

    inicio_dt = datetime.combine(date.today(), payload_hora_inicio)
    fin_dt = datetime.combine(date.today(), payload_hora_fin)
    duracion_horas = (fin_dt - inicio_dt).total_seconds() / 3600
    if duracion_horas < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "DURACION_MINIMA", "mensaje": "La reserva debe tener una duración mínima de 1 hora"},
        )

    query = db.query(models.Reserva).filter(
        models.Reserva.cancha_id == cancha.id,
        models.Reserva.fecha == payload_fecha,
        models.Reserva.hora_inicio < payload_hora_fin,
        models.Reserva.hora_fin > payload_hora_inicio,
    )
    if exclude_id is not None:
        query = query.filter(models.Reserva.id != exclude_id)
    colision = query.first()
    if colision:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "HORARIO_OCUPADO", "mensaje": "Este horario ya está ocupado. Intenta con otra hora"},
        )


@router.get("/", response_model=List[schemas.ReservaResponse])
def listar_reservas(cancha_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Reserva)
    if cancha_id is not None:
        query = query.filter(models.Reserva.cancha_id == cancha_id)
    return query.order_by(models.Reserva.fecha, models.Reserva.hora_inicio).all()


@router.get("/{reserva_id}", response_model=schemas.ReservaResponse)
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "RESERVA_NO_ENCONTRADA", "mensaje": f"No existe una reserva con ID {reserva_id}"},
        )
    return reserva


@router.post("/", response_model=schemas.ReservaResponse, status_code=status.HTTP_201_CREATED)
def crear_reserva(payload: schemas.ReservaCreate, db: Session = Depends(get_db)):
    cancha = db.query(models.Cancha).filter(models.Cancha.id == payload.cancha_id).first()
    if not cancha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CANCHA_NO_ENCONTRADA", "mensaje": f"No existe una cancha con ID {payload.cancha_id}"},
        )
    if not cancha.esta_disponible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "CANCHA_NO_DISPONIBLE", "mensaje": "La cancha está en mantenimiento y no puede ser reservada"},
        )

    _validar_reserva(payload.fecha, payload.hora_inicio, payload.hora_fin, cancha, db)

    total = _calcular_total(payload.hora_inicio, payload.hora_fin, cancha.precio_por_hora)
    reserva = models.Reserva(
        cancha_id=payload.cancha_id,
        fecha=payload.fecha,
        hora_inicio=payload.hora_inicio,
        hora_fin=payload.hora_fin,
        nombre_cliente=payload.nombre_cliente,
        total=total,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


@router.put("/{reserva_id}", response_model=schemas.ReservaResponse)
def actualizar_reserva(reserva_id: int, payload: schemas.ReservaUpdate, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "RESERVA_NO_ENCONTRADA", "mensaje": f"No existe una reserva con ID {reserva_id}"},
        )

    update_data = payload.model_dump(exclude_unset=True)
    nueva_fecha = update_data.get("fecha", reserva.fecha)
    nueva_hora_inicio = update_data.get("hora_inicio", reserva.hora_inicio)
    nueva_hora_fin = update_data.get("hora_fin", reserva.hora_fin)

    cancha = db.query(models.Cancha).filter(models.Cancha.id == reserva.cancha_id).first()
    _validar_reserva(nueva_fecha, nueva_hora_inicio, nueva_hora_fin, cancha, db, exclude_id=reserva_id)

    for field, value in update_data.items():
        setattr(reserva, field, value)

    reserva.total = _calcular_total(nueva_hora_inicio, nueva_hora_fin, cancha.precio_por_hora)
    db.commit()
    db.refresh(reserva)
    return reserva


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "RESERVA_NO_ENCONTRADA", "mensaje": f"No existe una reserva con ID {reserva_id}"},
        )
    db.delete(reserva)
    db.commit()
