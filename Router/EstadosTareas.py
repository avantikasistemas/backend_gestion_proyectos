from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.EstadosTareas import EstadosTareas
from Utils.decorator import http_decorator
from Config.db import get_db

estados_tareas_router = APIRouter()

@estados_tareas_router.post('/estados-tareas', tags=["Estados Tareas"], response_model=dict)
@http_decorator
def listar_estados_tareas(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todos los estados de tareas
    """
    data = getattr(request.state, "json_data", {})
    response = EstadosTareas(db).listar_estados()
    return response
