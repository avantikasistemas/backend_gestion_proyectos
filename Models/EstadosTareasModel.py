from sqlalchemy import Column, Integer, String, Boolean
from Config.db import BASE

class EstadosTareasModel(BASE):
    __tablename__ = "intranet_estados_tareas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(255))
    orden = Column(Integer, nullable=False, default=0)
    estado = Column(Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "orden": self.orden,
            "estado": self.estado
        }
