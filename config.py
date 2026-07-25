# ==========================================
# JC AI MARKET SCANNER PRO - CONFIGURACIÓN
# Copyright 2026, JESUS CRUZ
# ==========================================

# TELEGRAM BOT CONFIG
TELEGRAM_TOKEN = "8864661105:AAHIrGuPdMD2k3m387OYQeG9NMzDSSUzMMk"  # El token HTTP API que te dio BotFather
TELEGRAM_CHAT_ID = "8200473209"         # Tu ID personal o ID del grupo/canal

# CONFIGURACIÓN DE CORREO (SMTP)
ENABLE_EMAIL = True
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "tu_correo@gmail.com"
EMAIL_PASSWORD = "tu_app_password_de_gmail"  # Contraseña de aplicación
EMAIL_RECEIVER = "tu_correo@gmail.com"

# LISTA DE SÍMBOLOS (Formato Yahoo Finance)
SYMBOLS = {
    "FOREX": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"],
    "CRYPTO": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"],
    "METALS_INDICES": ["GC=F", "SI=F", "^GSPC", "^DJI", "^IXIC"],
    "STOCKS": ["AAPL", "TSLA", "NVDA", "AMZN", "MSFT"]
}

# TEMPORALIDADES
USE_M5 = True   # GATILLO
USE_H1 = True   # CONFIRMACIÓN TENDENCIA
USE_H4 = True   # CONFIRMACIÓN TENDENCIA MAYOR

# INDICADORES TÉCNICOS
EMA_FAST = 30
EMA_MID = 50
EMA_SLOW = 100

RSI_PERIOD = 14
RSI_BUY_LEVEL = 50.0
RSI_SELL_LEVEL = 50.0

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# INTERVALO DE ESCANEO (en segundos)
SCAN_INTERVAL_SECONDS = 300  # 5 minutos para respetar límites de yfinance