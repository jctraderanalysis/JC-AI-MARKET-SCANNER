import yfinance as yf
import pandas as pd
import ta
import config

def fetch_data(symbol: str, timeframe: str, period: str = "5d"):
    """Obtiene datos de yfinance y calcula indicadores usando la librería ta."""
    try:
        df = yf.download(tickers=symbol, period=period, interval=timeframe, progress=False)
        if df.empty or len(df) < config.EMA_SLOW + 5:
            return None

        # Limpieza de MultiIndex si yfinance lo genera
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Cálculo de EMAs con ta
        df['EMA_30'] = ta.trend.ema_indicator(df['Close'], window=config.EMA_FAST)
        df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=config.EMA_MID)
        df['EMA_100'] = ta.trend.ema_indicator(df['Close'], window=config.EMA_SLOW)

        # Cálculo de RSI con ta
        df['RSI'] = ta.momentum.rsi(df['Close'], window=config.RSI_PERIOD)

        # Cálculo de MACD con ta
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
