from Utils.tools import Tools, CustomException
from Models.EstadosPropuestasModel import EstadosPropuestasModel
from sqlalchemy import select

class EstadosPropuestas:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()

    def obtener_estados(self):
        """
        Obtiene todos los estados de propuestas activos.
        
        Returns:
            Lista de estados activos ordenados por id
        """
        try:
            # Consultar estados activos
            stmt = select(EstadosPropuestasModel).where(
                EstadosPropuestasModel.estado == 1
            ).order_by(EstadosPropuestasModel.id.asc())
            
            result = self.db.execute(stmt).scalars().all()
            
            # Convertir a diccionario
            estados = [estado.to_dict() for estado in result]
            
            return self.tools.output(200, "Estados obtenidos correctamente", estados)
            
        except Exception as e:
            print(f"Error al obtener estados: {str(e)}")
            raise CustomException("Error al obtener estados de propuestas")
