from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from Config.db import BASE
from datetime import datetime

class TareasProyectoModel(BASE):
    __tablename__ = "intranet_tareas_proyecto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_proyecto = Column(Integer, ForeignKey('intranet_proyectos.id'), nullable=False)
    titulo = Column(String(255), nullable=False)
    responsable = Column(String(255), nullable=False)
    id_estado_tarea = Column(Integer, ForeignKey('intranet_estados_tareas.id'), nullable=False)
    fecha_vencimiento = Column(DateTime, nullable=True)
    estado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "id_proyecto": self.id_proyecto,
            "titulo": self.titulo,
            "responsable": self.responsable,
            "id_estado_tarea": self.id_estado_tarea,
            "fecha_vencimiento": self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
