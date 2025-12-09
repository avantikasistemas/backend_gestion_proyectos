from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.PreguntasPropuestas import PreguntasPropuestas
from Utils.decorator import http_decorator
from Config.db import get_db

preguntas_propuestas_router = APIRouter()

@preguntas_propuestas_router.post('/preguntas-propuestas', tags=["Preguntas"], response_model=dict)
@http_decorator
def obtener_preguntas_propuestas(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todas las preguntas del cuestionario de propuestas
    """
    response = PreguntasPropuestas(db).obtener_preguntas()
    return response
