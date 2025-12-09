from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.EstadosPropuestas import EstadosPropuestas
from Utils.decorator import http_decorator
from Config.db import get_db

estados_propuestas_router = APIRouter()

@estados_propuestas_router.post('/estados-propuestas', tags=["Estados"], response_model=dict)
@http_decorator
def obtener_estados_propuestas(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todos los estados de propuestas activos
    """
    response = EstadosPropuestas(db).obtener_estados()
    return response
