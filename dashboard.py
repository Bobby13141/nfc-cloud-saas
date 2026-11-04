import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página web del cliente
st.set_page_config(page_title="Panel de Métricas | Phygital Cloud", page_icon="📊", layout="wide")

# Título y encabezado para el cliente
st.title("📊 Panel de Métricas & Reputación en la Nube")
st.subheader("Cliente: Universidad Tecnológica de Honduras (UTH)")
st.divider()

# Simulador de base de datos de métricas obtenidas desde main.py
datos_escaneos = [
    {"Fecha y Hora": "2026-11-04 00:58:30", "Negocio ID": "uth", "Origen": "Tarjeta NFC (NTAG213)", "Navegador": "Chrome / Windows"},
    {"Fecha y Hora": "2026-11-04 01:16:56", "Negocio ID": "uth", "Origen": "Código QR Impreso", "Navegador": "Safari / iPhone"},
    {"Fecha y Hora": "2026-11-04 01:20:10", "Negocio ID": "uth", "Origen": "Tarjeta NFC (NTAG213)", "Navegador": "Chrome / Android"},
]

df = pd.DataFrame(datos_escaneos)

# --- SECCIÓN DE MÉTRICAS RÁPIDAS (Tarjetas KPI) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Escaneos (Este Mes)", value=len(df), delta="+2 hoy")
with col2:
    st.metric(label="Método más usado", value="NFC (66.7%)")
with col3:
    st.metric(label="Estado del Servidor", value="24/7 En Nube", delta_color="normal")

st.divider()

# --- SECCIÓN DE GRÁFICAS Y TABLAS DE DATOS ---
col_tabla, col_grafica = st.columns([2, 1])

with col_tabla:
    st.write("### 📜 Historial de Escaneos en Tiempo Real")
    st.dataframe(df, use_container_width=True)

with col_grafica:
    st.write("### 📱 Distribución por Origen")
    conteo_origen = df["Origen"].value_counts()
    st.bar_chart(conteo_origen)

st.divider()

# --- SECCIÓN DE CONTROL DINÁMICO (Para que el cliente cambie su destino) ---
st.write("### ⚙️ Configuración de Redirección Dinámica")
st.info("Desde aquí el dueño del negocio puede cambiar la URL sin tener que modificar la tarjeta física o el QR.")

url_actual = st.text_input(
    "URL actual de destino (Google Reviews UTH):", 
    value="https://www.google.com/maps/place/Universidad+Tecnol%C3%B3gica+de+Honduras+-+UTH/..."
)

if st.button("Actualizar URL de Destino"):
    st.success("✅ ¡URL de destino actualizada con éxito en el servidor Python!")