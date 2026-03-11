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
            id_kanban = data.get("id_kanban")
            descripcion = data.get("descripcion")
            horas_estimadas = data.get("horas_estimadas")
            horas_reales = data.get("horas_reales")

            if not id_proyecto or not titulo or not responsable:
                raise CustomException("Los campos id_proyecto, titulo y responsable son requeridos")
            if not id_kanban:
                raise CustomException("El campo id_kanban es requerido")

            tarea_data = {
                'id_proyecto': id_proyecto,
                'titulo': titulo,
                'descripcion': descripcion or None,
                'responsable': responsable,
                'horas_estimadas': float(horas_estimadas) if horas_estimadas not in (None, '') else None,
                'horas_reales': float(horas_reales) if horas_reales not in (None, '') else None,
                'id_kanban': int(id_kanban),
                'estado': True,
                'created_at': datetime.now()
            }

            nueva_tarea = self.querys.crear_tarea_proyecto(tarea_data)
            self.db.commit()

            return self.tools.output(200, "Tarea creada exitosamente", nueva_tarea.to_dict())

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

    def mover_columna(self, data: dict):
        """Mueve una tarea a otra columna del kanban"""
        try:
            id_tarea = data.get("id_tarea")
            id_kanban = data.get("id_kanban")

            if not id_tarea:
                raise CustomException("El campo id_tarea es requerido")
            if not id_kanban:
                raise CustomException("El campo id_kanban es requerido")

            tarea = self.querys.mover_columna_tarea(id_tarea, int(id_kanban))
            self.db.commit()
            self.db.refresh(tarea)

            return self.tools.output(200, "Columna actualizada", tarea.to_dict())

        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error al mover columna: {str(e)}")
            raise CustomException("Error al mover la tarea")

    def actualizar_tarea(self, data: dict):
        """Actualiza los datos de una tarea existente"""
        try:
            id_tarea = data.get("id_tarea")
            if not id_tarea:
                raise CustomException("El campo id_tarea es requerido")

            campos = {}
            for key in ('titulo', 'descripcion', 'responsable', 'horas_estimadas', 'horas_reales', 'id_kanban'):
                if key in data:
                    val = data[key]
                    if key in ('horas_estimadas', 'horas_reales'):
                        campos[key] = float(val) if val not in (None, '') else None
                    elif key == 'id_kanban' and val is not None:
                        campos[key] = int(val)
                    else:
                        campos[key] = val

            tarea = self.querys.actualizar_tarea(int(id_tarea), campos)
            self.db.commit()
            self.db.refresh(tarea)

            return self.tools.output(200, "Tarea actualizada exitosamente", tarea.to_dict())

        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar tarea: {str(e)}")
            raise CustomException("Error al actualizar la tarea")

    def listar_kanbans(self):
        """Lista los tipos de columna kanban disponibles"""
        try:
            kanbans = self.querys.listar_tipos_kanban()
            return self.tools.output(200, "Kanbans obtenidos", kanbans)
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al listar kanbans: {str(e)}")
            raise CustomException("Error al listar los kanbans")
