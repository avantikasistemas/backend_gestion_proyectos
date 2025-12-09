from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime

class CriteriosProyecto:
    """
    Clase para gestionar la lógica de negocio de criterios de aceptación de proyectos.
    """

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(db)

    def crear_criterio(self, data: dict):
        """Crea un nuevo criterio de aceptación para un proyecto"""
        try:
            id_proyecto = data.get("id_proyecto")
            descripcion = data.get("descripcion")
            
            if not id_proyecto or not descripcion:
                raise CustomException("Los campos id_proyecto y descripcion son requeridos")
            
            criterio_data = {
                'id_proyecto': id_proyecto,
                'descripcion': descripcion,
                'completado': False,
                'estado': True,
                'created_at': datetime.now()
            }
            
            nuevo_criterio = self.querys.crear_criterio_proyecto(criterio_data)
            self.db.commit()
            
            return self.tools.output(200, "Criterio creado exitosamente", nuevo_criterio.to_dict())
            
        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error al crear criterio: {str(e)}")
            raise CustomException("Error al crear el criterio de aceptación")

    def listar_criterios(self, data: dict):
        """Lista todos los criterios de un proyecto"""
        try:
            id_proyecto = data.get("id_proyecto")
            
            if not id_proyecto:
                raise CustomException("El campo id_proyecto es requerido")
            
            criterios = self.querys.listar_criterios_proyecto(id_proyecto)
            
            return self.tools.output(200, "Criterios obtenidos exitosamente", criterios)
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al listar criterios: {str(e)}")
            raise CustomException("Error al listar los criterios de aceptación")

    def toggle_completado(self, data: dict):
        """Alterna el estado de completado de un criterio"""
        try:
            id_criterio = data.get("id_criterio")
            
            if not id_criterio:
                raise CustomException("El campo id_criterio es requerido")
            
            criterio = self.querys.toggle_criterio_completado(id_criterio)
            self.db.commit()
            
            return self.tools.output(200, "Criterio actualizado exitosamente", criterio.to_dict())
            
        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar criterio: {str(e)}")
            raise CustomException("Error al actualizar el criterio")
