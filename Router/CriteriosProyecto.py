from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.CriteriosProyecto import CriteriosProyecto
from Utils.decorator import http_decorator
from Config.db import get_db

criterios_router = APIRouter()

@criterios_router.post('/criterios/crear', tags=["Criterios Proyecto"], response_model=dict)
@http_decorator
def crear_criterio(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para crear un nuevo criterio de aceptación
    Requiere: id_proyecto (int), descripcion (str)
    """
    data = getattr(request.state, "json_data", {})
    response = CriteriosProyecto(db).crear_criterio(data)
    return response

@criterios_router.post('/criterios/listar', tags=["Criterios Proyecto"], response_model=dict)
@http_decorator
def listar_criterios(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para listar todos los criterios de un proyecto
    Requiere: id_proyecto (int)
    """
    data = getattr(request.state, "json_data", {})
    response = CriteriosProyecto(db).listar_criterios(data)
    return response

@criterios_router.post('/criterios/toggle', tags=["Criterios Proyecto"], response_model=dict)
@http_decorator
def toggle_criterio(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para alternar el estado de completado de un criterio
    Requiere: id_criterio (int)
    """
    data = getattr(request.state, "json_data", {})
    response = CriteriosProyecto(db).toggle_completado(data)
    return response
