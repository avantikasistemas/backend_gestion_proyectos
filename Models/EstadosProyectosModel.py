from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from Config.db import BASE
from datetime import datetime

class EstadosProyectosModel(BASE):
    __tablename__ = 'intranet_estados_proyectos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    orden = Column(Integer, nullable=False, default=0)
    estado = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    fecha_actualizacion = Column(DateTime, nullable=True)
