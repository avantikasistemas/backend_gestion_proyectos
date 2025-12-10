from Utils.tools import Tools, CustomException
from Utils.querys import Querys

class Propuestas:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(db)

    def crear_propuesta(self, data: dict):
        """
        Crea una nueva propuesta.
        
        Args:
            data: Diccionario con los datos de la propuesta
            
        Returns:
            Respuesta con la propuesta creada
        """
        try:
            titulo = data.get("titulo", "").strip()
            resumen = data.get("resumen", "").strip()
            macroprocesos = data.get("macroprocesos", [])  # Lista de IDs
            accion = data.get("accion", "borrador")  # 'borrador' o 'enviar'
            id_usuario = data.get("id_usuario")
            nombre_usuario = data.get("nombre_usuario")
            respuestas = data.get("respuestas", [])  # Lista de respuestas del cuestionario
            
            # Validaciones
            if not titulo:
                raise CustomException("El título es obligatorio")
            
            if not macroprocesos or len(macroprocesos) == 0:
                raise CustomException("Debe seleccionar al menos un macroproceso")
            
            if not id_usuario:
                raise CustomException("Usuario no identificado")
            
            # Determinar el estado según la acción
            codigo_estado = "BORRADOR" if accion == "borrador" else "ENVIADO"
            
            # Obtener el estado usando querys
            estado_obj = self.querys.obtener_estado_por_codigo(codigo_estado)
            
            # Generar código único de propuesta
            ultimo_codigo = self.querys.obtener_ultimo_codigo_propuesta()
            
            if ultimo_codigo:
                ultimo_numero = int(ultimo_codigo.split('-')[1]) if '-' in ultimo_codigo else int(ultimo_codigo)
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            
            codigo = f"{nuevo_numero:04d}"  # Formato: 0001, 0002, etc.
            
            # Convertir lista de macroprocesos a string
            macroprocesos_str = ",".join(map(str, macroprocesos))
            
            # Crear la propuesta usando querys
            nueva_propuesta = self.querys.crear_propuesta(
                titulo=titulo,
                resumen=resumen,
                macroprocesos_str=macroprocesos_str,
                id_estado=estado_obj.id,
                id_usuario=id_usuario,
                nombre_usuario=nombre_usuario,
                codigo=codigo
            )
            
            # Guardar respuestas del cuestionario si existen
            if respuestas and len(respuestas) > 0:
                self.querys.guardar_respuestas_propuesta(nueva_propuesta.id, respuestas)
            
            return self.tools.output(200, "Propuesta creada exitosamente", nueva_propuesta.to_dict())
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al crear propuesta: {str(e)}")
            raise CustomException("Error al crear la propuesta")

    def obtener_propuestas(self, filtros: dict = None):
        """
        Obtiene todas las propuestas con sus estados.
        
        Args:
            filtros: Diccionario con filtros opcionales (id_estado, texto, pagina, limite)
            
        Returns:
            Lista de propuestas con paginación
        """
        try:
            # Extraer filtros
            id_estado = filtros.get("id_estado") if filtros else None
            texto = filtros.get("texto") if filtros else None
            pagina = filtros.get("pagina", 1) if filtros else 1
            limite = filtros.get("limite", 12) if filtros else 12
            
            # Obtener propuestas usando querys con paginación
            resultado = self.querys.listar_propuestas(
                id_estado=id_estado, 
                texto=texto,
                pagina=pagina,
                limite=limite
            )
            
            # Formatear respuesta
            propuestas = []
            for propuesta_obj, estado_obj in resultado['propuestas']:
                propuesta_dict = propuesta_obj.to_dict()
                propuesta_dict["nombre_estado"] = estado_obj.nombre
                propuesta_dict["codigo_estado"] = estado_obj.codigo
                propuestas.append(propuesta_dict)
            
            # Devolver con metadata de paginación
            respuesta_data = {
                'propuestas': propuestas,
                'paginacion': {
                    'total': resultado['total'],
                    'pagina': resultado['pagina'],
                    'limite': resultado['limite'],
                    'total_paginas': resultado['total_paginas']
                }
            }
            
            return self.tools.output(200, "Propuestas obtenidas correctamente", respuesta_data)
            
        except Exception as e:
            print(f"Error al obtener propuestas: {str(e)}")
            raise CustomException("Error al obtener propuestas")

    def obtener_propuesta_detalle(self, propuesta_id: int):
        """
        Obtiene el detalle de una propuesta específica.
        
        Args:
            propuesta_id: ID de la propuesta
            
        Returns:
            Respuesta con los datos de la propuesta incluyendo macroprocesos completos
        """
        try:
            # Obtener propuesta usando querys
            result = self.querys.obtener_propuesta_por_id(propuesta_id)
            
            if not result:
                raise CustomException("Propuesta no encontrada")
            
            propuesta_obj, estado_obj = result
            
            # Formatear respuesta
            propuesta_dict = propuesta_obj.to_dict()
            propuesta_dict["nombre_estado"] = estado_obj.nombre
            propuesta_dict["codigo_estado"] = estado_obj.codigo
            
            # Obtener macroprocesos completos si existen IDs
            if propuesta_obj.macroprocesos_ids:
                # Parsear los IDs del string "1,3,5" a lista de enteros
                try:
                    ids_str = propuesta_obj.macroprocesos_ids.split(',')
                    ids_list = [int(id.strip()) for id in ids_str if id.strip()]
                    
                    # Obtener los macroprocesos completos
                    macroprocesos_objs = self.querys.obtener_macroprocesos_por_ids(ids_list)
                    
                    # Convertir a diccionarios
                    propuesta_dict["macroprocesos"] = [mp.to_dict() for mp in macroprocesos_objs]
                except ValueError as e:
                    print(f"Error al parsear IDs de macroprocesos: {str(e)}")
                    propuesta_dict["macroprocesos"] = []
            else:
                propuesta_dict["macroprocesos"] = []
            
            # Obtener respuestas del cuestionario
            respuestas_result = self.querys.obtener_respuestas_propuesta(propuesta_id)
            respuestas_list = []
            
            for respuesta_obj, pregunta_obj in respuestas_result:
                respuestas_list.append({
                    "id_pregunta": pregunta_obj.id,
                    "pregunta": pregunta_obj.pregunta,
                    "descripcion": pregunta_obj.descripcion,
                    "respuesta": respuesta_obj.respuesta,
                    "orden": pregunta_obj.orden
                })
            
            propuesta_dict["respuestas"] = respuestas_list
            
            return self.tools.output(200, "Propuesta obtenida correctamente", propuesta_dict)
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al obtener detalle de propuesta: {str(e)}")
            raise CustomException("Error al obtener el detalle de la propuesta")

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de propuestas agrupadas por estado.
        
        Returns:
            Respuesta con estadísticas por estado
        """
        try:
            estadisticas = self.querys.obtener_estadisticas_propuestas()
            
            return self.tools.output(200, "Estadísticas obtenidas correctamente", estadisticas)
            
        except Exception as e:
            print(f"Error al obtener estadísticas: {str(e)}")
            raise CustomException("Error al obtener estadísticas de propuestas")

    def cambiar_estado(self, data: dict):
        """
        Cambia el estado de una propuesta.
        
        Args:
            data: Diccionario con id_propuesta, codigo_estado, motivo_rechazo (opcional)
            
        Returns:
            Respuesta con la propuesta actualizada
        """
        try:
            id_propuesta = data.get("id_propuesta")
            codigo_estado = data.get("codigo_estado")
            motivo_rechazo = data.get("motivo_rechazo")
            
            if not id_propuesta:
                raise CustomException("ID de propuesta requerido")
            
            if not codigo_estado:
                raise CustomException("Código de estado requerido")
            
            # Cambiar estado usando querys
            propuesta_actualizada = self.querys.cambiar_estado_propuesta(
                id_propuesta=id_propuesta,
                codigo_estado=codigo_estado,
                motivo_rechazo=motivo_rechazo
            )
            
            return self.tools.output(200, "Estado actualizado correctamente", propuesta_actualizada.to_dict())
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al cambiar estado: {str(e)}")
            raise CustomException("Error al cambiar el estado de la propuesta")
