import streamlit as st
import pandas as pd
import main
import config
from scanner import fetch_data

st.set_page_config(page_title="JC AI MARKET SCANNER PRO", page_icon="📈", layout="wide")

st.title("🚀 JC AI MARKET SCANNER PRO")
st.caption("Copyright 2026, JESUS CRUZ")

# Inicia el escáner en segundo plano
main.start_background_scanner()

st.success("✅ Escáner activo y monitoreando el mercado 24/7 en la nube.")

# Botón para refrescar la tabla manualmente
if st.button("🔄 Refrescar Tabla de Precios e Indicadores"):
    st.rerun()

st.markdown("---")
st.subheader("📊 Resumen del Mercado en Tiempo Real")

# Generar tabla en vivo
data = []
all_symbols = []
for cat, syms in config.SYMBOLS.items():
    for s in syms:
        all_symbols.append((s, cat))

with st.spinner("Cargando datos actuales de los activos..."):
    for sym, cat in all_symbols[:15]:  # Muestra los primeros 15 para carga rápida
        df = fetch_data(sym, "5m", "1d")
        if df is not None and not df.empty:
            row = df.iloc[-1]
            price = round(float(row['Close']), 4)
            rsi = round(float(row['RSI']), 2)
            ema30 = round(float(row['EMA_30']), 4)
            
            # Tendencia rápida
            trend = "🟢 Alcista" if price > ema30 else "🔴 Bajista"
            
            data.append({
                "Símbolo": sym,
                "Categoría": cat,
                "Precio Actual": price,
                "RSI (M5)": rsi,
                "EMA 30": ema30,
                "Estado M5": trend
            })

if data:
    df_display = pd.DataFrame(data)
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("Obteniendo datos de mercado...")
