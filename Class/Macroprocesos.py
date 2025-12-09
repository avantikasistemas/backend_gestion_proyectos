from Utils.tools import Tools, CustomException
from Models.MacroprocesosModel import MacroprocesosModel
from sqlalchemy import select

class Macroprocesos:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()

    def obtener_macroprocesos(self):
        """
        Obtiene todos los macroprocesos activos.
        
        Returns:
            Lista de macroprocesos activos ordenados por nombre
        """
        try:
            # Consultar macroprocesos activos
            stmt = select(MacroprocesosModel).where(
                MacroprocesosModel.estado == 1
            ).order_by(MacroprocesosModel.nombre.asc())
            
            result = self.db.execute(stmt).scalars().all()
            
            # Convertir a diccionario
            macroprocesos = [mp.to_dict() for mp in result]
            
            return self.tools.output(200, "Macroprocesos obtenidos correctamente", macroprocesos)
            
        except Exception as e:
            print(f"Error al obtener macroprocesos: {str(e)}")
            raise CustomException("Error al obtener macroprocesos")
