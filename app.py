import streamlit as st
import main

st.set_page_config(page_title="JC AI MARKET SCANNER PRO", page_icon="📈")

st.title("🚀 JC AI MARKET SCANNER PRO")
st.caption("Copyright 2026, JESUS CRUZ")

# Inicia el escáner en un hilo en segundo plano (Background Thread)
main.start_background_scanner()

st.success("✅ El escáner de mercado se encuentra activo y escaneando 24/7 en segundo plano.")
st.info("📲 Las alertas de Alta Probabilidad llegarán automáticamente a tu Bot de Telegram (jctrader_analysis_bot) y Correo Electrónico.")

st.markdown("---")
st.markdown("### Estado del Sistema")
st.write("• **Bot de Telegram:** Vinculado")
st.write("• **Gatillo M5 + Filtro MTF:** Activo")
st.write("• **Símbolos:** Forex, Crypto, Índices, Acciones")
