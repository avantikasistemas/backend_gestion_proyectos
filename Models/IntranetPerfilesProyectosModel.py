from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Text
from sqlalchemy.sql import func
from Config.db import BASE

class IntranetPerfilesProyectosModel(BASE):
    """
    Modelo SQLAlchemy para la tabla intranet_perfiles_proyectos.
    Define los diferentes perfiles de usuario: DIRECTOR_INNOVACION, COLABORADOR
    """
    __tablename__ = "intranet_perfiles_proyectos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_perfil = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text, nullable=False)
    codigo_perfil = Column(String(20), nullable=False, unique=True)
    estado = Column(SmallInteger, default=1, nullable=False)  # 1=activo, 0=inactivo
    fecha_creacion = Column(DateTime, default=func.getdate(), nullable=False)
    fecha_modificacion = Column(DateTime, default=func.getdate(), onupdate=func.getdate(), nullable=False)

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "nombre_perfil": self.nombre_perfil,
            "descripcion": self.descripcion,
            "codigo_perfil": self.codigo_perfil,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_modificacion": self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
        }
