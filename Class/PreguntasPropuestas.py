from Utils.tools import Tools, CustomException
from Utils.querys import Querys

class PreguntasPropuestas:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(db)

    def obtener_preguntas(self):
        """
        Obtiene todas las preguntas activas para el formulario de propuestas.
        
        Returns:
            Respuesta con lista de preguntas
        """
        try:
            preguntas = self.querys.obtener_preguntas_propuestas()
            preguntas_dict = [p.to_dict() for p in preguntas]
            
            return self.tools.output(200, "Preguntas obtenidas correctamente", preguntas_dict)
            
        except Exception as e:
            print(f"Error al obtener preguntas: {str(e)}")
            raise CustomException("Error al obtener las preguntas")
