from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from datetime import datetime

app = FastAPI(title="NFC Cloud Redirection API")

# Diccionario que simula la base de datos de enlaces de cada negocio
NEGOCIOS_DB = {
    "uth": "https://www.google.com/maps/place/Universidad+Tecnol%C3%B3gica+de+Honduras+-+UTH/@14.0445169,-87.1818893,816m/data=!3m1!1e3!4m8!3m7!1s0x8f6fbcfd9e49eb59:0x5435e60d9baa7b03!8m2!3d14.0445594!4d-87.1810624!9m1!1b1!16s%2Fg%2F11c5",
    "demo": "https://google.com"
}

@app.get("/")
def home():
    return {"status": "Servidor en la Nube Activo", "version": "1.0"}

@app.get("/r/{negocio_id}")
def redirigir_y_registrar(negocio_id: str, request: Request):
    # Convertir a minúsculas para evitar problemas de tipeo
    key = negocio_id.lower()
    
    # Capturar datos para analíticas en la nube
    fecha_escaneo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_agent = request.headers.get("user-agent", "Desconocido")
    ip_cliente = request.client.host if request.client else "Desconocida"

    print(f"[{fecha_escaneo}] Escaneo registrado para: {key} desde IP {ip_cliente}")

    # Obtener URL o enviar a Google si no se encuentra el ID
    url_destino = NEGOCIOS_DB.get(key, "https://google.com")
    
    # Retornar la redirección HTTP 307
    return RedirectResponse(url=url_destino)