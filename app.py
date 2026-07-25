import streamlit as st
import pandas as pd
import datetime
import pytz
import main
import config
from scanner import analyze_symbol_full, generate_ai_report

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

def style_dataframe(df):
    def highlight_status(val):
        val_str = str(val)
        if "🟢" in val_str:
            return "background-color: #d4edda; color: #155724; font-weight: bold;"
        elif "🔴" in val_str:
            return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
        elif "🟡" in val_str:
            return "background-color: #fff3cd; color: #856404; font-weight: bold;"
        return ""

    try:
        styler = df.style.map(highlight_status, subset=["Estructura H1", "Estructura M5", "RSI (M5)", "MACD (M5)"])
    except AttributeError:
        styler = df.style.applymap(highlight_status, subset=["Estructura H1", "Estructura M5", "RSI (M5)", "MACD (M5)"])
    return styler

def render_market_section(title, symbols, open_status, closed_msg):
    st.subheader(title)
    if open_status:
        st.success("🟢 MERCADO ABIERTO")
        data = []
        for sym in symbols:
            info = analyze_symbol_full(sym)
            if info:
                # Filtrar solo las columnas visibles para la tabla
                data.append({
                    "Símbolo": info["Símbolo"],
                    "Precio": info["Precio"],
                    "Estructura H1": info["Estructura H1"],
                    "Estructura M5": info["Estructura M5"],
                    "RSI (M5)": info["RSI (M5)"],
                    "MACD (M5)": info["MACD (M5)"]
                })
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(style_dataframe(df), use_container_width=True)

            st.markdown("#### 🤖 Generar Informe Ejecutivo con IA Integrada")
            col1, col2 = st.columns([2, 1])
            with col1:
                selected_sym = st.selectbox(f"Selecciona un activo de {title}:", symbols, key=f"select_{title}")
            with col2:
                st.write("")
                st.write("")
                btn_gen = st.button(f"🤖 Analizar {selected_sym} con IA", key=f"btn_{title}")

            if btn_gen:
                with st.spinner(f"Analizando la estructura multitemporal de {selected_sym}..."):
                    report = generate_ai_report(selected_sym)
                    st.markdown("---")
                    st.info(report)
    else:
        st.error(f"🔴 MERCADO CERRADO — {closed_msg}")

st.markdown("---")

tab_crypto, tab_forex, tab_stocks, tab_indices = st.tabs(["🪙 Criptomonedas", "💱 Forex", "📊 Acciones", "📈 Índices"])

with tab_crypto:
    syms_crypto = config.SYMBOLS.get("CRYPTO", ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"])
    render_market_section("Criptomonedas", syms_crypto, True, "")

with tab_forex:
    syms_forex = config.SYMBOLS.get("FOREX", ["EURUSD=X", "GBPUSD=X", "AUDUSD=X"])
    render_market_section("Forex", syms_forex, is_forex_open(), "Abre el Domingo a las 5:00 PM AST")

with tab_stocks:
    syms_stocks = config.SYMBOLS.get("STOCKS", ["NVDA", "TSLA", "AAPL"])
    render_market_section("Acciones Wall Street", syms_stocks, is_stocks_open(), "Abre el Lunes a las 9:30 AM AST")

with tab_indices:
    syms_indices = config.SYMBOLS.get("INDICES", ["^GSPC", "^DJI"])
    render_market_section("Índices", syms_indices, is_indices_open(), "Abre el Domingo a las 6:00 PM AST")
