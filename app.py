import streamlit as st
import pandas as pd
import datetime
import pytz
import main
import config
from scanner import fetch_data

st.set_page_config(page_title="JC AI MARKET SCANNER PRO", page_icon="📈", layout="wide")

st.title("🚀 JC AI MARKET SCANNER PRO")
st.caption("Copyright 2026, JESUS CRUZ")

# Inicia el escáner en segundo plano
main.start_background_scanner()

# Obtener hora actual en Puerto Rico (AST)
tz_ast = pytz.timezone('America/Puerto_Rico')
now_ast = datetime.datetime.now(tz_ast)
weekday = now_ast.weekday() # 0: Lunes, 5: Sábado, 6: Domingo
hour = now_ast.hour

st.write(f"🕒 **Hora actual (Puerto Rico):** {now_ast.strftime('%Y-%m-%d %I:%M:%S %p AST')}")

# Funciones de verificación de mercado abierto/cerrado
def is_crypto_open():
    return True # 24/7

def is_forex_open():
    # Cierra Viernes ~5 PM AST, Abre Domingo 5 PM AST
    if weekday == 5: # Sábado
        return False
    if weekday == 4 and hour >= 17: # Viernes tarde
        return False
    if weekday == 6 and hour < 17: # Domingo antes de las 5 PM
        return False
    return True

def is_indices_open():
    # Cierra Viernes ~5 PM AST, Abre Domingo 6 PM AST
    if weekday == 5:
        return False
    if weekday == 4 and hour >= 17:
        return False
    if weekday == 6 and hour < 18:
        return False
    return True

def is_stocks_open():
    # Lunes a Viernes 9:30 AM a 4:00 PM AST
    if weekday in [5, 6]: # Fin de semana
        return False
    if hour < 9 or (hour == 9 and now_ast.minute < 30) or hour >= 16:
        return False
    return True

# Función para construir la tabla de datos
def build_market_table(symbols):
    data = []
    for sym in symbols:
        df = fetch_data(sym, "5m", "1d")
        if df is not None and not df.empty:
            row = df.iloc[-1]
            price = round(float(row['Close']), 4)
            rsi = round(float(row['RSI']), 2)
            ema30 = round(float(row['EMA_30']), 4)
            trend = "🟢 Alcista" if price > ema30 else "🔴 Bajista"
            
            data.append({
                "Símbolo": sym,
                "Precio Actual": price,
                "RSI (M5)": rsi,
                "EMA 30": ema30,
                "Tendencia M5": trend
            })
    return pd.DataFrame(data) if data else None

st.markdown("---")

# Crear pestañas independientes
tab_crypto, tab_forex, tab_stocks, tab_indices = st.tabs([
    "🪙 Criptomonedas", 
    "💱 Forex", 
    "📊 Acciones", 
    "📈 Índices"
])

# --- PESTAÑA CRIPTO ---
with tab_crypto:
    st.subheader("🪙 Criptomonedas")
    st.success("🟢 MERCADO ABIERTO 24/7 — Cotizando y escaneando en tiempo real")
    syms_crypto = config.SYMBOLS.get("CRYPTO", ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"])
    df_crypto = build_market_table(syms_crypto)
    if df_crypto is not None:
        st.dataframe(df_crypto, use_container_width=True)
    else:
        st.info("Cargando datos de Criptomonedas...")

# --- PESTAÑA FOREX ---
with tab_forex:
    st.subheader("💱 Forex")
    if is_forex_open():
        st.success("🟢 MERCADO ABIERTO — Escaneando divisas en tiempo real")
        syms_forex = config.SYMBOLS.get("FOREX", ["EURUSD=X", "GBPUSD=X", "AUDUSD=X"])
        df_forex = build_market_table(syms_forex)
        if df_forex is not None:
            st.dataframe(df_forex, use_container_width=True)
    else:
        st.error("🔴 MERCADO CERRADO — Abre el Domingo a las 5:00 PM (Hora de Puerto Rico / AST)")

# --- PESTAÑA ACCIONES ---
with tab_stocks:
    st.subheader("📊 Acciones Wall Street")
    if is_stocks_open():
        st.success("🟢 MERCADO ABIERTO — Escaneando acciones en tiempo real")
        syms_stocks = config.SYMBOLS.get("STOCKS", ["NVDA", "TSLA", "AAPL", "AMZN"])
        df_stocks = build_market_table(syms_stocks)
        if df_stocks is not None:
            st.dataframe(df_stocks, use_container_width=True)
    else:
        st.error("🔴 MERCADO CERRADO — Abre el Lunes a las 9:30 AM (Hora de Puerto Rico / AST)")

# --- PESTAÑA ÍNDICES ---
with tab_indices:
    st.subheader("📈 Índices")
    if is_indices_open():
        st.success("🟢 MERCADO ABIERTO — Escaneando índices en tiempo real")
        syms_indices = config.SYMBOLS.get("INDICES", ["^GSPC", "^DJI", "^IXIC"])
        df_indices = build_market_table(syms_indices)
        if df_indices is not None:
            st.dataframe(df_indices, use_container_width=True)
    else:
        st.error("🔴 MERCADO CERRADO — Abre el Domingo a las 6:00 PM (Hora de Puerto Rico / AST)")
