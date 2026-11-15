from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI(title="NFC Cloud Redirection API")

# Base de datos en memoria para URLs dinámicas
NEGOCIOS_DB = {
    "uth": "https://www.google.com/maps/place/Universidad+Tecnol%C3%B3gica+de+Honduras+-+UTH/@14.0445169,-87.1818893,816m/data=!3m1!1e3!4m8!3m7!1s0x8f6fbcfd9e49eb59:0x5435e60d9baa7b03!8m2!3d14.0445594!4d-87.1810624!9m1!1b1!16s%2Fg%2F11c5",
    "demo": "https://google.com"
}

# Historial real de escaneos en tiempo real
HISTORIAL_ESCANEOS = []

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
    fecha_escaneo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_agent = request.headers.get("user-agent", "Desconocido")
    dispositivo = detectar_dispositivo(user_agent)
    
    # Clasificar el origen físico
    tipo_origen = "Tarjeta NFC (NTAG213)" if origen.lower() == "nfc" else "Código QR Impreso"

    # Guardar registro real
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