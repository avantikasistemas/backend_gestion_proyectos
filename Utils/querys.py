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
from Models.TiposClasificacionModel import TiposClasificacionModel
from Models.IntranetProyectosTiposKanbanModel import IntranetProyectosTiposKanbanModel
from Models.SprintProyectoModel import SprintProyectoModel

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
                       id_usuario: int, nombre_usuario: str, codigo: str,
                       id_macroproceso_solicitante: int = None):
        """
        Crea una nueva propuesta en la base de datos.
        
        Args:
            titulo: Título de la propuesta
            resumen: Descripción de la propuesta
            macroprocesos_str: IDs de macroprocesos separados por coma "1,3,5"
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
                id_macroproceso_solicitante=id_macroproceso_solicitante,
                macroprocesos_ids=macroprocesos_str,
                # id_estado=id_estado,
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

    def listar_propuestas(self, id_estado: int = None, texto: str = None, pagina: int = 1, limite: int = 12, id_tipo_clasificacion: int = None):
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
            ).filter(
                PropuestasModel.estado == 1
            )
            
            # Aplicar filtro por tipo de clasificación si existe
            if id_tipo_clasificacion:
                query = query.filter(PropuestasModel.id_tipo_clasificacion == id_tipo_clasificacion)
            
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
        Obtiene una propuesta por su ID.
        
        Args:
            propuesta_id: ID de la propuesta
            
        Returns:
            PropuestasModel o None si no se encuentra
        """
        try:
            result = self.db.query(PropuestasModel).filter(
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

    def obtener_tipo_clasificacion_por_id(self, id_tipo: int):
        """Retorna el objeto TiposClasificacionModel con el id dado, o None si no existe."""
        try:
            return self.db.query(TiposClasificacionModel).filter(
                TiposClasificacionModel.id == id_tipo,
                TiposClasificacionModel.estado == 1
            ).first()
        except Exception as e:
            print(f"Error en obtener_tipo_clasificacion_por_id: {str(e)}")
            return None

    def obtener_email_usuario_por_id(self, id_usuario: int):
        """Retorna el email del usuario con el id dado, o None si no existe."""
        try:
            usuario = self.db.query(IntranetUsuariosProyectosModel).filter(
                IntranetUsuariosProyectosModel.id == id_usuario,
                IntranetUsuariosProyectosModel.estado == 1
            ).first()
            return usuario.email if usuario else None
        except Exception as e:
            print(f"Error en obtener_email_usuario_por_id: {str(e)}")
            return None

    def obtener_datos_email_propuesta(self, macroprocesos_ids: list, id_macroproceso_solicitante):
        """
        Consolida los datos necesarios para construir el correo de notificación de una propuesta:
        nombres de macroprocesos impactados y nombre del macroproceso solicitante.

        Returns:
            dict: {mp_nombres, nombre_solicitante}
        """
        try:
            # Nombres de macroprocesos impactados
            mp_rows = self.obtener_macroprocesos_por_ids(macroprocesos_ids) if macroprocesos_ids else []
            mp_nombres = [mp.nombre for mp in mp_rows]

            # Nombre del macroproceso solicitante
            nombre_solicitante = "—"
            if id_macroproceso_solicitante:
                sol_rows = self.obtener_macroprocesos_por_ids([id_macroproceso_solicitante])
                if sol_rows:
                    nombre_solicitante = sol_rows[0].nombre

            return {
                "mp_nombres": mp_nombres,
                "nombre_solicitante": nombre_solicitante
            }
        except Exception as e:
            print(f"Error en obtener_datos_email_propuesta: {str(e)}")
            return {"mp_nombres": [], "nombre_solicitante": "—"}

    def obtener_estadisticas_propuestas(self):
        """
        Obtiene el total de propuestas activas y el desglose por tipo de clasificación.
        
        Returns:
            dict: { total, por_clasificacion: [{id, nombre, cantidad}] }
        """
        try:
            total = self.db.query(func.count(PropuestasModel.id)).filter(
                PropuestasModel.estado == 1
            ).scalar()

            result = self.db.query(
                TiposClasificacionModel.id.label('clasificacion_id'),
                TiposClasificacionModel.nombre.label('clasificacion_nombre'),
                func.count(PropuestasModel.id).label('cantidad')
            ).outerjoin(
                PropuestasModel,
                (PropuestasModel.id_tipo_clasificacion == TiposClasificacionModel.id) &
                (PropuestasModel.estado == 1)
            ).filter(
                TiposClasificacionModel.estado == 1
            ).group_by(
                TiposClasificacionModel.id,
                TiposClasificacionModel.nombre,
                TiposClasificacionModel.orden
            ).order_by(
                TiposClasificacionModel.orden.asc()
            ).all()

            por_clasificacion = [
                { 'id': r.clasificacion_id, 'nombre': r.clasificacion_nombre, 'cantidad': r.cantidad }
                for r in result
            ]

            return { 'total': total or 0, 'por_clasificacion': por_clasificacion }
            
        except Exception as e:
            print(f"Error en obtener_estadisticas_propuestas: {str(e)}")
            raise CustomException("Error al obtener estadísticas de propuestas")

    def cambiar_estado_propuesta(self, id_propuesta: int, codigo_estado: str,
                                   id_tipo_clasificacion: int = None, comentario_clasificacion: str = None):
        """
        Cambia el estado de una propuesta.
        
        Args:
            id_propuesta: ID de la propuesta
            codigo_estado: Código del nuevo estado (EN_REVISION, APROBADA, RECHAZADA)
            motivo_rechazo: Motivo del rechazo (obligatorio si estado es RECHAZADA)
            id_tipo_clasificacion: Tipo de clasificación (obligatorio si estado es APROBADA)
            comentario_clasificacion: Comentario de clasificación (obligatorio si estado es APROBADA)
            
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
            
            # Si es aprobada, guardar clasificación
            if codigo_estado == 'APROBADA':
                if not id_tipo_clasificacion:
                    raise CustomException("El tipo de clasificación es obligatorio para aprobar")
                if not comentario_clasificacion or not comentario_clasificacion.strip():
                    raise CustomException("El comentario de clasificación es obligatorio para aprobar")
                propuesta.id_tipo_clasificacion = id_tipo_clasificacion
                propuesta.comentario_clasificacion = comentario_clasificacion.strip()
            
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

    def clasificar_propuesta(self, id_propuesta: int, id_tipo_clasificacion: int, comentario_clasificacion: str, id_origen_iniciativa: int = None):
        """
        Actualiza únicamente el tipo de clasificación y el comentario de una propuesta.
        """
        try:
            propuesta = self.db.query(PropuestasModel).filter(
                PropuestasModel.id == id_propuesta,
                PropuestasModel.estado == 1
            ).first()

            if not propuesta:
                raise CustomException("Propuesta no encontrada")

            propuesta.id_tipo_clasificacion = id_tipo_clasificacion
            propuesta.comentario_clasificacion = comentario_clasificacion.strip()
            if id_origen_iniciativa:
                propuesta.id_origen_iniciativa = id_origen_iniciativa

            self.db.commit()
            self.db.refresh(propuesta)
            return propuesta

        except CustomException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            print(f"Error en clasificar_propuesta: {str(e)}")
            raise CustomException("Error al clasificar la propuesta")

    # ==================== MÉTODOS PARA PROYECTOS ====================

    def obtener_propuestas_aprobadas_sin_proyecto(self):
        """
        Obtiene propuestas que están aprobadas y NO tienen proyecto asignado.
        
        Returns:
            list: Lista de propuestas aprobadas sin proyecto
        """
        try:
            # Consulta con SQLAlchemy ORM: propuestas sin proyecto asignado
            propuestas = self.db.query(PropuestasModel).filter(
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
                    'created_at': p.created_at.isoformat() if p.created_at else None
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
                ProyectosModel.id_propuesta,
                ProyectosModel.criterios_aceptacion,
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

    # ==================== MÉTODOS PARA CRITERIOS DE ACEPTACIÓN EN PROYECTO ====================

    def actualizar_criterios_proyecto(self, proyecto_id: int, criterios: str):
        """Actualiza el texto de criterios de aceptación del proyecto"""
        try:
            proyecto = self.db.query(ProyectosModel).filter(
                ProyectosModel.id == proyecto_id,
                ProyectosModel.estado == True
            ).first()

            if not proyecto:
                raise CustomException("Proyecto no encontrado")

            proyecto.criterios_aceptacion = criterios
            proyecto.fecha_actualizacion = datetime.now()
            return proyecto

        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en actualizar_criterios_proyecto: {str(e)}")
            raise CustomException("Error al actualizar los criterios de aceptación")

    # ==================== MÉTODOS PARA CRITERIOS INDIVIDUALES (legacy) ====================
    
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

    def mover_columna_tarea(self, tarea_id: int, id_kanban: int):
        """Actualiza la columna kanban de una tarea usando id_kanban"""
        try:
            tarea = self.db.query(TareasProyectoModel).filter(
                TareasProyectoModel.id == tarea_id,
                TareasProyectoModel.estado == True
            ).first()

            if not tarea:
                raise CustomException("Tarea no encontrada")

            # Verificar que el kanban existe
            kanban = self.db.query(IntranetProyectosTiposKanbanModel).filter(
                IntranetProyectosTiposKanbanModel.id == id_kanban,
                IntranetProyectosTiposKanbanModel.estado == 1
            ).first()
            if not kanban:
                raise CustomException("Columna kanban no encontrada")

            tarea.id_kanban = id_kanban
            tarea.updated_at = datetime.now()
            return tarea

        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en mover_columna_tarea: {str(e)}")
            raise CustomException("Error al mover la tarea")

    def listar_tipos_kanban(self):
        """Lista todos los tipos de columna kanban activos ordenados"""
        try:
            kanbans = self.db.query(IntranetProyectosTiposKanbanModel).filter(
                IntranetProyectosTiposKanbanModel.estado == 1
            ).order_by(IntranetProyectosTiposKanbanModel.orden).all()
            return [k.to_dict() for k in kanbans]
        except Exception as e:
            print(f"Error en listar_tipos_kanban: {str(e)}")
            raise CustomException("Error al listar los tipos kanban")

    def actualizar_tarea(self, tarea_id: int, data: dict):
        """Actualiza los campos editables de una tarea"""
        try:
            tarea = self.db.query(TareasProyectoModel).filter(
                TareasProyectoModel.id == tarea_id,
                TareasProyectoModel.estado == True
            ).first()

            if not tarea:
                raise CustomException("Tarea no encontrada")

            if data.get('titulo'):
                tarea.titulo = data['titulo']
            if 'descripcion' in data:
                tarea.descripcion = data['descripcion']
            if data.get('responsable'):
                tarea.responsable = data['responsable']
            if 'horas_estimadas' in data:
                tarea.horas_estimadas = data['horas_estimadas']
            if 'horas_reales' in data:
                tarea.horas_reales = data['horas_reales']
            if data.get('id_kanban'):
                kanban = self.db.query(IntranetProyectosTiposKanbanModel).filter(
                    IntranetProyectosTiposKanbanModel.id == data['id_kanban'],
                    IntranetProyectosTiposKanbanModel.estado == 1
                ).first()
                if not kanban:
                    raise CustomException("Columna kanban no encontrada")
                tarea.id_kanban = data['id_kanban']
            if 'id_sprint' in data:
                tarea.id_sprint = data['id_sprint']

            tarea.updated_at = datetime.now()
            return tarea

        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error en actualizar_tarea: {str(e)}")
            raise CustomException("Error al actualizar la tarea")

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
    
    def listar_tareas_proyecto(self, proyecto_id: int, id_sprint: int = None):
        """Lista todas las tareas de un proyecto con su columna kanban, con filtro opcional por sprint"""
        try:
            query = self.db.query(
                TareasProyectoModel,
                IntranetProyectosTiposKanbanModel.nombre.label('nombre_kanban'),
                SprintProyectoModel.nombre.label('nombre_sprint')
            ).join(
                IntranetProyectosTiposKanbanModel,
                TareasProyectoModel.id_kanban == IntranetProyectosTiposKanbanModel.id
            ).outerjoin(
                SprintProyectoModel,
                TareasProyectoModel.id_sprint == SprintProyectoModel.id
            ).filter(
                TareasProyectoModel.id_proyecto == proyecto_id,
                TareasProyectoModel.estado == True
            )

            if id_sprint is not None:
                query = query.filter(TareasProyectoModel.id_sprint == id_sprint)

            tareas = query.order_by(TareasProyectoModel.created_at.desc()).all()

            resultado = []
            for tarea, nombre_kanban, nombre_sprint in tareas:
                tarea_dict = tarea.to_dict()
                tarea_dict['nombre_kanban'] = nombre_kanban
                tarea_dict['nombre_sprint'] = nombre_sprint
                resultado.append(tarea_dict)

            return resultado

        except Exception as e:
            print(f"Error en listar_tareas_proyecto: {str(e)}")
            raise CustomException("Error al listar las tareas del proyecto")
    
    def actualizar_estado_tarea(self, tarea_id: int, nuevo_estado_id: int):
        """Deprecated: usar mover_columna_tarea con id_kanban en su lugar"""
        raise CustomException("El endpoint actualizar-estado está deprecado. Usa mover-columna con id_kanban")

