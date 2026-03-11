from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from Config.db import BASE
from datetime import datetime

class TareasProyectoModel(BASE):
    __tablename__ = "intranet_tareas_proyecto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_proyecto = Column(Integer, ForeignKey('intranet_proyectos.id'), nullable=False)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=False)
    horas_estimadas = Column(Numeric(10, 2), nullable=True)
    horas_reales = Column(Numeric(10, 2), nullable=True)
    id_kanban = Column(Integer, ForeignKey('intranet_proyectos_tipos_kanban.id'), nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "id_proyecto": self.id_proyecto,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "responsable": self.responsable,
            "horas_estimadas": float(self.horas_estimadas) if self.horas_estimadas is not None else None,
            "horas_reales": float(self.horas_reales) if self.horas_reales is not None else None,
            "id_kanban": self.id_kanban,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
