import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="TapCloud | Analítica & Reputación en la Nube", page_icon="☁️", layout="wide")

API_URL = "https://nfc-cloud-saas.onrender.com"

st.title("☁️ TapCloud — Panel de Métricas & Reputación")
st.subheader("Cliente: Universidad Tecnológica de Honduras (UTH)")

if st.button("🔄 Actualizar Datos en Tiempo Real"):
    st.rerun()

try:
    respuesta = requests.get(f"{API_URL}/api/metricas", timeout=15)
    datos = respuesta.json()
    escaneos = datos.get("escaneos", [])
except Exception:
    escaneos = []
    st.warning("⏳ El servidor en Render está despertando. Haz clic en 'Actualizar Datos en Tiempo Real' en unos segundos.")

st.divider()

total = len(escaneos)
if total > 0:
    df = pd.DataFrame(escaneos)
    conteo_origen = df["Origen"].value_counts()
    metodo_top = conteo_origen.index[0]
    porcentaje_top = (conteo_origen.iloc[0] / total) * 100
    texto_metodo = f"{'NFC' if 'NFC' in metodo_top else 'QR'} ({porcentaje_top:.1f}%)"
else:
    df = pd.DataFrame(columns=["Fecha y Hora", "Negocio ID", "Origen", "Navegador"])
    texto_metodo = "Sin datos aún"

col1, col2, col3 = st.columns(3)
col1.metric("Total Escaneos (En Vivo)", str(total), f"+{total} registrados")
col2.metric("Método más usado", texto_metodo)
col3.metric("Estado del Servidor", "24/7 En Nube")

st.divider()

c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📜 Historial de Escaneos en Tiempo Real")
    if total > 0:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay escaneos registrados. Escanea el QR o acerca tu teléfono a la tarjeta NFC y presiona Actualizar.")

with c2:
    st.subheader("📱 Distribución por Origen")
    if total > 0:
        st.bar_chart(df["Origen"].value_counts())
    else:
        st.info("Esperando el primer escaneo para graficar.")