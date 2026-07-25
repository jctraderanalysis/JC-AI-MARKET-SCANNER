import time
import datetime
import pytz
import requests
import config

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = getattr(config, 'TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = getattr(config, 'TELEGRAM_CHAT_ID', '')

# Control de estados para no repetir alertas
market_states = {
    "FOREX": None,
    "STOCKS": None,
    "INDICES": None
}

def send_telegram_alert(message: str):
    """Envia un mensaje directo a tu Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Token o Chat ID de Telegram no configurados.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[!] Error enviando alerta a Telegram: {e}")

def check_market_schedules():
    """Verifica aperturas y cierres de mercado en tiempo de Puerto Rico (AST)."""
    tz_ast = pytz.timezone('America/Puerto_Rico')
    now = datetime.datetime.now(tz_ast)
    weekday = now.weekday() # 0 = Lunes, 5 = Sábado, 6 = Domingo
    hour = now.hour
    minute = now.minute

    # 1. ESTADO FOREX (Abre Dom 5:00 PM - Cierra Vie 5:00 PM)
    forex_open = not (weekday == 5 or (weekday == 4 and hour >= 17) or (weekday == 6 and hour < 17))
    if market_states["FOREX"] is not None and market_states["FOREX"] != forex_open:
        if forex_open:
            send_telegram_alert("🟢 **🚨 ¡ALERTA DE APERTURA!**\n\nEl mercado de **FOREX** acaba de abrir. Iniciando escaneo de H4, H1 y M5...")
        else:
            send_telegram_alert("🔴 **💤 MERCADO CERRADO**\n\nEl mercado de **FOREX** ha cerrado por el fin de semana. No se buscarán entradas hasta el domingo 5:00 PM AST.")
    market_states["FOREX"] = forex_open

    # 2. ESTADO ACCIONES (Abre Lun-Vie 9:30 AM - Cierra 4:00 PM)
    stocks_open = not (weekday in [5, 6] or hour < 9 or (hour == 9 and minute < 30) or hour >= 16)
    if market_states["STOCKS"] is not None and market_states["STOCKS"] != stocks_open:
        if stocks_open:
            send_telegram_alert("🟢 **🚨 ¡ALERTA DE APERTURA!**\n\nLa bolsa de Wall Street (**Acciones**) acaba de abrir sus puertas. Escaneando oportunidades...")
        else:
            send_telegram_alert("🔴 **💤 MERCADO CERRADO**\n\nLa bolsa de Wall Street (**Acciones**) ha cerrado sesión por hoy.")
    market_states["STOCKS"] = stocks_open

    # 3. ESTADO ÍNDICES (Abre Dom 6:00 PM - Cierra Vie 5:00 PM)
    indices_open = not (weekday == 5 or (weekday == 4 and hour >= 17) or (weekday == 6 and hour < 18))
    if market_states["INDICES"] is not None and market_states["INDICES"] != indices_open:
        if indices_open:
            send_telegram_alert("🟢 **🚨 ¡ALERTA DE APERTURA!**\n\nEl mercado de **ÍNDICES** (S&P500 / Nasdaq) acaba de abrir.")
        else:
            send_telegram_alert("🔴 **💤 MERCADO CERRADO**\n\nEl mercado de **ÍNDICES** ha cerrado.")
    market_states["INDICES"] = indices_open

def start_background_scanner():
    """Ejecuta el monitoreo en segundo plano."""
    check_market_schedules()
