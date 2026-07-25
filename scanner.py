import yfinance as yf
import pandas as pd
import ta
import config
import google.generativeai as genai

def fetch_data(symbol: str, timeframe: str, period: str = "5d"):
    """Obtiene datos de yfinance y calcula indicadores."""
    try:
        df = yf.download(tickers=symbol, period=period, interval=timeframe, progress=False)
        if df.empty or len(df) < 30:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        ema_f = getattr(config, 'EMA_FAST', 30)
        ema_m = getattr(config, 'EMA_MID', 50)
        ema_s = getattr(config, 'EMA_SLOW', 100)

        df['EMA_FAST'] = ta.trend.ema_indicator(df['Close'], window=ema_f)
        df['EMA_MID'] = ta.trend.ema_indicator(df['Close'], window=ema_m)
        df['EMA_SLOW'] = ta.trend.ema_indicator(df['Close'], window=ema_s)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=getattr(config, 'RSI_PERIOD', 14))

        macd_obj = ta.trend.MACD(
            close=df['Close'],
            window_slow=getattr(config, 'MACD_SLOW', 26),
            window_fast=getattr(config, 'MACD_FAST', 12),
            window_sign=getattr(config, 'MACD_SIGNAL', 9)
        )
        df['MACD'] = macd_obj.macd()
        df['MACD_SIGNAL'] = macd_obj.macd_signal()
        df['MACD_HIST'] = macd_obj.macd_diff()

        return df
    except Exception as e:
        print(f"[!] Error descargando {symbol} en {timeframe}: {e}")
        return None

def analyze_symbol_full(symbol: str):
    """Analiza H1 y M5 para la tabla multitemporal."""
    df_h1 = fetch_data(symbol, "1h", "7d")
    df_m5 = fetch_data(symbol, "5m", "1d")

    if df_m5 is None or df_m5.empty:
        return None

    row_m5 = df_m5.iloc[-1]
    price = round(float(row_m5['Close']), 4)
    rsi_val = round(float(row_m5['RSI']), 2) if pd.notnull(row_m5['RSI']) else 50.0
    macd_hist = float(row_m5['MACD_HIST']) if pd.notnull(row_m5['MACD_HIST']) else 0.0

    if row_m5['EMA_FAST'] > row_m5['EMA_MID'] > row_m5['EMA_SLOW']:
        ema_m5_status = "🟢 Alcista"
    elif row_m5['EMA_FAST'] < row_m5['EMA_MID'] < row_m5['EMA_SLOW']:
        ema_m5_status = "🔴 Bajista"
    else:
        ema_m5_status = "🟡 Neutro / Mapeo"

    if df_h1 is not None and not df_h1.empty:
        row_h1 = df_h1.iloc[-1]
        if row_h1['EMA_FAST'] > row_h1['EMA_MID']:
            h1_status = "🟢 Alcista"
        elif row_h1['EMA_FAST'] < row_h1['EMA_MID']:
            h1_status = "🔴 Bajista"
        else:
            h1_status = "🟡 Neutro"
    else:
        h1_status = "⚪ N/A"

    if macd_hist > 0:
        macd_status = "🟢 Positivo"
    elif macd_hist < 0:
        macd_status = "🔴 Negativo"
    else:
        macd_status = "⚪ Neutro"

    if rsi_val >= 70:
        rsi_status = f"🔴 Sobrecompra ({rsi_val})"
    elif rsi_val <= 30:
        rsi_status = f"🟢 Sobreventa ({rsi_val})"
    elif rsi_val > 50:
        rsi_status = f"🟢 Alcista ({rsi_val})"
    else:
        rsi_status = f"🔴 Bajista ({rsi_val})"

    return {
        "Símbolo": symbol,
        "Precio": price,
        "Estructura H1": h1_status,
        "Estructura M5": ema_m5_status,
        "RSI (M5)": rsi_status,
        "MACD (M5)": macd_status,
    }

def generate_ai_report(symbol: str, api_key: str):
    """Envía los datos técnicos a Gemini para redactar un informe profesional de IA."""
    info = analyze_symbol_full(symbol)
    if not info:
        return "❌ No se pudieron obtener datos técnicos suficientes para generar el reporte de IA."

    prompt = f"""
    Eres el asistente oficial de análisis de trading para 'JC AI MARKET SCANNER PRO' (Copyright 2026, JESUS CRUZ).
    Genera un informe técnico ejecutivo y detallado para el activo: {symbol}.

    DATOS TÉCNICOS EN TIEMPO REAL:
    - Precio Actual: {info['Precio']}
    - Estructura Tendencial H1: {info['Estructura H1']}
    - Estructura Tendencial M5: {info['Estructura M5']}
    - Lectura de RSI (M5): {info['RSI (M5)']}
    - Lectura de MACD (M5): {info['MACD (M5)']}

    ESTRUCTURA DEL REPORTE SOLICITADO:
    1. 📌 **Resumen Ejecutivo**: Sesgo actual (COMPRA, VENTA o ESPERAR) y nivel de confianza.
    2. 📊 **Análisis Multitemporal (MTF)**: Evaluación de alineación entre H1 y M5 (EMAs 30, 50, 100).
    3. 📈 **Momentum y Osciladores**: Análisis de convergencia/divergencia entre RSI y MACD.
    4. 🎯 **Plan Operativo y Gestión de Riesgo**: Puntos clave de entrada, zonas de invalidez (Stop Loss) y objetivos probables.

    Utiliza un tono profesional, claro, bien formateado con viñetas y emojis.
    """

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error al conectar con la IA de Gemini: {e}"

def analyze_symbol(symbol: str):
    df_h1 = fetch_data(symbol, "1h", "7d")
    df_m5 = fetch_data(symbol, "5m", "1d")

    if df_h1 is None or df_m5 is None:
        return None

    row_m5 = df_m5.iloc[-2]
    prev_m5 = df_m5.iloc[-3]
    row_h1 = df_h1.iloc[-2]

    price = float(row_m5['Close'])

    h1_bull = row_h1['EMA_FAST'] > row_h1['EMA_MID'] > row_h1['EMA_SLOW']
    m5_bull_ema = row_m5['EMA_FAST'] > row_m5['EMA_MID'] > row_m5['EMA_SLOW']
    m5_bull_rsi = row_m5['RSI'] > 50
    m5_bull_macd = (row_m5['MACD_HIST'] > 0) and (row_m5['MACD_HIST'] > prev_m5['MACD_HIST'])

    if h1_bull and m5_bull_ema and m5_bull_rsi and m5_bull_macd:
        return {
            "symbol": symbol, "type": "COMPRA", "price": round(price, 4),
            "confidence": 92, "rsi": round(float(row_m5['RSI']), 2),
            "reason": "Alineación MTF Alcista Completa"
        }

    h1_bear = row_h1['EMA_FAST'] < row_h1['EMA_MID'] < row_h1['EMA_SLOW']
    m5_bear_ema = row_m5['EMA_FAST'] < row_m5['EMA_MID'] < row_m5['EMA_SLOW']
    m5_bear_rsi = row_m5['RSI'] < 50
    m5_bear_macd = (row_m5['MACD_HIST'] < 0) and (row_m5['MACD_HIST'] < prev_m5['MACD_HIST'])

    if h1_bear and m5_bear_ema and m5_bear_rsi and m5_bear_macd:
        return {
            "symbol": symbol, "type": "VENTA", "price": round(price, 4),
            "confidence": 92, "rsi": round(float(row_m5['RSI']), 2),
            "reason": "Alineación MTF Bajista Completa"
        }

    return None
