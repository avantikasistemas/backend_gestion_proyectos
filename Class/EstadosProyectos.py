from Utils.tools import Tools, CustomException
from Models.EstadosProyectosModel import EstadosProyectosModel

class EstadosProyectos:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()

    def listar_estados(self):
        """Lista todos los estados de proyectos activos ordenados por orden"""
        try:
            estados = self.db.query(EstadosProyectosModel).filter(
                EstadosProyectosModel.estado == True
            ).order_by(EstadosProyectosModel.orden).all()

            estados_list = []
            for estado in estados:
                estados_list.append({
                    "id": estado.id,
                    "nombre": estado.nombre,
                    "descripcion": estado.descripcion,
                    "orden": estado.orden
                })

            return self.tools.output(200, "Estados de proyectos obtenidos exitosamente", estados_list)

        except Exception as e:
            print(f"Error al listar estados de proyectos: {str(e)}")
            raise CustomException("Error al obtener los estados de proyectos")
