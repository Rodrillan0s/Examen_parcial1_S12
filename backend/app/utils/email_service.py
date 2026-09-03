import os
import json
import urllib.request
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import Config

# Servicio de envío de correo transaccional utilizando la API v3 y SMTP de Brevo (Sendinblue)
def enviar_correo_recuperacion_brevo(destinatario_email: str, destinatario_nombre: str, codigo_recuperacion: str) -> bool:
    api_key = os.getenv("MAIL_PASSWORD") or os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "toledoquirogaeddy@gmail.com")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Código de Recuperación — AURA Atelier</title>
    </head>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #0c0c0e; color: #f4f4f5; margin: 0; padding: 40px 20px;">
      <div style="max-width: 520px; margin: 0 auto; background-color: #121216; border: 1px solid rgba(212, 175, 55, 0.25); border-radius: 20px; padding: 36px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
        
        <div style="text-align: center; margin-bottom: 24px;">
          <h1 style="font-family: Georgia, serif; font-size: 28px; color: #ffffff; margin: 0; letter-spacing: 2px;">
            AURA <span style="color: #d4af37; font-weight: 300; font-style: italic;">ATELIER</span>
          </h1>
          <p style="font-size: 11px; text-transform: uppercase; tracking: 3px; color: #a1a1aa; margin-top: 6px;">Recuperación de Contraseña Segura</p>
        </div>

        <div style="border-top: 1px solid #27272a; border-bottom: 1px solid #27272a; padding: 24px 0; margin-bottom: 24px; text-align: center;">
          <p style="font-size: 14px; color: #d4d4d8; margin-bottom: 16px;">
            Hola <strong>{destinatario_nombre}</strong>, hemos recibido una solicitud para restablecer la contraseña de tu cuenta.
          </p>
          
          <div style="background-color: #09090b; border: 1px solid #3f3f46; border-radius: 12px; padding: 16px; margin: 20px 0; display: inline-block; width: 80%;">
            <span style="font-size: 11px; text-transform: uppercase; color: #d4af37; display: block; margin-bottom: 6px; letter-spacing: 1px;">Código de Verificación (15 Minutos)</span>
            <span style="font-family: monospace; font-size: 32px; font-weight: bold; color: #ffffff; letter-spacing: 8px;">{codigo_recuperacion}</span>
          </div>

          <p style="font-size: 12px; color: #a1a1aa; margin-top: 16px; line-height: 1.5;">
            Ingresa este código de 6 dígitos en el panel de la tienda para crear tu nueva contraseña. Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
          </p>
        </div>

        <div style="text-align: center; font-size: 11px; color: #71717a;">
          <p>© 2026 AURA Atelier — Cadena de Tiendas de Moda & Alta Costura</p>
        </div>

      </div>
    </body>
    </html>
    """

    # 1. Intentar mediante la API HTTP v3 de Brevo (Rápido e inmune a bloqueos de puertos SMTP)
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
            "sender": {
                "name": "AURA Atelier Security",
                "email": sender_email
            },
            "to": [
                {
                    "email": destinatario_email,
                    "name": destinatario_nombre
                }
            ],
            "subject": f"✦ {codigo_recuperacion} es tu Código de Recuperación — AURA Atelier",
            "htmlContent": html_content
        }

        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, method='POST')
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json')
        req.add_header('api-key', api_key)

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
            if response.status in (200, 201, 202):
                print(f"[BREVO API SUCCESS] Correo enviado a {destinatario_email}")
                return True

    except Exception as api_err:
        print(f"[BREVO API WARNING] Falló API REST: {api_err}. Intentando SMTP Relay...")

    # 2. Fallback por SMTP Relay de Brevo
    try:
        mail_server = os.getenv("MAIL_SERVER", "smtp-relay.brevo.com")
        mail_port = int(os.getenv("MAIL_PORT", 587))
        mail_user = os.getenv("MAIL_USERNAME")
        mail_pass = os.getenv("MAIL_PASSWORD")

        msg = MIMEMultipart("alternative")
        msg['Subject'] = f"✦ {codigo_recuperacion} es tu Código de Recuperación — AURA Atelier"
        msg['From'] = f"AURA Atelier <{sender_email}>"
        msg['To'] = destinatario_email

        part_html = MIMEText(html_content, 'html')
        msg.attach(part_html)

        with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
            server.starttls()
            server.login(mail_user, mail_pass)
            server.sendmail(sender_email, [destinatario_email], msg.as_string())
            print(f"[BREVO SMTP] Correo enviado exitosamente a {destinatario_email}")
            return True
    except Exception as smtp_err:
        print(f"[BREVO SMTP ERROR] No se pudo enviar el correo por SMTP: {smtp_err}")
        return False
