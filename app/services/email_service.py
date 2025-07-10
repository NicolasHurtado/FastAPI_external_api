import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from ..config import get_settings
from ..exceptions import EmailServiceException

logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio para envío de correos electrónicos.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """
        Envía un correo electrónico.

        Args:
            to_emails: Lista de emails destinatarios
            subject: Asunto del correo
            body: Cuerpo del correo en texto plano
            html_body: Cuerpo del correo en HTML (opcional)

        Returns:
            True si se envió correctamente, False en caso contrario

        Raises:
            EmailServiceException: Si hay error en el envío
        """
        if not self.settings.smtp_username or not self.settings.smtp_password:
            logger.warning("Configuración de email no disponible")
            return False

        try:
            # Crear mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.settings.smtp_username
            message["To"] = ", ".join(to_emails)

            # Agregar cuerpo en texto plano
            text_part = MIMEText(body, "plain", "utf-8")
            message.attach(text_part)

            # Agregar cuerpo en HTML si está disponible
            if html_body:
                html_part = MIMEText(html_body, "html", "utf-8")
                message.attach(html_part)

            # Configurar servidor SMTP
            with smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port) as server:
                server.starttls()
                server.login(self.settings.smtp_username, self.settings.smtp_password)
                server.send_message(message)

            logger.info(f"Correo enviado exitosamente a {to_emails}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Error de autenticación SMTP")
            raise EmailServiceException("Error de autenticación en el servidor de correo")
        except smtplib.SMTPRecipientsRefused:
            logger.error("Destinatarios rechazados")
            raise EmailServiceException("Destinatarios rechazados por el servidor")
        except smtplib.SMTPException as e:
            logger.error(f"Error SMTP: {e}")
            raise EmailServiceException(f"Error en el servidor de correo: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al enviar correo: {e}")
            raise EmailServiceException(f"Error inesperado al enviar correo: {e}")

    def send_user_status_notification(
        self, user_email: str, user_name: str, external_status: str
    ) -> bool:
        """
        Envía una notificación sobre el estado del usuario basado en datos externos.

        Args:
            user_email: Email del usuario
            user_name: Nombre del usuario
            external_status: Estado obtenido de la API externa

        Returns:
            True si se envió correctamente
        """
        if external_status == "inactive":
            subject = "Estado de Usuario Inactivo"
            body = f"""
            Estimado/a {user_name},

            Hemos detectado que tu estado en nuestro sistema externo es 'inactivo'.

            Por favor, contacta con nuestro equipo de soporte si esto es un error.

            Saludos,
            El equipo de soporte
            """

            html_body = f"""
            <html>
            <body>
                <h2>Estado de Usuario Inactivo</h2>
                <p>Estimado/a <strong>{user_name}</strong>,</p>
                <p>Hemos detectado que tu estado en nuestro sistema externo es '<strong>inactivo</strong>'.</p>
                <p>Por favor, contacta con nuestro equipo de soporte si esto es un error.</p>
                <p>Saludos,<br>El equipo de soporte</p>
            </body>
            </html>
            """

            return self.send_email([user_email], subject, body, html_body)

        return False


# Instancia singleton del servicio
email_service = EmailService()
