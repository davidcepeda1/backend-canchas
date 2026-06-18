from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db

router = APIRouter(prefix="/canchas", tags=["canchas"])


def _not_found(cancha_id: int):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "CANCHA_NO_ENCONTRADA", "mensaje": f"No existe una cancha con ID {cancha_id}"},
    )


@router.get("/", response_model=List[schemas.CanchaResponse])
def listar_canchas(db: Session = Depends(get_db)):
    return db.query(models.Cancha).all()


@router.get("/{cancha_id}", response_model=schemas.CanchaResponse)
def obtener_cancha(cancha_id: int, db: Session = Depends(get_db)):
    cancha = db.query(models.Cancha).filter(models.Cancha.id == cancha_id).first()
    if not cancha:
        _not_found(cancha_id)
    return cancha


@router.post("/", response_model=schemas.CanchaResponse, status_code=status.HTTP_201_CREATED)
def crear_cancha(payload: schemas.CanchaCreate, db: Session = Depends(get_db)):
    if payload.precio_por_hora <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "PRECIO_INVALIDO", "mensaje": "El precio por hora debe ser mayor a 0"},
        )
    cancha = models.Cancha(**payload.model_dump())
    db.add(cancha)
    db.commit()
    db.refresh(cancha)
    return cancha


@router.put("/{cancha_id}", response_model=schemas.CanchaResponse)
def actualizar_cancha(cancha_id: int, payload: schemas.CanchaUpdate, db: Session = Depends(get_db)):
    cancha = db.query(models.Cancha).filter(models.Cancha.id == cancha_id).first()
    if not cancha:
        _not_found(cancha_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "precio_por_hora" in update_data and update_data["precio_por_hora"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "PRECIO_INVALIDO", "mensaje": "El precio por hora debe ser mayor a 0"},
        )
    for field, value in update_data.items():
        setattr(cancha, field, value)
    db.commit()
    db.refresh(cancha)
    return cancha


@router.delete("/{cancha_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cancha(cancha_id: int, db: Session = Depends(get_db)):
    cancha = db.query(models.Cancha).filter(models.Cancha.id == cancha_id).first()
    if not cancha:
        _not_found(cancha_id)
    db.delete(cancha)
    db.commit()
