from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.EstadosProyectos import EstadosProyectos
from Utils.decorator import http_decorator
from Config.db import get_db

estados_proyectos_router = APIRouter()

@estados_proyectos_router.post('/estados-proyectos', tags=["Estados Proyectos"], response_model=dict)
@http_decorator
def listar_estados_proyectos(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todos los estados de proyectos
    """
    data = getattr(request.state, "json_data", {})
    response = EstadosProyectos(db).listar_estados()
    return response
