from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.Proyectos import Proyectos
from Utils.decorator import http_decorator
from Config.db import get_db

proyectos_router = APIRouter()

@proyectos_router.post('/proyectos/propuestas-sin-proyecto', tags=["Proyectos"], response_model=dict)
@http_decorator
def obtener_propuestas_sin_proyecto(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener propuestas aprobadas que no tienen proyecto asignado
    """
    response = Proyectos(db).obtener_propuestas_aprobadas_sin_proyecto()
    return response

@proyectos_router.post('/proyectos/crear', tags=["Proyectos"], response_model=dict)
@http_decorator
def crear_proyecto(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para crear un nuevo proyecto desde una propuesta aprobada
    Requiere: id_propuesta (int)
    Opcional: fecha_inicio, fecha_fin_estimada
    """
    data = getattr(request.state, "json_data", {})
    user_data = getattr(request.state, "user", {})
    response = Proyectos(db).crear_proyecto(data, user_data)
    return response

@proyectos_router.post('/proyectos/listar', tags=["Proyectos"], response_model=dict)
@http_decorator
def listar_proyectos(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todos los proyectos
    Acepta filtros opcionales: id_estado_proyecto, texto
    """
    data = getattr(request.state, "json_data", {})
    response = Proyectos(db).listar_proyectos(data)
    return response

@proyectos_router.post('/proyectos/detalle', tags=["Proyectos"], response_model=dict)
@http_decorator
def detalle_proyecto(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener el detalle de un proyecto
    Requiere: id (int)
    """
    data = getattr(request.state, "json_data", {})
    proyecto_id = data.get("id")
    
    if not proyecto_id:
        from Utils.tools import CustomException
        raise CustomException("ID de proyecto requerido")
    
    response = Proyectos(db).obtener_proyecto_detalle(proyecto_id)
    return response

@proyectos_router.post('/proyectos/actualizar-estado', tags=["Proyectos"], response_model=dict)
@http_decorator
def actualizar_estado_proyecto(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para actualizar el estado de un proyecto
    Requiere: id_proyecto (int), id_estado_proyecto (int)
    """
    data = getattr(request.state, "json_data", {})
    response = Proyectos(db).actualizar_estado_proyecto(data)
    return response


