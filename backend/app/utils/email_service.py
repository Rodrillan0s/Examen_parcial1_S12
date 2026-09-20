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

def enviar_correo_comprobante(
    destinatario_email: str,
    destinatario_nombre: str,
    tipo_documento: str,
    numero_documento: str,
    total_bs: float,
    pdf_bytes: bytes,
    nombre_archivo: str = "Comprobante_Venta.pdf"
) -> bool:
    """
    W29: Envía por correo el comprobante o factura electrónica en PDF adjunto.
    Si el correo falla, captura la excepción y no interrumpe la venta ya confirmada.
    """
    import base64
    from email.mime.application import MIMEApplication

    if not destinatario_email or '@' not in destinatario_email:
        print(f"[W29 EMAIL NOTICE] No se proporcionó un correo válido para el cliente ({destinatario_email}).")
        return False

    api_key = os.getenv("MAIL_PASSWORD") or os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "toledoquirogaeddy@gmail.com")

    doc_label = "Factura Electrónica" if "FACTURA" in tipo_documento.upper() else (
        "Comprobante de Reserva" if "RESERVA" in tipo_documento.upper() else "Comprobante de Venta"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>{doc_label} — AURA Atelier</title>
    </head>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #0c0c0e; color: #f4f4f5; margin: 0; padding: 40px 20px;">
      <div style="max-width: 560px; margin: 0 auto; background-color: #121216; border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 20px; padding: 36px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
        
        <div style="text-align: center; margin-bottom: 24px;">
          <h1 style="font-family: Georgia, serif; font-size: 28px; color: #ffffff; margin: 0; letter-spacing: 2px;">
            AURA <span style="color: #d4af37; font-weight: 300; font-style: italic;">ATELIER</span>
          </h1>
          <p style="font-size: 11px; text-transform: uppercase; letter-spacing: 3px; color: #a1a1aa; margin-top: 6px;">Comprobante de Operación Oficial</p>
        </div>

        <div style="border-top: 1px solid #27272a; border-bottom: 1px solid #27272a; padding: 24px 0; margin-bottom: 24px;">
          <p style="font-size: 14px; color: #d4d4d8; margin-bottom: 14px;">
            Estimado/a <strong>{destinatario_nombre}</strong>, tu compra ha sido confirmada con éxito.
          </p>
          
          <div style="background-color: #09090b; border: 1px solid #27272a; border-radius: 12px; padding: 18px; margin: 16px 0;">
            <table style="width: 100%; font-size: 12px; color: #d4d4d8;">
              <tr>
                <td style="padding: 4px 0; color: #a1a1aa;">Documento:</td>
                <td style="padding: 4px 0; font-weight: bold; text-align: right; color: #d4af37;">{doc_label}</td>
              </tr>
              <tr>
                <td style="padding: 4px 0; color: #a1a1aa;">N° Operación:</td>
                <td style="padding: 4px 0; font-family: monospace; font-weight: bold; text-align: right; color: #ffffff;">{numero_documento}</td>
              </tr>
              <tr>
                <td style="padding: 4px 0; color: #a1a1aa;">Monto Total:</td>
                <td style="padding: 4px 0; font-weight: bold; text-align: right; color: #10b981; font-size: 14px;">Bs. {total_bs:.2f}</td>
              </tr>
            </table>
          </div>

          <p style="font-size: 12px; color: #a1a1aa; line-height: 1.5; margin-top: 16px;">
            Adjuntamos a este correo tu comprobante en formato PDF con todos los detalles de la compra, desglose de prendas y datos de facturación.
          </p>
        </div>

        <div style="text-align: center; font-size: 11px; color: #71717a;">
          <p>© 2026 AURA Atelier — Cadena de Tiendas de Moda & Alta Costura</p>
          <p style="font-size: 10px; color: #52525b; margin-top: 4px;">Este correo contiene información fiscal y de entrega confidencial.</p>
        </div>

      </div>
    </body>
    </html>
    """

    # 1. Intentar mediante la API HTTP v3 de Brevo con adjunto Base64
    try:
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
            "sender": {
                "name": "AURA Atelier Pagos & Facturación",
                "email": sender_email
            },
            "to": [
                {
                    "email": destinatario_email,
                    "name": destinatario_nombre
                }
            ],
            "subject": f"✦ Tu {doc_label} {numero_documento} — AURA Atelier",
            "htmlContent": html_content,
            "attachment": [
                {
                    "name": nombre_archivo,
                    "content": b64_pdf
                }
            ]
        }

        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, method='POST')
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json')
        req.add_header('api-key', api_key)

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            if response.status in (200, 201, 202):
                print(f"[BREVO API SUCCESS] Comprobante PDF enviado a {destinatario_email}")
                return True
    except Exception as api_err:
        print(f"[BREVO API WARNING] Falló envío REST de comprobante: {api_err}. Intentando SMTP Relay...")

    # 2. Fallback por SMTP Relay de Brevo con MIMEApplication
    try:
        mail_server = os.getenv("MAIL_SERVER", "smtp-relay.brevo.com")
        mail_port = int(os.getenv("MAIL_PORT", 587))
        mail_user = os.getenv("MAIL_USERNAME")
        mail_pass = os.getenv("MAIL_PASSWORD")

        msg = MIMEMultipart()
        msg['Subject'] = f"✦ Tu {doc_label} {numero_documento} — AURA Atelier"
        msg['From'] = f"AURA Atelier <{sender_email}>"
        msg['To'] = destinatario_email

        part_html = MIMEText(html_content, 'html')
        msg.attach(part_html)

        pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=nombre_archivo)
        msg.attach(pdf_attachment)

        with smtplib.SMTP(mail_server, mail_port, timeout=12) as server:
            server.starttls()
            server.login(mail_user, mail_pass)
            server.sendmail(sender_email, [destinatario_email], msg.as_string())
            print(f"[BREVO SMTP SUCCESS] Comprobante PDF enviado exitosamente a {destinatario_email}")
            return True
    except Exception as smtp_err:
        print(f"[BREVO SMTP ERROR] No se pudo enviar comprobante por SMTP: {smtp_err}")
        return False

