from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Config.jwt_config import create_access_token

class Login:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)

    # Función para cargar los datos registrados
    def login(self, data: dict):
        """ Api que realiza el login de usuario con perfiles. """
        try:
            # Validar que vengan los campos requeridos
            email = data.get("email", "")
            clave = data.get("clave", "")

            if not email:
                raise CustomException("El campo email es requerido")
            
            if not clave:
                raise CustomException("El campo clave es requerido")

            email = email.strip().lower()  # Convertir email a minúsculas
            clave = clave.strip().upper()  # Convertir contraseña a mayúsculas

            # Validar usuario usando querys.py (ahora incluye perfil)
            user_data = self.querys.validar_login(email, clave)
            
            # Crear token JWT incluyendo información del perfil
            token_data = {
                "id": user_data["id"],
                "email": user_data["email"],
                "nombre": user_data["nombre"],
                "id_perfil": user_data["perfil"]["id"],
                "codigo_perfil": user_data["perfil"]["codigo_perfil"],
                "is_admin": user_data["is_admin"]
            }
            
            access_token = create_access_token(data=token_data)
            
            # Preparar respuesta completa con información del perfil
            response_data = {
                "id": user_data["id"],
                "email": user_data["email"],
                "nombre": user_data["nombre"],
                "perfil": {
                    "id": user_data["perfil"]["id"],
                    "nombre_perfil": user_data["perfil"]["nombre_perfil"],
                    "codigo_perfil": user_data["perfil"]["codigo_perfil"],
                    "descripcion": user_data["perfil"]["descripcion"]
                },
                "is_admin": user_data["is_admin"],
                "token": access_token
            }
            
            # Retornar la información
            return self.tools.output(200, "Login exitoso", response_data)

        except CustomException as e:
            print(f"Error al realizar login: {e}")
            raise CustomException(f"{e}")
        except Exception as e:
            print(f"Error inesperado en login: {str(e)}")
            raise CustomException("Error al procesar la solicitud de login")
