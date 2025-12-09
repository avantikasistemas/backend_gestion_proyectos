from Utils.tools import Tools, CustomException
from Models.EstadosTareasModel import EstadosTareasModel

class EstadosTareas:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()

    def listar_estados(self):
        """Lista todos los estados de tareas activos ordenados por orden"""
        try:
            estados = self.db.query(EstadosTareasModel).filter(
                EstadosTareasModel.estado == True
            ).order_by(EstadosTareasModel.orden).all()

            estados_list = []
            for estado in estados:
                estados_list.append({
                    "id": estado.id,
                    "nombre": estado.nombre,
                    "descripcion": estado.descripcion,
                    "orden": estado.orden
                })

            return self.tools.output(200, "Estados de tareas obtenidos exitosamente", estados_list)

        except Exception as e:
            print(f"Error al listar estados de tareas: {str(e)}")
            raise CustomException("Error al obtener los estados de tareas")
