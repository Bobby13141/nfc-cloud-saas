import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Panel de Métricas | Phygital Cloud", page_icon="📊", layout="wide")

API_URL = "https://nfc-cloud-saas.onrender.com"

st.title("📊 Panel de Métricas & Reputación en la Nube")
st.subheader("Cliente: Universidad Tecnológica de Honduras (UTH)")

if st.button("🔄 Actualizar Datos en Tiempo Real"):
    st.rerun()

try:
    respuesta = requests.get(f"{API_URL}/api/metricas", timeout=15)
    datos = respuesta.json()
    escaneos = datos.get("escaneos", [])
    url_actual = datos.get("urls", {}).get("uth", "")
except Exception:
    escaneos = []
    url_actual = "https://www.google.com/maps/place/Universidad+Tecnol%C3%B3gica+de+Honduras+-+UTH/..."
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

st.divider()

st.subheader("⚙️ Configuración de Redirección Dinámica")
st.info("Desde aquí el dueño del negocio puede cambiar la URL sin tener que modificar la tarjeta física o el QR.")

nueva_url = st.text_input("URL actual de destino (Google Reviews UTH):", value=url_actual)
if st.button("Actualizar URL de Destino"):
    try:
        res = requests.post(
            f"{API_URL}/api/actualizar-url",
            json={"negocio_id": "uth", "nueva_url": nueva_url},
            timeout=10
        )
        if res.status_code == 200:
            st.success("✅ ¡URL actualizada en la nube! El QR y NFC ahora redirigen al nuevo enlace.")
    except Exception:
        st.error("❌ No se pudo conectar con el servidor. Intenta de nuevo.")