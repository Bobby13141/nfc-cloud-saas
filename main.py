from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional

app = FastAPI(title="NFC Cloud Redirection API")

# URL oficial directa a reseñas de UTH Tegucigalpa mediante Place ID
NEGOCIOS_DB = {
    "uth": "https://search.google.com/local/writereview?placeid=ChIJWetJnv28b48RA3uqmw3mNVQ",
    "demo": "https://google.com"
}

HISTORIAL_ESCANEOS = []
ULTIMOS_ACCESOS = {}

class UpdateUrlRequest(BaseModel):
    negocio_id: str
    nueva_url: str

def detectar_dispositivo(user_agent: str) -> str:
    ua = user_agent.lower()
    if "iphone" in ua or "ipad" in ua:
        return "Safari / iPhone"
    elif "android" in ua:
        return "Chrome / Android"
    elif "windows" in ua:
        return "Chrome / Windows"
    elif "mac" in ua:
        return "Safari / Mac"
    return "Móvil / Otro"

@app.get("/")
def home():
    return {"status": "Servidor en la Nube Activo", "total_registros": len(HISTORIAL_ESCANEOS)}

@app.get("/r/{negocio_id}")
def redirigir_y_registrar(negocio_id: str, request: Request, origen: Optional[str] = "qr"):
    key = negocio_id.lower()
    ahora_hn = datetime.now(ZoneInfo("America/Tegucigalpa"))
    fecha_escaneo = ahora_hn.strftime("%Y-%m-%d %H:%M:%S")
    
    user_agent = request.headers.get("user-agent", "Desconocido")
    ip_cliente = request.client.host if request.client else "0.0.0.0"
    dispositivo = detectar_dispositivo(user_agent)
    tipo_origen = "Tarjeta NFC (NTAG213)" if origen.lower() == "nfc" else "Código QR Impreso"

    # Filtro anti-duplicados (evita contar doble si un teléfono salta de navegador a app en <15s)
    clave_unica = f"{ip_cliente}_{key}_{tipo_origen}"
    ultimo_tiempo = ULTIMOS_ACCESOS.get(clave_unica)

    if not ultimo_tiempo or (ahora_hn - ultimo_tiempo) > timedelta(seconds=15):
        ULTIMOS_ACCESOS[clave_unica] = ahora_hn
        registro = {
            "Fecha y Hora": fecha_escaneo,
            "Negocio ID": key,
            "Origen": tipo_origen,
            "Navegador": dispositivo
        }
        HISTORIAL_ESCANEOS.insert(0, registro)

    url_destino = NEGOCIOS_DB.get(key, "https://google.com")
    return RedirectResponse(url=url_destino)

@app.get("/api/metricas")
def obtener_metricas():
    return {
        "escaneos": HISTORIAL_ESCANEOS,
        "urls": NEGOCIOS_DB
    }

@app.post("/api/actualizar-url")
def actualizar_url(datos: UpdateUrlRequest):
    key = datos.negocio_id.lower()
    NEGOCIOS_DB[key] = datos.nueva_url
    return {"mensaje": "URL actualizada correctamente", "nueva_url": datos.nueva_url}