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

# --- INICIALIZACIÓN DE ESTADO DE SESIÓN (SESSION STATE) ---
if "custom_symbols" not in st.session_state:
    st.session_state.custom_symbols = {
        "CRYPTO": list(config.SYMBOLS.get("CRYPTO", ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"])),
        "FOREX": list(config.SYMBOLS.get("FOREX", ["EURUSD=X", "GBPUSD=X", "AUDUSD=X"])),
        "STOCKS": list(config.SYMBOLS.get("ACCIONES", ["NVDA", "TSLA", "AAPL"])),
        "INDICES": list(config.SYMBOLS.get("INDICES", ["^GSPC", "^DJI"]))
    }

# --- BARRA LATERAL: GESTOR DE ACTIVOS Y BÚSQUEDA ---
st.sidebar.header("⚙️ Gestor de Activos")

# 1. Agregar nuevo activo a una lista
st.sidebar.subheader("➕ Añadir Activo Manual")
mercado_destino = st.sidebar.selectbox("Selecciona Categoría:", ["CRYPTO", "FOREX", "ACCIONES", "INDICES"])
nuevo_simbolo = st.sidebar.text_input("Símbolo (ej: XLM-USD, TSLA, EURGBP=X):").strip().upper()

if st.sidebar.button("➕ Añadir a la lista", use_container_width=True):
    if nuevo_simbolo:
        if nuevo_simbolo not in st.session_state.custom_symbols[mercado_destino]:
            st.session_state.custom_symbols[mercado_destino].append(nuevo_simbolo)
            st.sidebar.success(f"✅ {nuevo_simbolo} añadido a {mercado_destino}")
            st.rerun()
        else:
            st.sidebar.warning(f"⚠️ {nuevo_simbolo} ya está en la lista.")
    else:
        st.sidebar.error("Escribe un símbolo válido.")

# 2. Resetear listas
if st.sidebar.button("🔄 Restablecer listas por defecto", use_container_width=True):
    st.session_state.custom_symbols = {
        "CRYPTO": list(config.SYMBOLS.get("CRYPTO", ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"])),
        "FOREX": list(config.SYMBOLS.get("FOREX", ["EURUSD=X", "GBPUSD=X", "AUDUSD=X"])),
        "STOCKS": list(config.SYMBOLS.get("ACCIONES", ["NVDA", "TSLA", "AAPL"])),
        "INDICES": list(config.SYMBOLS.get("INDICES", ["^GSPC", "^DJI"]))
    }
    st.sidebar.info("Listas restablecidas.")
    st.rerun()

st.sidebar.markdown("---")

# --- CONTROL DE HORARIOS DE MERCADO ---
tz_ast = pytz.timezone('America/Puerto_Rico')
now_ast = datetime.datetime.now(tz_ast)
weekday = now_ast.weekday()
hour = now_ast.hour

st.write(f"🕒 **Hora actual (Puerto Rico):** {now_ast.strftime('%Y-%m-%d %I:%M:%S %p AST')}")

def is_crypto_open(): return True
def is_forex_open(): return not (weekday == 5 or (weekday == 4 and hour >= 17) or (weekday == 6 and hour < 17))
def is_indices_open(): return not (weekday == 5 or (weekday == 4 and hour >= 17) or (weekday == 6 and hour < 18))
def is_stocks_open(): return not (weekday in [5, 6] or hour < 9 or (hour == 9 and now_ast.minute < 30) or hour >= 16)

# --- ESTILIZACIÓN DE DATAFRAME ---
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
        styler = df.style.map(highlight_status, subset=["Tendencia H4", "Pierna H1", "Gatillo M5", "RSI (M5)", "MACD (M5)"])
    except AttributeError:
        styler = df.style.applymap(highlight_status, subset=["Tendencia H4", "Pierna H1", "Gatillo M5", "RSI (M5)", "MACD (M5)"])
    return styler

# --- RENDERING DE SECCIONES ---
def render_market_section(title, symbols, open_status, closed_msg):
    st.subheader(title)
    if open_status:
        st.success("🟢 MERCADO ABIERTO")
        data = []
        for sym in symbols:
            info = analyze_symbol_full(sym)
            if info:
                data.append({
                    "Símbolo": info["Símbolo"],
                    "Precio": info["Precio"],
                    "Tendencia H4": info["Tendencia H4"],
                    "Pierna H1": info["Pierna H1"],
                    "Gatillo M5": info["Gatillo M5"],
                    "RSI (M5)": info["RSI (M5)"],
                    "MACD (M5)": info["MACD (M5)"]
                })
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(style_dataframe(df), use_container_width=True)

            st.markdown("#### 🤖 Generar Informe Ejecutivo")
            col1, col2 = st.columns([2, 1])
            with col1:
                selected_sym = st.selectbox(f"Selecciona un activo de {title}:", symbols, key=f"select_{title}")
            with col2:
                st.write("")
                st.write("")
                btn_gen = st.button(f"🤖 Analizar {selected_sym}", key=f"btn_{title}")

            if btn_gen:
                with st.spinner(f"Analizando {selected_sym}..."):
                    report = generate_ai_report(selected_sym)
                    st.markdown("---")
                    st.info(report)
    else:
        st.error(f"🔴 MERCADO CERRADO — {closed_msg}")

st.markdown("---")

# --- PESTAÑAS PRINCIPALES DE NAVEGACIÓN ---
tab_crypto, tab_forex, tab_stocks, tab_indices = st.tabs(["🪙 Criptomonedas", "💱 Forex", "📊 Acciones", "📈 Índices"])

with tab_crypto:
    render_market_section("Criptomonedas", st.session_state.custom_symbols["CRYPTO"], True, "")

with tab_forex:
    render_market_section("Forex", st.session_state.custom_symbols["FOREX"], is_forex_open(), "Abre el Domingo a las 5:00 PM AST")

with tab_stocks:
    render_market_section("Acciones Wall Street", st.session_state.custom_symbols["STOCKS"], is_stocks_open(), "Abre el Lunes a las 9:30 AM AST")

with tab_indices:
    render_market_section("Índices", st.session_state.custom_symbols["INDICES"], is_indices_open(), "Abre el Domingo a las 6:00 PM AST")
