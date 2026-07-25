import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def send_telegram_msg(message: str):
    """Envía un mensaje al bot de Telegram."""
    if not config.TELEGRAM_TOKEN or config.TELEGRAM_TOKEN == "AQUI_PEGA_EL_TOKEN_DE_BOTFATHER":
        print("[!] Token de Telegram no configurado.")
        return

    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"[!] Error enviando mensaje a Telegram: {response.text}")
    except Exception as e:
        print(f"[!] Excepción en Telegram: {e}")

def send_email_report(subject: str, body_text: str):
    """Envía reporte por correo electrónico."""
    if not config.ENABLE_EMAIL:
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = config.EMAIL_SENDER
        msg['To'] = config.EMAIL_RECEIVER
        msg['Subject'] = subject

        msg.attach(MIMEText(body_text, 'plain'))

        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("[+] Correo enviado con éxito.")
    except Exception as e:
        print(f"[!] Error al enviar correo: {e}")

def notify_startup():
    """Alerta inicial al arrancar el scanner."""
    msg = (
        "<b>🚀 JC AI MARKET SCANNER PRO ACTIVADO</b>\n"
        "<i>Copyright 2026, JESUS CRUZ</i>\n\n"
        "✅ Escáner iniciado correctamente.\n"
        "🔍 Analizando mercados en segundo plano 24/7..."
    )
    send_telegram_msg(msg)
    send_email_report(
        "EA ACTIVADO EMPEZANDO A ESCANEAR",
        "JC AI MARKET SCANNER PRO iniciado.\nCopyright 2026, JESUS CRUZ\nEmpezando escaneo de mercados."
    )