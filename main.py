import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional

app = FastAPI(title="NFC Cloud Redirection API")

# Credenciales de Upstash desde Variables de Entorno de Render
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "").rstrip("/")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {UPSTASH_TOKEN}"}

DEFAULT_URLS = {
    "uth": "https://search.google.com/local/writereview?placeid=ChIJWetJnv28b48RA3uqmw3mNVQ",
    "demo": "https://google.com"
}

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

def upstash_cmd(comando: list):
    """Ejecuta comandos en Upstash Redis vía API REST"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return None
    try:
        res = requests.post(UPSTASH_URL, headers=HEADERS, json=comando, timeout=5)
        return res.json().get("result")
    except Exception:
        return None

@app.get("/")
def home():
    total = upstash_cmd(["LLEN", "historial_escaneos"]) or 0
    return {
        "status": "Servidor en la Nube Activo + Persistencia Upstash",
        "total_registros_permanentes": total
    }

@app.get("/r/{negocio_id}")
def redirigir_y_registrar(negocio_id: str, request: Request, origen: Optional[str] = "qr"):
    key = negocio_id.lower()
    ahora_hn = datetime.now(ZoneInfo("America/Tegucigalpa"))
    fecha_escaneo = ahora_hn.strftime("%Y-%m-%d %H:%M:%S")
    
    user_agent = request.headers.get("user-agent", "Desconocido")
    ip_cliente = request.client.host if request.client else "0.0.0.0"
    dispositivo = detectar_dispositivo(user_agent)
    tipo_origen = "Tarjeta NFC (NTAG213)" if origen.lower() == "nfc" else "Código QR Impreso"

    # Filtro anti-duplicados (15 segundos)
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
        upstash_cmd(["LPUSH", "historial_escaneos", json.dumps(registro)])

    url_guardada = upstash_cmd(["HGET", "negocios_urls", key])
    url_destino = url_guardada if url_guardada else DEFAULT_URLS.get(key, "https://google.com")
    return RedirectResponse(url=url_destino)

@app.get("/api/metricas")
def obtener_metricas():
    crudos = upstash_cmd(["LRANGE", "historial_escaneos", 0, -1]) or []
    escaneos = [json.loads(item) for item in crudos]
    
    url_uth = upstash_cmd(["HGET", "negocios_urls", "uth"]) or DEFAULT_URLS["uth"]
    return {
        "escaneos": escaneos,
        "urls": {"uth": url_uth}
    }

@app.post("/api/actualizar-url")
def actualizar_url(datos: UpdateUrlRequest):
    key = datos.negocio_id.lower()
    upstash_cmd(["HSET", "negocios_urls", key, datos.nueva_url])
    return {"mensaje": "URL guardada permanentemente en la nube", "nueva_url": datos.nueva_url}