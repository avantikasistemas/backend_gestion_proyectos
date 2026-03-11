from Utils.tools import Tools, CustomException
from Models.TiposClasificacionModel import TiposClasificacionModel
from sqlalchemy import select

class TiposClasificacion:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()

    def obtener_tipos(self):
        try:
            stmt = select(TiposClasificacionModel).where(
                TiposClasificacionModel.estado == 1
            ).order_by(TiposClasificacionModel.orden.asc())

            result = self.db.execute(stmt).scalars().all()
            tipos = [t.to_dict() for t in result]

            return self.tools.output(200, "Tipos de clasificación obtenidos correctamente", tipos)

        except Exception as e:
            print(f"Error al obtener tipos de clasificación: {str(e)}")
            raise CustomException("Error al obtener tipos de clasificación")
