from .validator import Validator


class Rules:
    """ Esta clase se encarga de validar los datos de entrada de la API
        y si hay un error, lanza una excepcion """

    val = Validator()

    def __init__(self, path: str, params: dict):
        path_dict = {
            "/login": self.__val_login,
        }
        # Se obtiene la funcion a ejecutar
        func = path_dict.get(path, None)
        if func:
            # Se ejecuta la funcion para obtener las reglas de validacion
            validacion_dict = func(params)

            # Se valida la datas
            self.val.validacion_datos_entrada(validacion_dict)

    def __val_login(self, params):
        validacion_dict = [
            {
                "tipo": "string",
                "campo": "email",
                "valor": params.get("email"),
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "clave",
                "valor": params.get("clave"),
                "obligatorio": True,
            }
        ]
        return validacion_dict

