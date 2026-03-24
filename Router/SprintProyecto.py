from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.SprintProyecto import SprintProyecto
from Utils.decorator import http_decorator
from Config.db import get_db

sprint_router = APIRouter()

@sprint_router.post('/sprints/listar', tags=["Sprint Proyecto"], response_model=dict)
@http_decorator
def listar_sprints(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todos los sprints activos
    """
    response = SprintProyecto(db).obtener_sprints()
    return response
