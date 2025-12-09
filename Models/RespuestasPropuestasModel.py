from sqlalchemy import Column, Integer, Text, SmallInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from Config.db import BASE

class RespuestasPropuestasModel(BASE):
    """
    Modelo SQLAlchemy para la tabla intranet_respuestas_propuestas.
    Almacena las respuestas del cuestionario para cada propuesta.
    """
    __tablename__ = "intranet_respuestas_propuestas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_propuesta = Column(Integer, ForeignKey('intranet_propuestas.id'), nullable=False)
    id_pregunta = Column(Integer, ForeignKey('intranet_preguntas_propuestas.id'), nullable=False)
    respuesta = Column(Text)
    estado = Column(SmallInteger, default=1, nullable=False)  # 1=activo, 0=inactivo
    created_at = Column(DateTime, default=func.getdate(), nullable=False)

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "id_propuesta": self.id_propuesta,
            "id_pregunta": self.id_pregunta,
            "respuesta": self.respuesta,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
