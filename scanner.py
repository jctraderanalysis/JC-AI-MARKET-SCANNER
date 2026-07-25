import yfinance as yf
import pandas as pd
import ta
import config

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
        "RSI_VAL": rsi_val,
        "MACD_HIST": macd_hist
    }

def generate_ai_report(symbol: str, _unused_key=None):
    """Genera un Informe Ejecutivo Técnico Inteligente 100% nativo sin depender de APIs externas."""
    info = analyze_symbol_full(symbol)
    if not info:
        return "❌ No se pudieron obtener datos suficientes para generar el informe técnico."

    price = info['Precio']
    h1 = info['Estructura H1']
    m5 = info['Estructura M5']
    rsi_text = info['RSI (M5)']
    rsi_val = info['RSI_VAL']
    macd_text = info['MACD (M5)']
    macd_hist = info['MACD_HIST']

    # Lógica de Sesgo
    if "🟢" in h1 and "🟢" in m5:
        bias = "🟢 COMPRA (ALTA PROBABILIDAD)"
        confidence = "88% - 94%"
        action = "Buscar gatillo de entrada en M5 al toque o retroceso de la EMA 30/50."
        sl_zone = "Por debajo del último mínimo estructural en M5."
    elif "🔴" in h1 and "🔴" in m5:
        bias = "🔴 VENTA (ALTA PROBABILIDAD)"
        confidence = "88% - 94%"
        action = "Buscar gatillo de entrada en corta al retest de la EMA 30 en M5."
        sl_zone = "Por encima del último máximo estructural en M5."
    elif "🟢" in h1 and "🔴" in m5:
        bias = "🟡 ESPERAR / RETROCESO"
        confidence = "60%"
        action = "Tendencia mayor H1 es Alcista pero M5 está corrigiendo. Esperar que M5 vuelva a alinearse alcista."
        sl_zone = "N/A - Espere confirmación de gatillo."
    elif "🔴" in h1 and "🟢" in m5:
        bias = "🟡 ESPERAR / CORRECCIÓN"
        confidence = "60%"
        action = "Tendencia mayor H1 es Bajista pero M5 hace pullback. No operar contra tendencia H1."
        sl_zone = "N/A - Espere alineación en M5."
    else:
        bias = "⚪ MERCADO EN RANGO / NEUTRO"
        confidence = "50%"
        action = "El activo no muestra alineación en EMAs. Mantenerse al margen."
        sl_zone = "N/A"

    report = f"""
### 🤖 JC AI TRADER REPORT — {symbol}
*Copyright 2026, JESUS CRUZ*

---

#### 📌 **1. Resumen Ejecutivo & Sesgo del Mercado**
* **Precio Actual:** `{price}`
* **Sesgo Técnico:** **{bias}**
* **Nivel de Confianza:** `{confidence}`

---

#### 📊 **2. Análisis Multitemporal (MTF)**
* **Estructura H1:** **{h1}** — *Determina la dirección mayor.*
* **Estructura M5:** **{m5}** — *Alineación de EMAs (30, 50, 100) en temporalidad de gatillo.*

---

#### 📈 **3. Momentum & Osciladores**
* **RSI (M5):** `{rsi_text}` — {'Fuerza alcista sostenida' if rsi_val > 50 else 'Presión bajista activa'}.
* **MACD Histograma (M5):** `{macd_text}` (`{round(macd_hist, 6)}`) — {'Convergencia a favor del movimiento' if macd_hist > 0 else 'Fuerza vendedora superior'}.

---

#### 🎯 **4. Plan Operativo y Gestión de Riesgo**
* **Recomendación:** {action}
* **Zona Invalidez / Stop Loss:** {sl_zone}
    """
    return report

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
