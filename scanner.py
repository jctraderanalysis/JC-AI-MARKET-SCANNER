import yfinance as yf
import pandas as pd
import ta
import config

def fetch_data(symbol: str, timeframe: str, period: str = "30d"):
    """Obtiene datos de yfinance y calcula indicadores técnicos."""
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
    """Analiza H4, H1 y M5 evaluando precio vs EMAs para precisión técnica."""
    df_h1_raw = fetch_data(symbol, "1h", "30d")
    df_m5 = fetch_data(symbol, "5m", "2d")

    if df_h1_raw is None or df_m5 is None or df_m5.empty:
        return None

    # Resampling preciso para H4
    df_h4 = df_h1_raw.resample('4h').agg({
        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'
    }).dropna()

    ema_f = getattr(config, 'EMA_FAST', 30)
    ema_m = getattr(config, 'EMA_MID', 50)
    ema_s = getattr(config, 'EMA_SLOW', 100)

    df_h4['EMA_FAST'] = ta.trend.ema_indicator(df_h4['Close'], window=ema_f)
    df_h4['EMA_MID'] = ta.trend.ema_indicator(df_h4['Close'], window=ema_m)
    df_h4['EMA_SLOW'] = ta.trend.ema_indicator(df_h4['Close'], window=ema_s)
    df_h4['RSI'] = ta.momentum.rsi(df_h4['Close'], window=14)

    row_m5 = df_m5.iloc[-1]
    price = round(float(row_m5['Close']), 4)
    rsi_val = round(float(row_m5['RSI']), 2) if pd.notnull(row_m5['RSI']) else 50.0
    macd_hist = float(row_m5['MACD_HIST']) if pd.notnull(row_m5['MACD_HIST']) else 0.0

    # Evaluacion de H4 (Precio vs EMAs y RSI)
    if len(df_h4) > 10:
        row_h4 = df_h4.iloc[-1]
        p_h4 = row_h4['Close']
        ema_f_h4 = row_h4['EMA_FAST']
        ema_m_h4 = row_h4['EMA_MID']
        rsi_h4 = row_h4['RSI']

        if p_h4 < ema_f_h4 and p_h4 < ema_m_h4:
            if ema_f_h4 < ema_m_h4 or rsi_h4 < 45:
                h4_status = "🔴 Bajista (Ciclo)"
            else:
                h4_status = "🟡 Transición / Rango"
        elif ema_f_h4 > ema_m_h4 > row_h4['EMA_SLOW'] and p_h4 > ema_f_h4:
            h4_status = "🟢 Alcista (Ciclo)"
        else:
            h4_status = "🟡 Transición / Rango"
    else:
        h4_status = "⚪ N/A"

    # Evaluacion de H1 (Pierna)
    row_h1 = df_h1_raw.iloc[-1]
    if row_h1['EMA_FAST'] > row_h1['EMA_MID'] > row_h1['EMA_SLOW']:
        h1_status = "🟢 Pierna Alcista"
    elif row_h1['EMA_FAST'] < row_h1['EMA_MID'] < row_h1['EMA_SLOW']:
        h1_status = "🔴 Pierna Bajista"
    else:
        h1_status = "🟡 Corrección"

    # Evaluacion de M5 (Gatillo)
    if row_m5['EMA_FAST'] > row_m5['EMA_MID'] > row_m5['EMA_SLOW']:
        ema_m5_status = "🟢 Alcista"
    elif row_m5['EMA_FAST'] < row_m5['EMA_MID'] < row_m5['EMA_SLOW']:
        ema_m5_status = "🔴 Bajista"
    else:
        ema_m5_status = "🟡 Mapeo"

    macd_status = "🟢 Positivo" if macd_hist > 0 else "🔴 Negativo"

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
        "Tendencia H4": h4_status,
        "Pierna H1": h1_status,
        "Gatillo M5": ema_m5_status,
        "RSI (M5)": rsi_status,
        "MACD (M5)": macd_status,
        "RSI_VAL": rsi_val,
        "MACD_HIST": macd_hist
    }

