from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from Config.db import BASE
from datetime import datetime

class CriteriosProyectoModel(BASE):
    __tablename__ = "intranet_criterios_proyecto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_proyecto = Column(Integer, ForeignKey('intranet_proyectos.id'), nullable=False)
    descripcion = Column(Text, nullable=False)
    completado = Column(Boolean, default=False, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "id_proyecto": self.id_proyecto,
            "descripcion": self.descripcion,
            "completado": self.completado,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
