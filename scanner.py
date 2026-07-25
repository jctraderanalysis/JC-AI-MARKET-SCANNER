def analyze_symbol_full(symbol: str):
    """Analiza H4, H1 y M5 evaluando precio real vs medias en H4."""
    # 1. Obtener H4 directo / resampled
    df_h1_raw = fetch_data(symbol, "1h", "30d")
    df_m5 = fetch_data(symbol, "5m", "2d")

    if df_h1_raw is None or df_m5 is None or df_m5.empty:
        return None

    # Resamplear H4 correctamente
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

    # EVALUACIÓN REAL DE H4 (Precio + EMAs + RSI)
    if len(df_h4) > 10:
        row_h4 = df_h4.iloc[-1]
        p_h4 = row_h4['Close']
        ema_f_h4 = row_h4['EMA_FAST']
        ema_m_h4 = row_h4['EMA_MID']
        rsi_h4 = row_h4['RSI']

        # Si el precio en H4 está por DEBAJO de las medias o el RSI H4 < 50, NO puede ser alcista
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

    # Estado H1 (Pierna)
    row_h1 = df_h1_raw.iloc[-1]
    if row_h1['EMA_FAST'] > row_h1['EMA_MID'] > row_h1['EMA_SLOW']:
        h1_status = "🟢 Pierna Alcista"
    elif row_h1['EMA_FAST'] < row_h1['EMA_MID'] < row_h1['EMA_SLOW']:
        h1_status = "🔴 Pierna Bajista"
    else:
        h1_status = "🟡 Corrección"

    # Estado M5 (Gatillo)
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
