import logging
import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


def enviar_correo(archivo_excel, destinatario, fecha, cajero):
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    if not gmail_user or not gmail_password:
        raise ValueError(
            "Faltan credenciales GMAIL_USER y/o GMAIL_PASSWORD en el archivo .env"
        )

    try:
        asunto = f"Cierre de Caja - {cajero} - {fecha}"
        cuerpo_html = f"""
        <html>
        <body style="font-family: Calibri, sans-serif;">
            <h2 style="color: #4472C4;">Cierre de Caja</h2>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Cajero:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{cajero}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Fecha:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{fecha}</td>
                </tr>
            </table>
            <p style="margin-top: 20px;">Se adjunta el detalle del cierre de caja en formato Excel.</p>
            <p style="color: #888; font-size: 12px;">Este es un mensaje generado automáticamente.</p>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg["From"] = gmail_user
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg["Date"] = formatdate(localtime=True)
        msg.attach(MIMEText(cuerpo_html, "html"))

        with open(archivo_excel, "rb") as adjunto:
            parte = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            parte.set_payload(adjunto.read())

        from email import encoders

        encoders.encode_base64(parte)
        nombre_archivo = os.path.basename(archivo_excel)
        parte.add_header(
            "Content-Disposition",
            f"attachment; filename={nombre_archivo}",
        )
        msg.attach(parte)

        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(gmail_user, gmail_password)
            servidor.send_message(msg)

        logger.info("Correo enviado exitosamente a %s", destinatario)

    except Exception:
        logger.exception("Error al enviar el correo")
        raise
