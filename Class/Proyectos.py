from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime

class Proyectos:
    """
    Clase para gestionar la lógica de negocio de proyectos.
    """

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(db)

    def obtener_propuestas_aprobadas_sin_proyecto(self):
        """Obtiene propuestas aprobadas que no tienen proyecto asignado"""
        try:
            propuestas = self.querys.obtener_propuestas_aprobadas_sin_proyecto()
            return self.tools.output(200, "Propuestas aprobadas sin proyecto obtenidas exitosamente", propuestas)
        except Exception as e:
            print(f"Error al obtener propuestas aprobadas sin proyecto: {str(e)}")
            raise CustomException("Error al obtener las propuestas aprobadas")

    def crear_proyecto(self, data: dict, user_data: dict):
        """Crea un nuevo proyecto a partir de una propuesta aprobada"""
        try:
            id_propuesta = data.get("id_propuesta")
            
            if not id_propuesta:
                raise CustomException("El campo id_propuesta es requerido")
            
            # Verificar que la propuesta existe y está aprobada (usando querys)
            propuesta = self.querys.obtener_propuesta_aprobada_por_id(id_propuesta)
            
            # Obtener el primer estado de proyecto (En planeación)
            estado_inicial = self.querys.obtener_estado_proyecto_inicial()
            
            # Obtener descripción de la propuesta (con fallback)
            descripcion = getattr(propuesta, 'descripcion', None) or propuesta.resumen
            
            # Preparar datos del proyecto
            proyecto_data = {
                'id_propuesta': id_propuesta,
                'id_estado_proyecto': estado_inicial.id,
                'titulo': propuesta.titulo,
                'descripcion': descripcion,
                'progreso': 0.00,
                'id_usuario_creador': user_data.get("id"),
                'estado': True,
                'fecha_creacion': datetime.now()
            }
            
            # Crear el proyecto usando querys
            nuevo_proyecto = self.querys.crear_proyecto(proyecto_data)
            
            # Actualizar la propuesta con el id del proyecto (si la columna existe)
            self.querys.actualizar_propuesta_con_proyecto(id_propuesta, nuevo_proyecto.id)
            
            # Hacer commit de todas las operaciones
            self.db.commit()
            
            resultado = {
                "id": nuevo_proyecto.id,
                "titulo": nuevo_proyecto.titulo,
                "id_propuesta": nuevo_proyecto.id_propuesta,
                "nombre_estado": estado_inicial.nombre,
                "progreso": float(nuevo_proyecto.progreso)
            }
            
            return self.tools.output(200, "Proyecto creado exitosamente", resultado)
            
        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error al crear proyecto: {str(e)}")
            raise CustomException("Error al crear el proyecto")

    def listar_proyectos(self, data: dict):
        """Lista todos los proyectos con filtros opcionales"""
        try:
            # Extraer filtros
            id_estado_proyecto = data.get("id_estado_proyecto")
            texto = data.get("texto")
            
            # Obtener proyectos usando querys
            proyectos = self.querys.listar_proyectos(
                id_estado_proyecto=id_estado_proyecto,
                texto=texto
            )
            
            # Formatear respuesta
            proyectos_list = []
            for proyecto in proyectos:
                proyectos_list.append({
                    "id": proyecto.id,
                    "titulo": proyecto.titulo,
                    "descripcion": proyecto.descripcion,
                    "progreso": float(proyecto.progreso),
                    "id_propuesta": proyecto.id_propuesta,
                    "id_estado_proyecto": proyecto.id_estado_proyecto,
                    "nombre_estado": proyecto.nombre_estado,
                    "nombre_creador": proyecto.nombre_creador,
                    "fecha_creacion": proyecto.fecha_creacion.isoformat()
                })
            
            return self.tools.output(200, "Proyectos obtenidos exitosamente", proyectos_list)
            
        except Exception as e:
            print(f"Error al listar proyectos: {str(e)}")
            raise CustomException("Error al obtener los proyectos")

    def obtener_proyecto_detalle(self, proyecto_id: int):
        """Obtiene el detalle completo de un proyecto"""
        try:
            # Obtener proyecto usando querys
            proyecto = self.querys.obtener_proyecto_detalle(proyecto_id)
            
            # Formatear respuesta
            resultado = {
                "id": proyecto.id,
                "titulo": proyecto.titulo,
                "descripcion": proyecto.descripcion,
                "progreso": float(proyecto.progreso),
                "id_estado_proyecto": proyecto.id_estado_proyecto,
                "nombre_estado": proyecto.nombre_estado,
                "creador": {
                    "nombre": proyecto.nombre_creador,
                    "email": proyecto.email_creador
                },
                "propuesta": {
                    "id": proyecto.id_propuesta,
                    "codigo": proyecto.codigo_propuesta,
                    "titulo": proyecto.titulo_propuesta
                },
                "fecha_creacion": proyecto.fecha_creacion.isoformat(),
                "fecha_actualizacion": proyecto.fecha_actualizacion.isoformat() if proyecto.fecha_actualizacion else None
            }
            
            return self.tools.output(200, "Detalle del proyecto obtenido exitosamente", resultado)
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al obtener detalle del proyecto: {str(e)}")
            raise CustomException("Error al obtener el detalle del proyecto")

    def actualizar_estado_proyecto(self, data: dict):
        """Actualiza el estado de un proyecto"""
        try:
            proyecto_id = data.get("id_proyecto")
            nuevo_estado_id = data.get("id_estado_proyecto")
            
            if not proyecto_id or not nuevo_estado_id:
                raise CustomException("Los campos id_proyecto e id_estado_proyecto son requeridos")
            
            # Actualizar estado usando querys
            proyecto = self.querys.actualizar_estado_proyecto(proyecto_id, nuevo_estado_id)
            
            # Hacer commit
            self.db.commit()
            
            resultado = {
                "id": proyecto.id,
                "id_estado_proyecto": proyecto.id_estado_proyecto,
                "mensaje": "Estado actualizado exitosamente"
            }
            
            return self.tools.output(200, "Estado del proyecto actualizado exitosamente", resultado)
            
        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar estado del proyecto: {str(e)}")
            raise CustomException("Error al actualizar el estado del proyecto")


