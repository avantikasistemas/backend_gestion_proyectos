from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from Config.jwt_config import verify_token
from typing import Callable

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware para validar el token JWT en las peticiones.
    Rutas excluidas: /login (endpoints públicos)
    """
    
    # Lista de rutas que NO requieren autenticación
    EXCLUDED_PATHS = ['/login', '/docs', '/openapi.json', '/redoc']
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Verificar si la ruta requiere autenticación
        path = request.url.path
        
        # Si la ruta está excluida, continuar sin validar token
        if any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS):
            response = await call_next(request)
            return response
        
        # Obtener el token del header Authorization
        authorization = request.headers.get('Authorization')
        
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "codigo": 401,
                    "mensaje": "Token no proporcionado",
                    "data": {}
                }
            )
        
        # Verificar formato: "Bearer <token>"
        parts = authorization.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "codigo": 401,
                    "mensaje": "Formato de token inválido",
                    "data": {}
                }
            )
        
        token = parts[1]
        
        try:
            # Verificar y decodificar el token
            payload = verify_token(token)
            
            # Agregar la información del usuario al estado de la request
            # para que esté disponible en los endpoints
            request.state.user = payload
            
        except Exception as e:
            error_message = str(e)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "codigo": 401,
                    "mensaje": error_message,
                    "data": {}
                }
            )
        
        # Continuar con la siguiente parte de la cadena
        response = await call_next(request)
        return response