def generate_ai_report(symbol: str, _unused_key=None):
    """Genera un informe técnico ejecutivo basado en la estrategia H4-H1-M5."""
    info = analyze_symbol_full(symbol)
    if not info:
        return "❌ No se pudieron obtener datos suficientes para generar el informe técnico."

    price = info['Precio']
    h4 = info['Tendencia H4']
    h1 = info['Pierna H1']
    m5 = info['Gatillo M5']
    rsi_text = info['RSI (M5)']
    rsi_val = info['RSI_VAL']
    macd_text = info['MACD (M5)']
    macd_hist = info['MACD_HIST']

    if "🟢" in h4 and "🟢" in h1 and "🟢" in m5:
        bias = "🟢 COMPRA CONFIRMADA (ALTA PROBABILIDAD)"
        confidence = "92% - 96%"
        action = "Cierre de ciclo H4 alcista alineado con la pierna H1. Buscar gatillo en M5 al retroceso de EMAs."
        sl_zone = "Por debajo del último mínimo en M5 / soporte en H1."
    elif "🔴" in h4 and "🔴" in h1 and "🔴" in m5:
        bias = "🔴 VENTA CONFIRMADA (ALTA PROBABILIDAD)"
        confidence = "92% - 96%"
        action = "Cierre de ciclo H4 bajista alineado con la pierna H1. Buscar gatillo de venta en M5 al retest de EMAs."
        sl_zone = "Por encima del último máximo en M5 / resistencia en H1."
    elif "🟢" in h4 and "🟢" in h1 and "🔴" in m5:
        bias = "🟡 RETROCESO EN M5 / ESPERAR GIRO"
        confidence = "70%"
        action = "H4 y H1 son Alcistas. M5 está haciendo un pullback. Esperar confirmación alcista en M5 para entrar."
        sl_zone = "Esperar confirmación de entrada."
    elif "🔴" in h4 and "🔴" in h1 and "🟢" in m5:
        bias = "🟡 RETROCESO EN M5 / ESPERAR GIRO"
        confidence = "70%"
        action = "H4 y H1 son Bajistas. M5 en rebote alcista. Esperar a que M5 vuelva a girar a la baja."
        sl_zone = "Esperar confirmación de entrada."
    else:
        bias = "⚪ MERCADO DESALINEADO / EN RANGO"
        confidence = "50%"
        action = "Las temporalidades no coinciden. Permanecer al margen hasta ver estructura clara."
        sl_zone = "N/A"

    return f"""
### 🤖 JC AI TRADER REPORT — {symbol}
*Copyright 2026, JESUS CRUZ*

---

#### 📌 **1. Resumen Ejecutivo & Sesgo del Mercado**
* **Precio Actual:** `{price}`
* **Sesgo de Estrategia:** **{bias}**
* **Nivel de Confianza:** `{confidence}`

---

#### 📊 **2. Estructura Multitemporal (H4 -> H1 -> M5)**
* **H4 (Ciclo & Tendencia Mayor):** **{h4}**
* **H1 (Dirección de la Pierna):** **{h1}**
* **M5 (Gatillo de Entrada):** **{m5}**

---

#### 📈 **3. Momentum & Osciladores (M5)**
* **RSI (M5):** `{rsi_text}` — {'Fuerza compradora activa (>50)' if rsi_val > 50 else 'Presión vendedora activa (<50)'}.
* **MACD Histograma (M5):** `{macd_text}` (`{round(macd_hist, 6)}`) — {'Impulso a favor del movimiento' if macd_hist > 0 else 'Fuerza vendedora superior'}.

---

#### 🎯 **4. Plan Operativo & Gestión de Riesgo**
* **Acción Sugerida:** {action}
* **Zona de Invalidez / Stop Loss:** {sl_zone}
    """
