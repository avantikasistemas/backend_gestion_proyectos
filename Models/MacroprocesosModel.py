from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class MacroprocesosModel(BASE):
    """
    Modelo SQLAlchemy para la tabla macroprocesos.
    """
    __tablename__ = "macroprocesos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(10), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    estado = Column(SmallInteger, default=1, nullable=False)  # 1=activo, 0=inactivo
    created_at = Column(DateTime, default=func.getdate(), nullable=False)

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
