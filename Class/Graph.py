import os
import requests
from dotenv import load_dotenv

load_dotenv()


class Graph:

    def __init__(self):
        self.client_id = os.getenv("MICROSOFT_CLIENT_ID")
        self.client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        self.tenant_id = os.getenv("MICROSOFT_TENANT_ID")
        self.url_auth = os.getenv("MICROSOFT_URL")        # https://login.microsoftonline.com/
        self.url_graph = os.getenv("MICROSOFT_URL_GRAPH") # https://graph.microsoft.com/v1.0/users/

    def obtener_token(self) -> str:
        url = f"{self.url_auth}{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }
        response = requests.post(url, data=data, timeout=15)
        response.raise_for_status()
        return response.json().get("access_token")

    def enviar_correo(self, email_remitente: str, asunto: str, cuerpo_html: str, destinatarios: list, cc: list = None):
        token = self.obtener_token()
        url = f"{self.url_graph}{email_remitente}/sendMail"
        mensaje = {
            "subject": asunto,
            "body": {
                "contentType": "HTML",
                "content": cuerpo_html
            },
            "toRecipients": [
                {"emailAddress": {"address": d}} for d in destinatarios
            ]
        }
        if cc:
            mensaje["ccRecipients"] = [{"emailAddress": {"address": c}} for c in cc]
        payload = {
            "message": mensaje,
            "saveToSentItems": "true"
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
