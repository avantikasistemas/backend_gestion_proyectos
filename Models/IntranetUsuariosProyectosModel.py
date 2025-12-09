from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from Config.db import BASE

class IntranetUsuariosProyectosModel(BASE):
    """
    Modelo SQLAlchemy para la tabla intranet_usuarios_proyectos.
    Gestiona la información de usuarios con su perfil asociado.
    """
    __tablename__ = "intranet_usuarios_proyectos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False, unique=True)
    clave = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)  # Nombre completo
    id_perfil = Column(Integer)
    estado = Column(SmallInteger, default=1, nullable=False)  # 1=activo, 0=inactivo
    fecha_creacion = Column(DateTime, default=func.getdate(), nullable=False)
    fecha_modificacion = Column(DateTime, default=func.getdate(), onupdate=func.getdate(), nullable=False)
    ultimo_acceso = Column(DateTime)

    def to_dict(self, include_password=False):
        """
        Convierte el objeto a diccionario.
        
        Args:
            include_password (bool): Si True, incluye la contraseña (solo para uso interno)
        """
        data = {
            "id": self.id,
            "email": self.email,
            "nombre": self.nombre,
            "id_perfil": self.id_perfil,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_modificacion": self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
            "ultimo_acceso": self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
        }
        
        if include_password:
            data["clave"] = self.clave
            
        return data
