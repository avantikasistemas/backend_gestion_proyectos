from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Config.db import BASE, engine
from Middleware.get_json import JSONMiddleware
from Middleware.auth_middleware import AuthMiddleware
from Router.Proyectos import proyectos_router
from Router.Login import login_router
from Router.Macroprocesos import macroprocesos_router
from Router.EstadosPropuestas import estados_propuestas_router
from Router.Propuestas import propuestas_router
from Router.PreguntasPropuestas import preguntas_propuestas_router
from Router.EstadosProyectos import estados_proyectos_router
from Router.CriteriosProyecto import criterios_router
from Router.TareasProyecto import tareas_router
from Router.EstadosTareas import estados_tareas_router
from pathlib import Path

route = Path.cwd()
app = FastAPI()
app.title = "Avántika Proyectos"
app.version = "0.0.1"

# IMPORTANTE: El orden de los middlewares importa
# AuthMiddleware debe ir primero para validar autenticación antes que JSONMiddleware
app.add_middleware(AuthMiddleware)
app.add_middleware(JSONMiddleware)
app.add_middleware(
    CORSMiddleware,allow_origins=["*"],  # Permitir todos los orígenes; para producción, especifica los orígenes permitidos.
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos; puedes especificar los métodos permitidos.
    allow_headers=["*"],  # Permitir todos los encabezados; puedes especificar los encabezados permitidos.
)
app.include_router(proyectos_router)
app.include_router(login_router)
app.include_router(macroprocesos_router)
app.include_router(estados_propuestas_router)
app.include_router(propuestas_router)
app.include_router(preguntas_propuestas_router)
app.include_router(estados_proyectos_router)
app.include_router(criterios_router)
app.include_router(tareas_router)
app.include_router(estados_tareas_router)

BASE.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8014,
        reload=True
    )
