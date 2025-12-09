from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.Propuestas import Propuestas
from Utils.decorator import http_decorator
from Config.db import get_db

propuestas_router = APIRouter()

@propuestas_router.post('/propuestas/crear', tags=["Propuestas"], response_model=dict)
@http_decorator
def crear_propuesta(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para crear una nueva propuesta
    """
    data = getattr(request.state, "json_data", {})
    response = Propuestas(db).crear_propuesta(data)
    return response

@propuestas_router.post('/propuestas/listar', tags=["Propuestas"], response_model=dict)
@http_decorator
def listar_propuestas(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todas las propuestas
    Acepta filtros opcionales: id_estado, texto
    """
    data = getattr(request.state, "json_data", {})
    response = Propuestas(db).obtener_propuestas(data)
    return response

@propuestas_router.post('/propuestas/detalle', tags=["Propuestas"], response_model=dict)
@http_decorator
def detalle_propuesta(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener el detalle de una propuesta
    Requiere: id (int)
    """
    data = getattr(request.state, "json_data", {})
    propuesta_id = data.get("id")
    
    if not propuesta_id:
        from Utils.tools import CustomException
        raise CustomException("ID de propuesta requerido")
    
    response = Propuestas(db).obtener_propuesta_detalle(propuesta_id)
    return response

@propuestas_router.post('/propuestas/estadisticas', tags=["Propuestas"], response_model=dict)
@http_decorator
def estadisticas_propuestas(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener estadísticas de propuestas agrupadas por estado
    """
    response = Propuestas(db).obtener_estadisticas()
    return response

@propuestas_router.post('/propuestas/cambiar-estado', tags=["Propuestas"], response_model=dict)
@http_decorator
def cambiar_estado_propuesta(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para cambiar el estado de una propuesta
    Requiere: id_propuesta, codigo_estado, motivo_rechazo (si es rechazada)
    """
    data = getattr(request.state, "json_data", {})
    response = Propuestas(db).cambiar_estado(data)
    return response
