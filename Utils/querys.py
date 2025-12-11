from Utils.tools import Tools, CustomException
from sqlalchemy import text, func, select, and_, desc, or_
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime
from collections import defaultdict
from typing import List, Dict, Any
import json

from Models.IntranetUsuariosProyectosModel import IntranetUsuariosProyectosModel
from Models.IntranetPerfilesProyectosModel import IntranetPerfilesProyectosModel
from Models.PropuestasModel import PropuestasModel
from Models.EstadosPropuestasModel import EstadosPropuestasModel
from Models.MacroprocesosModel import MacroprocesosModel
from Models.PreguntasPropuestasModel import PreguntasPropuestasModel
from Models.RespuestasPropuestasModel import RespuestasPropuestasModel
from Models.ProyectosModel import ProyectosModel
from Models.EstadosProyectosModel import EstadosProyectosModel
from Models.CriteriosProyectoModel import CriteriosProyectoModel
from Models.TareasProyectoModel import TareasProyectoModel
from Models.EstadosTareasModel import EstadosTareasModel

class Querys:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.query_params = dict()

    # Función para validar login de usuario con SQLAlchemy ORM
    def validar_login(self, email: str, clave: str):
        """
        Valida las credenciales del usuario en la base de datos usando SQLAlchemy ORM.
        
        Args:
            email (str): Email del usuario
            clave (str): Contraseña (ya en mayúsculas)
            
        Returns:
            dict: Datos del usuario incluyendo perfil si es válido
            
        Raises:
            CustomException: Si las credenciales son incorrectas o el usuario está inactivo
        """
        try:
            # Consultar usuario con perfil usando SQLAlchemy ORM con join
            user = (
                self.db.query(IntranetUsuariosProyectosModel, IntranetPerfilesProyectosModel)
                .join(IntranetPerfilesProyectosModel, IntranetUsuariosProyectosModel.id_perfil == IntranetPerfilesProyectosModel.id)
                .filter(IntranetUsuariosProyectosModel.email == email)
                .filter(IntranetUsuariosProyectosModel.estado == 1)
                .first()
            )
            
            # Validar si existe el usuario
            if not user:
                raise CustomException("Email o contraseña incorrectos")
            
            usuario_obj, perfil_obj = user
            
            # Validar contraseña
            if usuario_obj.clave != clave:
                raise CustomException("Email o contraseña incorrectos")
            
            # Validar si el perfil está activo
            if perfil_obj.estado != 1:
                raise CustomException("Perfil inactivo. Contacte al administrador")
            
            # Actualizar último acceso
            usuario_obj.ultimo_acceso = datetime.now()
            self.db.commit()
            
            # Retornar datos del usuario con perfil
            return {
                "id": usuario_obj.id,
                "email": usuario_obj.email,
                "nombre": usuario_obj.nombre,
                "perfil": {
                    "id": perfil_obj.id,
                    "nombre_perfil": perfil_obj.nombre_perfil,
                    "codigo_perfil": perfil_obj.codigo_perfil,
                    "descripcion": perfil_obj.descripcion
                },
                "is_admin": perfil_obj.codigo_perfil
            }
            
        except CustomException as e:
            raise e
        except Exception as ex:
            print(f"Error en validar_login: {str(ex)}")
            raise CustomException("Error al validar credenciales")

    def crear_propuesta(self, titulo: str, resumen: str, macroprocesos_str: str, 
                       id_estado: int, id_usuario: int, nombre_usuario: str, codigo: str):
        """
        Crea una nueva propuesta en la base de datos.
        
        Args:
            titulo: Título de la propuesta
            resumen: Descripción de la propuesta
            impacto: Cantidad de personas impactadas
            macroprocesos_str: IDs de macroprocesos separados por coma "1,3,5"
            id_estado: ID del estado
            id_usuario: ID del usuario creador
            nombre_usuario: Nombre del usuario creador
            codigo: Código único de la propuesta
            
        Returns:
            PropuestasModel: La propuesta creada
            
        Raises:
            CustomException: Si hay error al crear
        """
        try:
            nueva_propuesta = PropuestasModel(
                codigo=codigo,
                titulo=titulo,
                resumen=resumen,
                macroprocesos_ids=macroprocesos_str,
                id_estado=id_estado,
                id_usuario_creador=id_usuario,
                nombre_creador=nombre_usuario,
                estado=1
            )
            
            self.db.add(nueva_propuesta)
            self.db.commit()
            self.db.refresh(nueva_propuesta)
            
            return nueva_propuesta
            
        except Exception as e:
            self.db.rollback()
            print(f"Error en crear_propuesta: {str(e)}")
            raise CustomException("Error al crear la propuesta en la base de datos")

    def obtener_ultimo_codigo_propuesta(self):
        """
        Obtiene el último código de propuesta generado.
        
        Returns:
            str: El último código o None si no hay propuestas
        """
        try:            
            ultima_propuesta = self.db.query(PropuestasModel).order_by(
                desc(PropuestasModel.id)
            ).first()
            
            return ultima_propuesta.codigo if ultima_propuesta else None
            
        except Exception as e:
            print(f"Error en obtener_ultimo_codigo_propuesta: {str(e)}")
            return None

    def obtener_estado_por_codigo(self, codigo_estado: str):
        """
        Obtiene un estado de propuesta por su código.
        
        Args:
            codigo_estado: Código del estado (ej: 'BORRADOR', 'ENVIADO')
            
        Returns:
            EstadosPropuestasModel: El estado encontrado
            
        Raises:
            CustomException: Si no se encuentra el estado
        """
        try:
            estado = self.db.query(EstadosPropuestasModel).filter(
                EstadosPropuestasModel.codigo == codigo_estado
            ).first()
            
            if not estado:
                raise CustomException(f"Estado {codigo_estado} no encontrado")
            
            return estado
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en obtener_estado_por_codigo: {str(e)}")
            raise CustomException("Error al obtener el estado")

    def listar_propuestas(self, id_estado: int = None, texto: str = None, pagina: int = 1, limite: int = 12):
        """
        Lista todas las propuestas activas con filtros opcionales y paginación.
        
        Args:
            id_estado: Filtro por ID de estado (opcional)
            texto: Filtro por texto en título o resumen (opcional)
            pagina: Número de página (default: 1)
            limite: Cantidad de registros por página (default: 12)
            
        Returns:
            dict: Diccionario con propuestas, total y paginación
        """
        try:            
            # Query base con join
            query = self.db.query(
                PropuestasModel,
                EstadosPropuestasModel
            ).join(
                EstadosPropuestasModel,
                PropuestasModel.id_estado == EstadosPropuestasModel.id
            ).filter(
                PropuestasModel.estado == 1
            )
            
            # Aplicar filtro de estado si existe
            if id_estado:
                query = query.filter(PropuestasModel.id_estado == id_estado)
            
            # Aplicar filtro de texto si existe
            if texto:
                texto_like = f"%{texto}%"
                query = query.filter(
                    or_(
                        PropuestasModel.titulo.like(texto_like),
                        PropuestasModel.resumen.like(texto_like)
                    )
                )
            
            # Ordenar por fecha de creación descendente
            query = query.order_by(desc(PropuestasModel.created_at))
            
            # Obtener total de registros antes de paginar
            total = query.count()
            
            # Calcular offset
            offset = (pagina - 1) * limite
            
            # Aplicar paginación
            propuestas_paginadas = query.offset(offset).limit(limite).all()
            
            # Calcular total de páginas
            total_paginas = (total + limite - 1) // limite  # Redondeo hacia arriba
            
            return {
                'propuestas': propuestas_paginadas,
                'total': total,
                'pagina': pagina,
                'limite': limite,
                'total_paginas': total_paginas
            }
            
        except Exception as e:
            print(f"Error en listar_propuestas: {str(e)}")
            raise CustomException("Error al listar propuestas")

    def obtener_propuesta_por_id(self, propuesta_id: int):
        """
        Obtiene una propuesta específica por su ID con su estado.
        
        Args:
            propuesta_id: ID de la propuesta
            
        Returns:
            tuple: (propuesta, estado) o None si no se encuentra
        """
        try:
            result = self.db.query(
                PropuestasModel,
                EstadosPropuestasModel
            ).join(
                EstadosPropuestasModel,
                PropuestasModel.id_estado == EstadosPropuestasModel.id
            ).filter(
                PropuestasModel.id == propuesta_id,
                PropuestasModel.estado == 1
            ).first()
            
            return result
            
        except Exception as e:
            print(f"Error en obtener_propuesta_por_id: {str(e)}")
            raise CustomException("Error al obtener la propuesta")

    def obtener_macroprocesos_por_ids(self, ids_list: list):
        """
        Obtiene macroprocesos por una lista de IDs.
        
        Args:
            ids_list: Lista de IDs de macroprocesos
            
        Returns:
            list: Lista de objetos MacroprocesosModel
        """
        try:
            if not ids_list:
                return []
            
            macroprocesos = self.db.query(MacroprocesosModel).filter(
                MacroprocesosModel.id.in_(ids_list),
                MacroprocesosModel.estado == 1
            ).all()
            
            return macroprocesos
            
        except Exception as e:
            print(f"Error en obtener_macroprocesos_por_ids: {str(e)}")
            return []

    def obtener_preguntas_propuestas(self):
        """
        Obtiene todas las preguntas activas para propuestas ordenadas por orden.
        
        Returns:
            list: Lista de objetos PreguntasPropuestasModel
        """
        try:
            preguntas = self.db.query(PreguntasPropuestasModel).filter(
                PreguntasPropuestasModel.estado == 1
            ).order_by(PreguntasPropuestasModel.orden.asc()).all()
            
            return preguntas
            
        except Exception as e:
            print(f"Error en obtener_preguntas_propuestas: {str(e)}")
            raise CustomException("Error al obtener las preguntas")

    def guardar_respuestas_propuesta(self, id_propuesta: int, respuestas: list):
        """
        Guarda las respuestas del cuestionario para una propuesta.
        
        Args:
            id_propuesta: ID de la propuesta
            respuestas: Lista de diccionarios con {id_pregunta, respuesta}
            
        Returns:
            int: Cantidad de respuestas guardadas
        """
        try:
            contador = 0
            for resp_data in respuestas:
                id_pregunta = resp_data.get("id_pregunta")
                respuesta_texto = resp_data.get("respuesta", "").strip()
                
                # Solo guardar si hay respuesta
                if respuesta_texto:
                    nueva_respuesta = RespuestasPropuestasModel(
                        id_propuesta=id_propuesta,
                        id_pregunta=id_pregunta,
                        respuesta=respuesta_texto,
                        estado=1
                    )
                    self.db.add(nueva_respuesta)
                    contador += 1
            
            self.db.commit()
            return contador
            
        except Exception as e:
            self.db.rollback()
            print(f"Error en guardar_respuestas_propuesta: {str(e)}")
            raise CustomException("Error al guardar las respuestas")

    def obtener_respuestas_propuesta(self, id_propuesta: int):
        """
        Obtiene las respuestas de una propuesta con sus preguntas.
        
        Args:
            id_propuesta: ID de la propuesta
            
        Returns:
            list: Lista de tuplas (respuesta, pregunta)
        """
        try:
            result = self.db.query(
                RespuestasPropuestasModel,
                PreguntasPropuestasModel
            ).join(
                PreguntasPropuestasModel,
                RespuestasPropuestasModel.id_pregunta == PreguntasPropuestasModel.id
            ).filter(
                RespuestasPropuestasModel.id_propuesta == id_propuesta,
                RespuestasPropuestasModel.estado == 1
            ).order_by(PreguntasPropuestasModel.orden.asc()).all()
            
            return result
            
        except Exception as e:
            print(f"Error en obtener_respuestas_propuesta: {str(e)}")
            return []

    def obtener_estadisticas_propuestas(self):
        """
        Obtiene el conteo de propuestas agrupadas por estado.
        
        Returns:
            list: Lista de diccionarios con {estado_id, estado_nombre, estado_codigo, cantidad}
        """
        try:
            
            result = self.db.query(
                EstadosPropuestasModel.id.label('estado_id'),
                EstadosPropuestasModel.nombre.label('estado_nombre'),
                EstadosPropuestasModel.codigo.label('estado_codigo'),
                func.count(PropuestasModel.id).label('cantidad')
            ).outerjoin(
                PropuestasModel,
                (PropuestasModel.id_estado == EstadosPropuestasModel.id) & 
                (PropuestasModel.estado == 1)
            ).filter(
                EstadosPropuestasModel.estado == 1
            ).group_by(
                EstadosPropuestasModel.id,
                EstadosPropuestasModel.nombre,
                EstadosPropuestasModel.codigo
            ).order_by(
                EstadosPropuestasModel.id.asc()
            ).all()
            
            # Formatear resultado
            estadisticas = []
            for row in result:
                estadisticas.append({
                    'estado_id': row.estado_id,
                    'estado_nombre': row.estado_nombre,
                    'estado_codigo': row.estado_codigo,
                    'cantidad': row.cantidad
                })
            
            return estadisticas
            
        except Exception as e:
            print(f"Error en obtener_estadisticas_propuestas: {str(e)}")
            raise CustomException("Error al obtener estadísticas de propuestas")

    def cambiar_estado_propuesta(self, id_propuesta: int, codigo_estado: str, motivo_rechazo: str = None):
        """
        Cambia el estado de una propuesta.
        
        Args:
            id_propuesta: ID de la propuesta
            codigo_estado: Código del nuevo estado (EN_REVISION, APROBADA, RECHAZADA)
            motivo_rechazo: Motivo del rechazo (obligatorio si estado es RECHAZADA)
            
        Returns:
            PropuestasModel: La propuesta actualizada
        """
        try:
            # Obtener la propuesta
            propuesta = self.db.query(PropuestasModel).filter(
                PropuestasModel.id == id_propuesta,
                PropuestasModel.estado == 1
            ).first()
            
            if not propuesta:
                raise CustomException("Propuesta no encontrada")
            
            # Obtener el estado actual de la propuesta
            estado_actual = self.db.query(EstadosPropuestasModel).filter(
                EstadosPropuestasModel.id == propuesta.id_estado,
                EstadosPropuestasModel.estado == 1
            ).first()
            
            # Validar que no se pueda cambiar el estado si ya está rechazada o aprobada
            if estado_actual and estado_actual.codigo == 'RECHAZADA':
                raise CustomException("No se puede cambiar el estado de una propuesta rechazada")
            
            if estado_actual and estado_actual.codigo == 'APROBADA':
                raise CustomException("No se puede cambiar el estado de una propuesta aprobada")
            
            # Obtener el estado nuevo
            estado = self.db.query(EstadosPropuestasModel).filter(
                EstadosPropuestasModel.codigo == codigo_estado,
                EstadosPropuestasModel.estado == 1
            ).first()
            
            if not estado:
                raise CustomException(f"Estado {codigo_estado} no encontrado")
            
            # Actualizar el estado
            propuesta.id_estado = estado.id
            
            # Si es aprobada, guardar la fecha de aprobación
            if codigo_estado == 'APROBADA':
                propuesta.fecha_aprobacion = datetime.now()
            
            # Si es rechazada, guardar el motivo
            if codigo_estado == 'RECHAZADA':
                if not motivo_rechazo or not motivo_rechazo.strip():
                    raise CustomException("El motivo de rechazo es obligatorio")
                propuesta.motivo_rechazo = motivo_rechazo
            else:
                # Limpiar motivo de rechazo si se cambia a otro estado
                propuesta.motivo_rechazo = None
            
            self.db.commit()
            self.db.refresh(propuesta)
            
            return propuesta
            
        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error en cambiar_estado_propuesta: {str(e)}")
            raise CustomException("Error al cambiar el estado de la propuesta")

    # ==================== MÉTODOS PARA PROYECTOS ====================

    def obtener_propuestas_aprobadas_sin_proyecto(self):
        """
        Obtiene propuestas que están aprobadas y NO tienen proyecto asignado.
        
        Returns:
            list: Lista de propuestas aprobadas sin proyecto
        """
        try:
            # ID del estado "Aprobada" según script SQL (estados_propuestas.sql)
            ID_ESTADO_APROBADA = 4
            
            # Consulta con SQLAlchemy ORM
            propuestas = self.db.query(PropuestasModel).filter(
                PropuestasModel.id_estado == ID_ESTADO_APROBADA,
                PropuestasModel.estado == 1,
                or_(
                    PropuestasModel.id_proyecto.is_(None),
                    PropuestasModel.id_proyecto == 0
                )
            ).order_by(desc(PropuestasModel.created_at)).all()
            
            # Formatear resultado
            resultado = []
            for p in propuestas:
                resultado.append({
                    'id': p.id,
                    'codigo': p.codigo,
                    'titulo': p.titulo,
                    'resumen': p.resumen,
                    'nombre_creador': p.nombre_creador,
                    'created_at': p.created_at.isoformat() if p.created_at else None,
                    'fecha_aprobacion': p.fecha_aprobacion.isoformat() if p.fecha_aprobacion else None
                })
            
            return resultado
            
        except Exception as e:
            print(f"Error en obtener_propuestas_aprobadas_sin_proyecto: {str(e)}")
            return []

    def obtener_propuesta_aprobada_por_id(self, id_propuesta: int):
        """
        Obtiene una propuesta aprobada por su ID.
        
        Args:
            id_propuesta: ID de la propuesta
            
        Returns:
            PropuestasModel: La propuesta si está aprobada y sin proyecto
            
        Raises:
            CustomException: Si la propuesta no existe o ya tiene proyecto
        """
        try:
            propuesta = self.db.query(PropuestasModel).filter(
                PropuestasModel.id == id_propuesta,
                PropuestasModel.estado == 1
            ).first()
            
            if not propuesta:
                raise CustomException("La propuesta no existe o está inactiva")
            
            # Verificar que la propuesta no tenga ya un proyecto asociado
            # (solo si la columna existe en la BD)
            if hasattr(propuesta, 'id_proyecto') and propuesta.id_proyecto:
                raise CustomException("Esta propuesta ya tiene un proyecto asociado")
            
            return propuesta
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en obtener_propuesta_aprobada_por_id: {str(e)}")
            raise CustomException("Error al obtener la propuesta")

    def obtener_estado_proyecto_inicial(self):
        """
        Obtiene el primer estado de proyecto (En planeación).
        
        Returns:
            EstadosProyectosModel: El estado inicial
            
        Raises:
            CustomException: Si no se encuentra el estado
        """
        try:
            estado = self.db.query(EstadosProyectosModel).filter(
                EstadosProyectosModel.estado == True
            ).order_by(EstadosProyectosModel.orden).first()
            
            if not estado:
                raise CustomException("No se encontró un estado inicial para el proyecto")
            
            return estado
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en obtener_estado_proyecto_inicial: {str(e)}")
            raise CustomException("Error al obtener el estado inicial del proyecto")

    def crear_proyecto(self, proyecto_data: dict):
        """
        Crea un nuevo proyecto en la base de datos.
        
        Args:
            proyecto_data: Diccionario con los datos del proyecto
            
        Returns:
            ProyectosModel: El proyecto creado
        """
        try:
            nuevo_proyecto = ProyectosModel(**proyecto_data)
            self.db.add(nuevo_proyecto)
            self.db.flush()  # Para obtener el ID sin hacer commit
            
            return nuevo_proyecto
            
        except Exception as e:
            self.db.rollback()
            print(f"Error en crear_proyecto: {str(e)}")
            raise CustomException("Error al crear el proyecto en la base de datos")

    def actualizar_propuesta_con_proyecto(self, id_propuesta: int, id_proyecto: int):
        """
        Actualiza una propuesta con el ID del proyecto asociado.
        
        Args:
            id_propuesta: ID de la propuesta
            id_proyecto: ID del proyecto
        """
        try:
            # Intentar actualizar usando SQL directo para evitar problemas con el modelo            
            sql = text("""
                UPDATE intranet_propuestas 
                SET id_proyecto = :id_proyecto 
                WHERE id = :id_propuesta
            """)
            
            self.db.execute(sql, {
                'id_proyecto': id_proyecto,
                'id_propuesta': id_propuesta
            })

        except Exception as e:
            print(f"Error en actualizar_propuesta_con_proyecto: {str(e)}")
            # No lanzar excepción para no romper el flujo si la columna no existe

    def listar_proyectos(self, id_estado_proyecto: int = None, texto: str = None):
        """
        Lista todos los proyectos activos con filtros opcionales.
        
        Args:
            id_estado_proyecto: Filtro por ID de estado (opcional)
            texto: Filtro por texto en título (opcional)
            
        Returns:
            list: Lista de proyectos con sus estados y creadores
        """
        try:
            # Query base con joins
            query = self.db.query(
                ProyectosModel.id,
                ProyectosModel.titulo,
                ProyectosModel.descripcion,
                ProyectosModel.progreso,
                ProyectosModel.id_propuesta,
                ProyectosModel.fecha_creacion,
                EstadosProyectosModel.nombre.label('nombre_estado'),
                EstadosProyectosModel.id.label('id_estado_proyecto'),
                IntranetUsuariosProyectosModel.nombre.label('nombre_creador')
            ).join(
                EstadosProyectosModel,
                ProyectosModel.id_estado_proyecto == EstadosProyectosModel.id
            ).join(
                IntranetUsuariosProyectosModel,
                ProyectosModel.id_usuario_creador == IntranetUsuariosProyectosModel.id
            ).filter(
                ProyectosModel.estado == True
            )
            
            # Aplicar filtro de estado si existe
            if id_estado_proyecto:
                query = query.filter(ProyectosModel.id_estado_proyecto == id_estado_proyecto)
            
            # Aplicar filtro de texto si existe
            if texto:
                query = query.filter(ProyectosModel.titulo.contains(texto))
            
            # Ordenar por fecha de creación descendente
            query = query.order_by(desc(ProyectosModel.fecha_creacion))
            
            return query.all()
            
        except Exception as e:
            print(f"Error en listar_proyectos: {str(e)}")
            raise CustomException("Error al listar proyectos")

    def obtener_proyecto_detalle(self, proyecto_id: int):
        """
        Obtiene el detalle completo de un proyecto.
        
        Args:
            proyecto_id: ID del proyecto
            
        Returns:
            Objeto con los datos del proyecto o None
        """
        try:
            proyecto = self.db.query(
                ProyectosModel.id,
                ProyectosModel.titulo,
                ProyectosModel.descripcion,
                ProyectosModel.progreso,
                ProyectosModel.id_propuesta,
                ProyectosModel.fecha_creacion,
                ProyectosModel.fecha_actualizacion,
                EstadosProyectosModel.nombre.label('nombre_estado'),
                EstadosProyectosModel.id.label('id_estado_proyecto'),
                IntranetUsuariosProyectosModel.nombre.label('nombre_creador'),
                IntranetUsuariosProyectosModel.email.label('email_creador'),
                PropuestasModel.codigo.label('codigo_propuesta'),
                PropuestasModel.titulo.label('titulo_propuesta')
            ).join(
                EstadosProyectosModel,
                ProyectosModel.id_estado_proyecto == EstadosProyectosModel.id
            ).join(
                IntranetUsuariosProyectosModel,
                ProyectosModel.id_usuario_creador == IntranetUsuariosProyectosModel.id
            ).join(
                PropuestasModel,
                ProyectosModel.id_propuesta == PropuestasModel.id
            ).filter(
                ProyectosModel.id == proyecto_id,
                ProyectosModel.estado == True
            ).first()
            
            if not proyecto:
                raise CustomException("Proyecto no encontrado")
            
            return proyecto
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en obtener_proyecto_detalle: {str(e)}")
            raise CustomException("Error al obtener el detalle del proyecto")

    # ==================== MÉTODOS PARA ACTUALIZAR ESTADO DE PROYECTO ====================
    
    def actualizar_estado_proyecto(self, proyecto_id: int, nuevo_estado_id: int):
        """Actualiza el estado de un proyecto"""
        try:
            proyecto = self.db.query(ProyectosModel).filter(
                ProyectosModel.id == proyecto_id,
                ProyectosModel.estado == True
            ).first()
            
            if not proyecto:
                raise CustomException("Proyecto no encontrado")
            
            # Verificar que el estado existe
            estado = self.db.query(EstadosProyectosModel).filter(
                EstadosProyectosModel.id == nuevo_estado_id
            ).first()
            
            if not estado:
                raise CustomException("Estado no encontrado")
            
            proyecto.id_estado_proyecto = nuevo_estado_id
            proyecto.fecha_actualizacion = datetime.now()
            
            return proyecto
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en actualizar_estado_proyecto: {str(e)}")
            raise CustomException("Error al actualizar el estado del proyecto")

    # ==================== MÉTODOS PARA CRITERIOS DE ACEPTACIÓN ====================
    
    def crear_criterio_proyecto(self, criterio_data: dict):
        """Crea un nuevo criterio de aceptación para un proyecto"""
        try:
            nuevo_criterio = CriteriosProyectoModel(**criterio_data)
            self.db.add(nuevo_criterio)
            self.db.flush()
            return nuevo_criterio
            
        except Exception as e:
            print(f"Error en crear_criterio_proyecto: {str(e)}")
            raise CustomException("Error al crear el criterio de aceptación")
    
    def listar_criterios_proyecto(self, proyecto_id: int):
        """Lista todos los criterios de aceptación de un proyecto"""
        try:
            criterios = self.db.query(CriteriosProyectoModel).filter(
                CriteriosProyectoModel.id_proyecto == proyecto_id,
                CriteriosProyectoModel.estado == True
            ).order_by(CriteriosProyectoModel.created_at.desc()).all()
            
            return [criterio.to_dict() for criterio in criterios]
            
        except Exception as e:
            print(f"Error en listar_criterios_proyecto: {str(e)}")
            raise CustomException("Error al listar los criterios de aceptación")
    
    def toggle_criterio_completado(self, criterio_id: int):
        """Alterna el estado de completado de un criterio"""
        try:
            criterio = self.db.query(CriteriosProyectoModel).filter(
                CriteriosProyectoModel.id == criterio_id,
                CriteriosProyectoModel.estado == True
            ).first()
            
            if not criterio:
                raise CustomException("Criterio no encontrado")
            
            criterio.completado = not criterio.completado
            criterio.updated_at = datetime.now()
            
            return criterio
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en toggle_criterio_completado: {str(e)}")
            raise CustomException("Error al actualizar el criterio")

    # ==================== MÉTODOS PARA ESTADOS DE TAREAS ====================
    
    def listar_estados_tareas(self):
        """Lista todos los estados de tareas activos"""
        try:
            estados = self.db.query(EstadosTareasModel).filter(
                EstadosTareasModel.estado == True
            ).order_by(EstadosTareasModel.orden).all()
            
            return [estado.to_dict() for estado in estados]
            
        except Exception as e:
            print(f"Error en listar_estados_tareas: {str(e)}")
            raise CustomException("Error al listar los estados de tareas")

    # ==================== MÉTODOS PARA TAREAS DE PROYECTO ====================
    
    def crear_tarea_proyecto(self, tarea_data: dict):
        """Crea una nueva tarea para un proyecto"""
        try:
            nueva_tarea = TareasProyectoModel(**tarea_data)
            self.db.add(nueva_tarea)
            self.db.flush()
            return nueva_tarea
            
        except Exception as e:
            print(f"Error en crear_tarea_proyecto: {str(e)}")
            raise CustomException("Error al crear la tarea del proyecto")
    
    def listar_tareas_proyecto(self, proyecto_id: int):
        """Lista todas las tareas de un proyecto con sus estados"""
        try:
            tareas = self.db.query(
                TareasProyectoModel,
                EstadosTareasModel.nombre.label('nombre_estado')
            ).join(
                EstadosTareasModel,
                TareasProyectoModel.id_estado_tarea == EstadosTareasModel.id
            ).filter(
                TareasProyectoModel.id_proyecto == proyecto_id,
                TareasProyectoModel.estado == True
            ).order_by(TareasProyectoModel.created_at.desc()).all()
            
            resultado = []
            for tarea, nombre_estado in tareas:
                tarea_dict = tarea.to_dict()
                tarea_dict['nombre_estado'] = nombre_estado
                resultado.append(tarea_dict)
            
            return resultado
            
        except Exception as e:
            print(f"Error en listar_tareas_proyecto: {str(e)}")
            raise CustomException("Error al listar las tareas del proyecto")
    
    def actualizar_estado_tarea(self, tarea_id: int, nuevo_estado_id: int):
        """Actualiza el estado de una tarea"""
        try:
            tarea = self.db.query(TareasProyectoModel).filter(
                TareasProyectoModel.id == tarea_id,
                TareasProyectoModel.estado == True
            ).first()
            
            if not tarea:
                raise CustomException("Tarea no encontrada")
            
            # ID del estado "Hecha" según script SQL
            ID_ESTADO_HECHA = 3
            
            # Validar que no se pueda cambiar el estado si ya está en "Hecha"
            if tarea.id_estado_tarea == ID_ESTADO_HECHA:
                raise CustomException("No se puede cambiar el estado de una tarea que ya está marcada como 'Hecha'")
            
            # Verificar que el estado existe
            estado = self.db.query(EstadosTareasModel).filter(
                EstadosTareasModel.id == nuevo_estado_id
            ).first()
            
            if not estado:
                raise CustomException("Estado de tarea no encontrado")
            
            tarea.id_estado_tarea = nuevo_estado_id
            tarea.updated_at = datetime.now()
            
            return tarea
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en actualizar_estado_tarea: {str(e)}")
            raise CustomException("Error al actualizar el estado de la tarea")
    
    def calcular_progreso_proyecto(self, proyecto_id: int):
        """Calcula el progreso del proyecto basado en tareas completadas"""
        try:
            # ID del estado "Hecha" según script SQL (estados_tareas.sql)
            # 1: Pendiente, 2: En progreso, 3: Hecha
            ID_ESTADO_HECHA = 3

            # Contar total de tareas
            total_tareas = self.db.query(TareasProyectoModel).filter(
                TareasProyectoModel.id_proyecto == proyecto_id,
                TareasProyectoModel.estado == True
            ).count()
            
            if total_tareas == 0:
                return 0.00
            
            # Contar tareas completadas (solo las que están en estado "Hecha" = ID 3)
            tareas_completadas = self.db.query(TareasProyectoModel).filter(
                TareasProyectoModel.id_proyecto == proyecto_id,
                TareasProyectoModel.id_estado_tarea == ID_ESTADO_HECHA,
                TareasProyectoModel.estado == True
            ).count()

            # Calcular porcentaje
            progreso = (tareas_completadas / total_tareas) * 100

            return round(progreso, 2)
            
        except Exception as e:
            print(f"Error en calcular_progreso_proyecto: {str(e)}")
            return 0.00
    
    def actualizar_progreso_proyecto(self, proyecto_id: int):
        """Actualiza el progreso de un proyecto automáticamente"""
        try:
            proyecto = self.db.query(ProyectosModel).filter(
                ProyectosModel.id == proyecto_id,
                ProyectosModel.estado == True
            ).first()
            
            if not proyecto:
                raise CustomException("Proyecto no encontrado")
            
            nuevo_progreso = self.calcular_progreso_proyecto(proyecto_id)
            proyecto.progreso = nuevo_progreso
            proyecto.fecha_actualizacion = datetime.now()
            
            # Hacer commit para persistir el progreso actualizado
            self.db.commit()
            # Refrescar para obtener el valor confirmado de la BD
            self.db.refresh(proyecto)
            
            return proyecto
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en actualizar_progreso_proyecto: {str(e)}")
            raise CustomException("Error al actualizar el progreso del proyecto")

