import streamlit as st
import pandas as pd
import datetime
import pytz
import main
import config
from scanner import analyze_symbol_full

st.set_page_config(page_title="JC AI MARKET SCANNER PRO", page_icon="📈", layout="wide")

st.title("🚀 JC AI MARKET SCANNER PRO")
st.caption("Copyright 2026, JESUS CRUZ")

main.start_background_scanner()

tz_ast = pytz.timezone('America/Puerto_Rico')
now_ast = datetime.datetime.now(tz_ast)
weekday = now_ast.weekday()
hour = now_ast.hour

st.write(f"🕒 **Hora actual (Puerto Rico):** {now_ast.strftime('%Y-%m-%d %I:%M:%S %p AST')}")

def is_crypto_open(): return True
def is_forex_open(): return not (weekday == 5 or (weekday == 4 and hour >= 17) or (weekday == 6 and hour < 17))
def is_indices_open(): return not (weekday == 5 or (weekday == 4 and hour >= 17) or (weekday == 6 and hour < 18))
def is_stocks_open(): return not (weekday in [5, 6] or hour < 9 or (hour == 9 and now_ast.minute < 30) or hour >= 16)

# Función para dar formato de colores a las celdas
def style_dataframe(df):
    def highlight_status(val):
        if "🟢" in str(val):
            return "background-color: #d4edda; color: #155724; font-weight: bold;"
        elif "🔴" in str(val):
            return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
        elif "🟡" in str(val):
            return "background-color: #fff3cd; color: #856404; font-weight: bold;"
        return ""

    return df.style.applymap(highlight_status, subset=["Estructura H1", "Estructura M5", "RSI (M5)", "MACD (M5)"])

def build_market_table(symbols):
    data = []
    for sym in symbols:
        info = analyze_symbol_full(sym)
        if info:
            data.append(info)
    if data:
        df = pd.DataFrame(data)
        return style_dataframe(df)
    return None

st.markdown("---")

tab_crypto, tab_forex, tab_stocks, tab_indices = st.tabs(["🪙 Criptomonedas", "💱 Forex", "📊 Acciones", "📈 Índices"])

with tab_crypto:
    st.subheader("🪙 Criptomonedas (Alineación Multitemporal)")
    st.success("🟢 MERCADO ABIERTO 24/7")
    syms_crypto = config.SYMBOLS.get("CRYPTO", ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"])
    df_crypto = build_market_table(syms_crypto)
    if df_crypto is not None:
        st.dataframe(df_crypto, use_container_width=True)

with tab_forex:
    st.subheader("💱 Forex")
    if is_forex_open():
        syms_forex = config.SYMBOLS.get("FOREX", ["EURUSD=X", "GBPUSD=X", "AUDUSD=X"])
        df_forex = build_market_table(syms_forex)
        if df_forex is not None:
            st.dataframe(df_forex, use_container_width=True)
    else:
        st.error("🔴 MERCADO CERRADO — Abre el Domingo a las 5:00 PM AST")

with tab_stocks:
    st.subheader("📊 Acciones")
    if is_stocks_open():
        syms_stocks = config.SYMBOLS.get("STOCKS", ["NVDA", "TSLA", "AAPL"])
        df_stocks = build_market_table(syms_stocks)
        if df_stocks is not None:
            st.dataframe(df_stocks, use_container_width=True)
    else:
        st.error("🔴 MERCADO CERRADO — Abre el Lunes a las 9:30 AM AST")

with tab_indices:
    st.subheader("📈 Índices")
    if is_indices_open():
        syms_indices = config.SYMBOLS.get("INDICES", ["^GSPC", "^DJI"])
        df_indices = build_market_table(syms_indices)
        if df_indices is not None:
            st.dataframe(df_indices, use_container_width=True)
    else:
        st.error("🔴 MERCADO CERRADO — Abre el Domingo a las 6:00 PM AST")
