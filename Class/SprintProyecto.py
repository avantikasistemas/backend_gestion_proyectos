from Utils.tools import Tools, CustomException
from Models.SprintProyectoModel import SprintProyectoModel
from sqlalchemy import select

class SprintProyecto:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()

    def obtener_sprints(self):
        try:
            stmt = select(SprintProyectoModel).where(
                SprintProyectoModel.estado == 1
            ).order_by(SprintProyectoModel.id.asc())

            result = self.db.execute(stmt).scalars().all()
            sprints = [s.to_dict() for s in result]

            return self.tools.output(200, "Sprints obtenidos correctamente", sprints)

        except Exception as e:
            print(f"Error al obtener sprints: {str(e)}")
            raise CustomException("Error al obtener los sprints")
