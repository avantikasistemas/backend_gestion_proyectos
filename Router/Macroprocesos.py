from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.Macroprocesos import Macroprocesos
from Utils.decorator import http_decorator
from Config.db import get_db

macroprocesos_router = APIRouter()

@macroprocesos_router.post('/macroprocesos', tags=["Macroprocesos"], response_model=dict)
@http_decorator
def obtener_macroprocesos(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todos los macroprocesos activos
    """
    response = Macroprocesos(db).obtener_macroprocesos()
    return response
