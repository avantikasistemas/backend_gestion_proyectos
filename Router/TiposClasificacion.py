from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.TiposClasificacion import TiposClasificacion
from Utils.decorator import http_decorator
from Config.db import get_db

tipos_clasificacion_router = APIRouter()

@tipos_clasificacion_router.post('/tipos-clasificacion', tags=["TiposClasificacion"], response_model=dict)
@http_decorator
def obtener_tipos_clasificacion(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todos los tipos de clasificación activos ordenados por orden asc
    """
    response = TiposClasificacion(db).obtener_tipos()
    return response
