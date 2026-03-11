from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.OrigenIniciativa import OrigenIniciativa
from Utils.decorator import http_decorator
from Config.db import get_db

origen_iniciativa_router = APIRouter()

@origen_iniciativa_router.post('/origenes-iniciativa', tags=["OrigenIniciativa"], response_model=dict)
@http_decorator
def obtener_origenes_iniciativa(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para obtener todos los orígenes de iniciativa activos ordenados por orden asc
    """
    response = OrigenIniciativa(db).obtener_origenes()
    return response
