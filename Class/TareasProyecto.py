from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime

class TareasProyecto:
    """
    Clase para gestionar la lógica de negocio de tareas de proyectos.
    """

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(db)

    def crear_tarea(self, data: dict):
        """Crea una nueva tarea para un proyecto"""
        try:
            id_proyecto = data.get("id_proyecto")
            titulo = data.get("titulo")
            responsable = data.get("responsable")
            fecha_vencimiento = data.get("fecha_vencimiento")
            
            if not id_proyecto or not titulo or not responsable:
                raise CustomException("Los campos id_proyecto, titulo y responsable son requeridos")
            
            # Obtener el estado inicial "Pendiente"
            estado_pendiente = self.querys.listar_estados_tareas()
            if not estado_pendiente:
                raise CustomException("No se encontraron estados de tareas configurados")
            
            # Buscar el estado "Pendiente" (debería ser el primero por orden)
            id_estado_inicial = estado_pendiente[0]['id']
            
            tarea_data = {
                'id_proyecto': id_proyecto,
                'titulo': titulo,
                'responsable': responsable,
                'id_estado_tarea': id_estado_inicial,
                'fecha_vencimiento': datetime.fromisoformat(fecha_vencimiento) if fecha_vencimiento else None,
                'estado': True,
                'created_at': datetime.now()
            }
            
            nueva_tarea = self.querys.crear_tarea_proyecto(tarea_data)
            
            # Actualizar progreso del proyecto
            self.querys.actualizar_progreso_proyecto(id_proyecto)
            
            self.db.commit()
            
            resultado = nueva_tarea.to_dict()
            resultado['nombre_estado'] = estado_pendiente[0]['nombre']
            
            return self.tools.output(200, "Tarea creada exitosamente", resultado)
            
        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error al crear tarea: {str(e)}")
            raise CustomException("Error al crear la tarea del proyecto")

    def listar_tareas(self, data: dict):
        """Lista todas las tareas de un proyecto"""
        try:
            id_proyecto = data.get("id_proyecto")
            
            if not id_proyecto:
                raise CustomException("El campo id_proyecto es requerido")
            
            tareas = self.querys.listar_tareas_proyecto(id_proyecto)
            
            return self.tools.output(200, "Tareas obtenidas exitosamente", tareas)
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al listar tareas: {str(e)}")
            raise CustomException("Error al listar las tareas del proyecto")

    def actualizar_estado_tarea(self, data: dict):
        """Actualiza el estado de una tarea"""
        try:
            id_tarea = data.get("id_tarea")
            id_estado_tarea = data.get("id_estado_tarea")
            
            if not id_tarea or not id_estado_tarea:
                raise CustomException("Los campos id_tarea e id_estado_tarea son requeridos")
            
            tarea = self.querys.actualizar_estado_tarea(id_tarea, id_estado_tarea)
            
            # IMPORTANTE: Hacer commit de la tarea ANTES de calcular el progreso
            self.db.commit()
            self.db.refresh(tarea)
            
            # Actualizar progreso del proyecto (ya hace commit internamente)
            proyecto = self.querys.actualizar_progreso_proyecto(tarea.id_proyecto)
            
            # Devolver tanto los datos de la tarea como el progreso actualizado del proyecto
            resultado = tarea.to_dict()
            resultado['progreso_proyecto'] = float(proyecto.progreso)
            
            return self.tools.output(200, "Estado de tarea actualizado exitosamente", resultado)
            
        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar estado de tarea: {str(e)}")
            raise CustomException("Error al actualizar el estado de la tarea")
