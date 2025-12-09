from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.TareasProyecto import TareasProyecto
from Utils.decorator import http_decorator
from Config.db import get_db

tareas_router = APIRouter()

@tareas_router.post('/tareas/crear', tags=["Tareas Proyecto"], response_model=dict)
@http_decorator
def crear_tarea(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para crear una nueva tarea del proyecto
    Requiere: id_proyecto (int), titulo (str), responsable (str)
    """
    data = getattr(request.state, "json_data", {})
    response = TareasProyecto(db).crear_tarea(data)
    return response

@tareas_router.post('/tareas/listar', tags=["Tareas Proyecto"], response_model=dict)
@http_decorator
def listar_tareas(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para listar todas las tareas de un proyecto
    Requiere: id_proyecto (int)
    """
    data = getattr(request.state, "json_data", {})
    response = TareasProyecto(db).listar_tareas(data)
    return response

@tareas_router.post('/tareas/actualizar-estado', tags=["Tareas Proyecto"], response_model=dict)
@http_decorator
def actualizar_estado_tarea(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para actualizar el estado de una tarea
    Requiere: id_tarea (int), id_estado_tarea (int)
    """
    data = getattr(request.state, "json_data", {})
    response = TareasProyecto(db).actualizar_estado_tarea(data)
    return response
