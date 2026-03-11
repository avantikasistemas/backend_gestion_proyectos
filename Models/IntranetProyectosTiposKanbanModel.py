from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class IntranetProyectosTiposKanbanModel(BASE):
    __tablename__ = "intranet_proyectos_tipos_kanban"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    orden = Column(Integer, nullable=False)
    estado = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=func.getdate(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "orden": self.orden,
        }
