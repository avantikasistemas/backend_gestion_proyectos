from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class EstadosPropuestasModel(BASE):
    """
    Modelo SQLAlchemy para la tabla intranet_estados_propuestas.
    """
    __tablename__ = "intranet_estados_propuestas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    codigo = Column(String(20), nullable=False, unique=True)
    estado = Column(SmallInteger, default=1, nullable=False)  # 1=activo, 0=inactivo
    created_at = Column(DateTime, default=func.getdate(), nullable=False)

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "codigo": self.codigo,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
