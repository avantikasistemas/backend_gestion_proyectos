from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, Numeric, ForeignKey
from Config.db import BASE
from datetime import datetime

class ProyectosModel(BASE):
    __tablename__ = 'intranet_proyectos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_propuesta = Column(Integer, ForeignKey('intranet_propuestas.id'), nullable=False)
    id_estado_proyecto = Column(Integer, ForeignKey('intranet_estados_proyectos.id'), nullable=False)
    titulo = Column(String(500), nullable=False)
    descripcion = Column(Text, nullable=True)
    progreso = Column(Numeric(5, 2), nullable=False, default=0.00)
    id_usuario_creador = Column(Integer, ForeignKey('intranet_usuarios_proyectos.id'), nullable=False)
    estado = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    fecha_actualizacion = Column(DateTime, nullable=True)
