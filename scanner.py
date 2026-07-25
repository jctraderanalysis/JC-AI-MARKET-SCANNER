import yfinance as yf
import pandas as pd
import ta
import config

def fetch_data(symbol: str, timeframe: str, period: str = "5d"):
    """Obtiene datos de yfinance y calcula indicadores con la librería 'ta'."""
    try:
        df = yf.download(tickers=symbol, period=period, interval=timeframe, progress=False)
        if df.empty or len(df) < config.EMA_SLOW + 5:
            return None

        # Limpieza de MultiIndex si yfinance lo genera
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Cálculo de EMAs
        df['EMA_30'] = ta.trend.ema_indicator(df['Close'], window=config.EMA_FAST)
        df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=config.EMA_MID)
        df['EMA_100'] = ta.trend.ema_indicator(df['Close'], window=config.EMA_SLOW)

        # Cálculo de RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=config.RSI_PERIOD)

        # Cálculo de MACD
        macd_obj = ta.trend.MACD(
            close=df['Close'],
            window_slow=config.MACD_SLOW,
            window_fast=config.MACD_FAST,
            window_sign=config.MACD_SIGNAL
        )
        df['MACD'] = macd_obj.macd()
        df['MACD_SIGNAL'] = macd_obj.macd_signal()
        df['MACD_HIST'] = macd_obj.macd_diff()

        return df
    except Exception as e:
        print(f"[!] Error descargando {symbol} en {timeframe}: {e}")
        return None

def analyze_symbol(symbol: str):
    """
    Evalúa la triple confirmación (H1, M5).
    Retorna la señal ('COMPRA', 'VENTA' o None) y la información técnica asociada.
    """
    df_h1 = fetch_data(symbol, "1h", "7d")
    df_m5 = fetch_data(symbol, "5m", "1d")

    if df_h1 is None or df_m5 is None:
        return None

    # Última vela cerrada (shift=1)
    row_m5 = df_m5.iloc[-2]
    prev_m5 = df_m5.iloc[-3]
    row_h1 = df_h1.iloc[-2]

    price = float(row_m5['Close'])

    # --- CONDICIONES DE COMPRA ---
    h1_bull = row_h1['EMA_30'] > row_h1['EMA_50'] > row_h1['EMA_100']
    m5_bull_ema = row_m5['EMA_30'] > row_m5['EMA_50'] > row_m5['EMA_100']
    m5_bull_rsi = row_m5['RSI'] > config.RSI_BUY_LEVEL
    m5_bull_macd = (row_m5['MACD_HIST'] > 0) and (row_m5['MACD_HIST'] > prev_m5['MACD_HIST'])
    m5_bull_price = price > row_m5['EMA_30']

    if h1_bull and m5_bull_ema and m5_bull_rsi and m5_bull_macd and m5_bull_price:
        return {
            "symbol": symbol,
            "type": "COMPRA",
            "price": round(price, 4),
            "confidence": 92,
            "rsi": round(float(row_m5['RSI']), 2),
            "reason": "EMA30>EMA50>EMA100 | RSI>50 | MACD Hist creciente"
        }

    # --- CONDICIONES DE VENTA ---
    h1_bear = row_h1['EMA_30'] < row_h1['EMA_50'] < row_h1['EMA_100']
    m5_bear_ema = row_m5['EMA_30'] < row_m5['EMA_50'] < row_m5['EMA_100']
    m5_bear_rsi = row_m5['RSI'] < config.RSI_SELL_LEVEL
    m5_bear_macd = (row_m5['MACD_HIST'] < 0) and (row_m5['MACD_HIST'] < prev_m5['MACD_HIST'])
    m5_bear_price = price < row_m5['EMA_30']

    if h1_bear and m5_bear_ema and m5_bear_rsi and m5_bear_macd and m5_bear_price:
        return {
            "symbol": symbol,
            "type": "VENTA",
            "price": round(price, 4),
            "confidence": 92,
            "rsi": round(float(row_m5['RSI']), 2),
            "reason": "EMA30<EMA50<EMA100 | RSI<50 | MACD Hist decreciente"
        }

    return None
