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
    id_macroproceso_solicitante = Column(Integer, nullable=True)  # FK a intranet_macroprocesos
    macroprocesos_ids = Column(String(200))  # IDs separados por coma "1,3,5"
    id_usuario_creador = Column(Integer, nullable=False)  # FK a intranet_usuarios_proyectos
    nombre_creador = Column(String(100))  # Nombre del usuario que creó
    id_tipo_clasificacion = Column(Integer, nullable=True)  # FK a intranet_tipos_clasificacion
    comentario_clasificacion = Column(Text, nullable=True)  # Comentario al clasificar la propuesta
    id_origen_iniciativa = Column(Integer, nullable=True)  # FK a intranet_propuestas_origen
    id_proyecto = Column(Integer, nullable=True)  # FK a intranet_proyectos - Descomentar después de ejecutar proyectos.sql
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
            # "descripcion": getattr(self, 'descripcion', None),  # Usar getattr por si no existe la columna
            "id_macroproceso_solicitante": self.id_macroproceso_solicitante,
            "macroprocesos_ids": self.macroprocesos_ids,
            "id_usuario_creador": self.id_usuario_creador,
            "nombre_creador": self.nombre_creador,
            "id_tipo_clasificacion": self.id_tipo_clasificacion,
            "comentario_clasificacion": self.comentario_clasificacion,
            "id_origen_iniciativa": self.id_origen_iniciativa,
            "id_proyecto": self.id_proyecto,  # Usar getattr por si no existe la columna
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
