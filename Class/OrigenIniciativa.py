from Utils.tools import Tools, CustomException
from Models.OrigenIniciativaModel import OrigenIniciativaModel
from sqlalchemy import select

class OrigenIniciativa:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()

    def obtener_origenes(self):
        try:
            stmt = select(OrigenIniciativaModel).where(
                OrigenIniciativaModel.estado == 1
            ).order_by(OrigenIniciativaModel.orden.asc())

            result = self.db.execute(stmt).scalars().all()
            origenes = [o.to_dict() for o in result]

            return self.tools.output(200, "Orígenes de iniciativa obtenidos correctamente", origenes)

        except Exception as e:
            print(f"Error al obtener orígenes de iniciativa: {str(e)}")
            raise CustomException("Error al obtener orígenes de iniciativa")
