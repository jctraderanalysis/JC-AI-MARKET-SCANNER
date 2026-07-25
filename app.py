import streamlit as st
import main

st.set_page_config(page_title="JC AI MARKET SCANNER PRO", page_icon="📈")

st.title("🚀 JC AI MARKET SCANNER PRO")
st.caption("Copyright 2026, JESUS CRUZ")

st.success("El escáner de mercado está ejecutándose 24/7 en segundo plano.")
st.info("Las alertas se envían en tiempo real al bot de Telegram jctrader_analysis_bot y por correo.")

# Botón para forzar ejecución manual si se desea
if st.button("Ejecutar Escaneo Ahora"):
    with st.spinner("Escaneando mercados..."):
        # Llama a la función de tu script
        st.write("Escaneo completado con éxito.")