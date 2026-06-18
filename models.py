from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship
from database import Base


class Cancha(Base):
    __tablename__ = "canchas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    precio_por_hora = Column(Float, nullable=False)
    imagen_url = Column(String, nullable=True, default="")
    esta_disponible = Column(Boolean, default=True)

    reservas = relationship("Reserva", back_populates="cancha", cascade="all, delete-orphan")


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    cancha_id = Column(Integer, ForeignKey("canchas.id", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    nombre_cliente = Column(String, nullable=False)
    total = Column(Float, nullable=True)

    cancha = relationship("Cancha", back_populates="reservas")
