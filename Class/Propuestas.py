from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Class.Graph import Graph

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
            id_usuario = data.get("id_usuario")
            nombre_usuario = data.get("nombre_usuario")
            email_usuario = data.get("email_usuario", "")
            respuestas = data.get("respuestas", [])  # Lista de respuestas del cuestionario
            id_macroproceso_solicitante = data.get("id_macroproceso_solicitante")
            
            # Validaciones
            if not titulo:
                raise CustomException("El título es obligatorio")
            
            if not macroprocesos or len(macroprocesos) == 0:
                raise CustomException("Debe seleccionar al menos un macroproceso")
            
            if not id_usuario:
                raise CustomException("Usuario no identificado")
            
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
                id_usuario=id_usuario,
                nombre_usuario=nombre_usuario,
                codigo=codigo,
                id_macroproceso_solicitante=id_macroproceso_solicitante
            )
            
            # Guardar respuestas del cuestionario si existen
            if respuestas and len(respuestas) > 0:
                self.querys.guardar_respuestas_propuesta(nueva_propuesta.id, respuestas)

            # Enviar correo de notificación (sin bloquear la creación si falla)
            if email_usuario:
                try:
                    cuerpo_html = self._construir_html_propuesta(
                        nueva_propuesta_id=None,
                        codigo=codigo,
                        titulo=titulo,
                        resumen=resumen,
                        nombre_usuario=nombre_usuario,
                        email_usuario=email_usuario,
                        macroprocesos_ids=macroprocesos,
                        id_macroproceso_solicitante=id_macroproceso_solicitante
                    )
                    Graph().enviar_correo(
                        email_remitente=email_usuario,
                        asunto=f"Nueva iniciativa registrada: {codigo} - {titulo}",
                        cuerpo_html=cuerpo_html,
                        destinatarios=["sistemas@avantika.com.co", "auxiliartic@avantika.com.co"]
                    )
                except Exception as mail_error:
                    print(f"[Graph] Error al enviar correo de notificación: {str(mail_error)}")

            return self.tools.output(200, "Propuesta creada exitosamente", nueva_propuesta.to_dict())
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al crear propuesta: {str(e)}")
            raise CustomException("Error al crear la propuesta")

    def _construir_html_propuesta(self, nueva_propuesta_id, codigo, titulo, resumen, nombre_usuario,
                                   email_usuario, macroprocesos_ids, id_macroproceso_solicitante):
        """Genera el cuerpo HTML para el correo de notificación de nueva propuesta."""
        import base64, os

        datos = self.querys.obtener_datos_email_propuesta(
            macroprocesos_ids=macroprocesos_ids,
            id_macroproceso_solicitante=id_macroproceso_solicitante
        )
        mp_nombres = datos["mp_nombres"]
        nombre_solicitante = datos["nombre_solicitante"]

        # Leer y codificar el logo en base64
        logo_b64 = ""
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo.png")
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass

        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:55px;" alt="Avántika" />' if logo_b64 else ""

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;color:#333;">
            <div style="background:#1a3c5e;padding:20px 30px;border-radius:8px 8px 0 0;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <h2 style="margin:0;color:#fff;">Nueva iniciativa registrada</h2>
                    <p style="margin:4px 0 0;color:#cde;font-size:14px;">Sistema de Gestión de Proyectos – Avántika</p>
                </div>
                {logo_html}
            </div>
            <div style="background:#fff;padding:24px 30px;border:1px solid #dde;">

                <table style="border-collapse:collapse;width:100%;">
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;width:35%;">Código</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{codigo}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Nombre</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{titulo}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Descripción</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{resumen}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Registrado por</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{nombre_usuario} ({email_usuario})</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Macroproceso solicitante</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{nombre_solicitante}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Macroprocesos impactados</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{', '.join(mp_nombres) if mp_nombres else '—'}</td>
                    </tr>
                </table>

            </div>
            <div style="background:#f0f4f8;padding:12px 30px;border-radius:0 0 8px 8px;font-size:12px;color:#888;">
                Este correo fue generado automáticamente. Por favor no responder.
            </div>
        </div>
        """
        return html

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
            id_tipo_clasificacion = filtros.get("id_tipo_clasificacion") if filtros else None
            
            # Obtener propuestas usando querys con paginación
            resultado = self.querys.listar_propuestas(
                id_estado=id_estado, 
                texto=texto,
                pagina=pagina,
                limite=limite,
                id_tipo_clasificacion=id_tipo_clasificacion
            )
            
            # Formatear respuesta
            propuestas = []
            for propuesta_obj in resultado['propuestas']:
                propuestas.append(propuesta_obj.to_dict())
            
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
            propuesta_obj = self.querys.obtener_propuesta_por_id(propuesta_id)
            
            if not propuesta_obj:
                raise CustomException("Propuesta no encontrada")
            
            # Formatear respuesta
            propuesta_dict = propuesta_obj.to_dict()
            
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

            # Obtener nombre del macroproceso solicitante
            if propuesta_obj.id_macroproceso_solicitante:
                mps = self.querys.obtener_macroprocesos_por_ids([propuesta_obj.id_macroproceso_solicitante])
                propuesta_dict["nombre_macroproceso_solicitante"] = mps[0].nombre if mps else None
            else:
                propuesta_dict["nombre_macroproceso_solicitante"] = None
            
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
            id_tipo_clasificacion = data.get("id_tipo_clasificacion")
            comentario_clasificacion = data.get("comentario_clasificacion")
            
            if not id_propuesta:
                raise CustomException("ID de propuesta requerido")
            
            if not codigo_estado:
                raise CustomException("Código de estado requerido")
            
            # Cambiar estado usando querys
            propuesta_actualizada = self.querys.cambiar_estado_propuesta(
                id_propuesta=id_propuesta,
                codigo_estado=codigo_estado,
                id_tipo_clasificacion=id_tipo_clasificacion,
                comentario_clasificacion=comentario_clasificacion
            )
            
            return self.tools.output(200, "Estado actualizado correctamente", propuesta_actualizada.to_dict())
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al cambiar estado: {str(e)}")
            raise CustomException("Error al cambiar el estado de la propuesta")

    def clasificar(self, data: dict):
        """
        Actualiza el tipo de clasificación y el comentario de una propuesta.
        Si el id de clasificación es 3 o 4, envía un correo formal al área correspondiente.
        """
        try:
            id_propuesta = data.get("id_propuesta")
            id_tipo_clasificacion = data.get("id_tipo_clasificacion")
            comentario_clasificacion = data.get("comentario_clasificacion", "")
            email_usuario = data.get("email_usuario", "sistemas@avantika.com.co")
            id_origen_iniciativa = data.get("id_origen_iniciativa")

            if not id_propuesta:
                raise CustomException("ID de propuesta requerido")

            if not id_tipo_clasificacion:
                raise CustomException("El tipo de clasificación es obligatorio")

            if not comentario_clasificacion or not str(comentario_clasificacion).strip():
                raise CustomException("El comentario de clasificación es obligatorio")

            propuesta_actualizada = self.querys.clasificar_propuesta(
                id_propuesta=id_propuesta,
                id_tipo_clasificacion=id_tipo_clasificacion,
                comentario_clasificacion=comentario_clasificacion,
                id_origen_iniciativa=id_origen_iniciativa
            )
            
            texto_extra = ' en el PTC-53' if id_tipo_clasificacion == 3 else '.'

            # Enviar correo si la clasificación es id 3 (Mejora Operativa) o id 4 (Acción SIG)
            if id_tipo_clasificacion in (3, 4):
                try:
                    tipo_obj = self.querys.obtener_tipo_clasificacion_por_id(id_tipo_clasificacion)
                    nombre_tipo = tipo_obj.nombre if tipo_obj else f"Tipo {id_tipo_clasificacion}"
                    destinatario = "soporte@avantika.com.co" if id_tipo_clasificacion == 3 else "calidad@avantika.com.co"
                    cc = ["innovacion@avantika.com.co", "tic@avantika.com.co", "sistemas@avantika.com.co"] if id_tipo_clasificacion == 3 else ["innovacion@avantika.com.co"]

                    cuerpo_html = self._construir_html_clasificacion(
                        codigo=propuesta_actualizada.codigo,
                        titulo=propuesta_actualizada.titulo,
                        resumen=propuesta_actualizada.resumen or "",
                        nombre_tipo=nombre_tipo,
                        nombre_creador=propuesta_actualizada.nombre_creador or "",
                        comentario=comentario_clasificacion,
                        texto_extra=texto_extra
                    )
                    Graph().enviar_correo(
                        email_remitente=email_usuario,
                        asunto=f"Solicitud de gestión de iniciativa: INI-{propuesta_actualizada.codigo} – {propuesta_actualizada.titulo}",
                        cuerpo_html=cuerpo_html,
                        destinatarios=[destinatario],
                        cc=cc
                    )
                except Exception as mail_error:
                    print(f"[Graph] Error al enviar correo de clasificación: {str(mail_error)}")

            # Enviar correo al creador si la clasificación es id 5 (Banco de Ideas)
            elif id_tipo_clasificacion == 5:
                try:
                    email_creador = self.querys.obtener_email_usuario_por_id(
                        propuesta_actualizada.id_usuario_creador
                    )
                    if email_creador:
                        cuerpo_html = self._construir_html_banco_ideas(
                            codigo=propuesta_actualizada.codigo,
                            titulo=propuesta_actualizada.titulo,
                            resumen=propuesta_actualizada.resumen or "",
                            nombre_creador=propuesta_actualizada.nombre_creador or ""
                        )
                        Graph().enviar_correo(
                            email_remitente=email_usuario,
                            asunto=f"Actualización sobre tu iniciativa: INI-{propuesta_actualizada.codigo} – {propuesta_actualizada.titulo}",
                            cuerpo_html=cuerpo_html,
                            destinatarios=[email_creador],
                            # cc=["innovacion@avantika.com.co"]
                            cc=[]
                        )
                except Exception as mail_error:
                    print(f"[Graph] Error al enviar correo de banco de ideas: {str(mail_error)}")

            return self.tools.output(200, "Propuesta clasificada correctamente", propuesta_actualizada.to_dict())

        except CustomException as e:
            raise e
        except Exception as e:
            print(f"Error al clasificar propuesta: {str(e)}")
            raise CustomException("Error al clasificar la propuesta")

    def _construir_html_banco_ideas(self, codigo, titulo, resumen, nombre_creador):
        """Genera el cuerpo HTML del correo formal al creador cuando la iniciativa pasa al banco de ideas."""
        import base64, os

        logo_b64 = ""
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo.png")
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass

        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:55px;" alt="Avántika" />' if logo_b64 else ""

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;color:#333;">
            <div style="background:#1a3c5e;padding:20px 30px;border-radius:8px 8px 0 0;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <h2 style="margin:0;color:#fff;">Actualización sobre tu iniciativa</h2>
                    <p style="margin:4px 0 0;color:#cde;font-size:14px;">Sistema de Gestión de Proyectos – Avántika</p>
                </div>
                {logo_html}
            </div>
            <div style="background:#fff;padding:24px 30px;border:1px solid #dde;">

                <p style="font-size:14px;color:#374151;line-height:1.6;">Estimado/a <strong>{nombre_creador}</strong>,</p>
                <p style="font-size:14px;color:#374151;line-height:1.6;">
                    Agradecemos el tiempo y el esfuerzo que dedicaste al registro de la siguiente iniciativa en nuestro
                    Sistema de Gestión de Proyectos. Tu aporte es valioso para la organización y es parte fundamental
                    de nuestra cultura de mejora e innovación continua.
                </p>
                <p style="font-size:14px;color:#374151;line-height:1.6;">
                    Luego de la revisión realizada por la Dirección de Innovación, la iniciativa
                    <strong>"{titulo}"</strong> ha sido incorporada al <strong>Banco de Ideas de Avántika</strong>.
                    Esto significa que, si bien en este momento no cuenta con los recursos o las condiciones necesarias
                    para su ejecución inmediata, la propuesta será conservada y podrá ser retomada en una etapa
                    futura cuando las circunstancias lo permitan.
                </p>

                <table style="border-collapse:collapse;width:100%;margin-top:16px;">
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;width:35%;">Código</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">INI-{codigo}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Título</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{titulo}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Descripción</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{resumen}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Estado</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">Incorporada al Banco de Ideas</td>
                    </tr>
                </table>

                <p style="font-size:14px;color:#374151;line-height:1.6;margin-top:20px;">
                    Te invitamos a continuar participando activamente con nuevas ideas y propuestas. Cada aporte
                    contribuye al crecimiento y la transformación de Avántika.<br><br>
                    Cordialmente,<br>
                    <strong>Dirección de Innovación</strong><br>
                    Avántika S.A.S.
                </p>
            </div>
            <div style="background:#f0f4f8;padding:12px 30px;border-radius:0 0 8px 8px;font-size:12px;color:#888;">
                Este correo fue generado automáticamente. Por favor no responder.
            </div>
        </div>
        """
        return html

    def _construir_html_clasificacion(self, codigo, titulo, resumen, nombre_tipo, nombre_creador, comentario, texto_extra):
        """Genera el cuerpo HTML del correo formal de solicitud de gestión enviado al área correspondiente."""
        import base64, os

        logo_b64 = ""
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo.png")
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass

        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:55px;" alt="Avántika" />' if logo_b64 else ""

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;color:#333;">
            <div style="background:#1a3c5e;padding:20px 30px;border-radius:8px 8px 0 0;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <h2 style="margin:0;color:#fff;">Solicitud de gestión de iniciativa</h2>
                    <p style="margin:4px 0 0;color:#cde;font-size:14px;">Sistema de Gestión de Proyectos – Avántika</p>
                </div>
                {logo_html}
            </div>
            <div style="background:#fff;padding:24px 30px;border:1px solid #dde;">

                <p style="font-size:14px;color:#374151;line-height:1.6;">Estimado equipo,</p>
                <p style="font-size:14px;color:#374151;line-height:1.6;">
                    Por medio del presente correo, nos permitimos informarles que la siguiente iniciativa ha sido revisada
                    y clasificada por la Dirección de Innovación como <strong>{nombre_tipo}</strong>, por lo cual se
                    requiere de su área la revisión, valoración y gestión correspondiente de acuerdo con los
                    procedimientos establecidos{texto_extra}
                </p>

                <table style="border-collapse:collapse;width:100%;margin-top:16px;">
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;width:35%;">Código</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">INI-{codigo}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Título</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{titulo}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Descripción</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{resumen}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Registrado por</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{nombre_creador}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Clasificación</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{nombre_tipo}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #ddd;font-weight:bold;background:#f7f9fc;">Observación del Director</td>
                        <td style="padding:6px 10px;border:1px solid #ddd;">{comentario}</td>
                    </tr>
                </table>

                <p style="font-size:14px;color:#374151;line-height:1.6;margin-top:20px;">
                    Agradecemos su atención y colaboración para dar el trámite correspondiente a esta solicitud.<br><br>
                    Cordialmente,<br>
                    <strong>Dirección de Innovación</strong><br>
                    Avántika S.A.S.
                </p>
            </div>
            <div style="background:#f0f4f8;padding:12px 30px;border-radius:0 0 8px 8px;font-size:12px;color:#888;">
                Este correo fue generado automáticamente. Por favor no responder.
            </div>
        </div>
        """
        return html
