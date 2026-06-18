from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import canchas, reservas

app = FastAPI(
    title="API Canchas Deportivas",
    description="API REST para la gestión de canchas deportivas y reservas",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(canchas.router)
app.include_router(reservas.router)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "API Canchas Deportivas OK", "version": "1.0.0"}
