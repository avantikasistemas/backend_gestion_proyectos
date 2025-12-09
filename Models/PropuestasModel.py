from sqlalchemy import Column, Integer, String, Text, SmallInteger, DateTime
from sqlalchemy.sql import func
from Config.db import BASE

class PropuestasModel(BASE):
    """
    Modelo SQLAlchemy para la tabla intranet_propuestas.
    """
    __tablename__ = "intranet_propuestas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), nullable=False, unique=True)
    titulo = Column(String(200), nullable=False)
    resumen = Column(Text)
    # descripcion = Column(Text)  # Descomentar después de ejecutar alter_propuestas_add_descripcion.sql
    impacto = Column(Integer)  # Cantidad de personas impactadas
    macroprocesos_ids = Column(String(200))  # IDs separados por coma "1,3,5"
    id_estado = Column(Integer, nullable=False)  # FK a intranet_estados_propuestas
    id_usuario_creador = Column(Integer, nullable=False)  # FK a intranet_usuarios_proyectos
    nombre_creador = Column(String(100))  # Nombre del usuario que creó
    motivo_rechazo = Column(Text)  # Motivo de rechazo si el estado es Rechazada
    # id_proyecto = Column(Integer, nullable=True)  # FK a intranet_proyectos - Descomentar después de ejecutar proyectos.sql
    estado = Column(SmallInteger, default=1, nullable=False)  # 1=activo, 0=inactivo
    created_at = Column(DateTime, default=func.getdate(), nullable=False)
    updated_at = Column(DateTime, default=func.getdate(), onupdate=func.getdate(), nullable=False)

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "codigo": self.codigo,
            "titulo": self.titulo,
            "resumen": self.resumen,
            "descripcion": getattr(self, 'descripcion', None),  # Usar getattr por si no existe la columna
            "impacto": self.impacto,
            "macroprocesos_ids": self.macroprocesos_ids,
            "id_estado": self.id_estado,
            "id_usuario_creador": self.id_usuario_creador,
            "nombre_creador": self.nombre_creador,
            "motivo_rechazo": self.motivo_rechazo,
            "id_proyecto": getattr(self, 'id_proyecto', None),  # Usar getattr por si no existe la columna
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
