from sqlalchemy import Column, Integer, String, Text, SmallInteger, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class PreguntasPropuestasModel(BASE):
    """
    Modelo SQLAlchemy para la tabla intranet_preguntas_propuestas.
    Almacena las preguntas del cuestionario de propuestas.
    """
    __tablename__ = "intranet_preguntas_propuestas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pregunta = Column(Text, nullable=False)
    descripcion = Column(Text)  # Descripción o ayuda de la pregunta
    orden = Column(Integer, nullable=False, default=0)  # Orden de visualización
    estado = Column(SmallInteger, default=1, nullable=False)  # 1=activo, 0=inactivo
    created_at = Column(DateTime, default=func.getdate(), nullable=False)

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "pregunta": self.pregunta,
            "descripcion": self.descripcion,
            "orden": self.orden,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
