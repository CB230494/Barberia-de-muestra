from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import (
    init_db, registrar_cita, obtener_citas, obtener_citas_por_fecha,
    bloquear_hora, desbloquear_hora
)

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"mensaje": "API de la Barbería funcionando correctamente"}

@app.post("/agendar")
async def agendar(request: Request):
    data = await request.json()
    nombre = data.get("nombre")
    fecha = data.get("fecha")
    hora = data.get("hora")

    if not all([nombre, fecha, hora]):
        return {"status": "error", "mensaje": "Faltan datos obligatorios"}

    registrar_cita(nombre, fecha, hora)
    return {
        "status": "ok",
        "mensaje": f"Cita registrada para {nombre} el {fecha} a las {hora}"
    }

@app.get("/citas")
def listar_citas():
    citas = obtener_citas()
    return {"citas": citas}

@app.get("/citas/{fecha}")
def citas_por_fecha(fecha: str):
    ocupadas = obtener_citas_por_fecha(fecha)
    return {"fecha": fecha, "ocupadas": ocupadas}

@app.post("/bloquear")
async def bloquear(request: Request):
    data = await request.json()
    fecha = data.get("fecha")
    hora = data.get("hora")
    if not all([fecha, hora]):
        return {"status": "error", "mensaje": "Faltan datos obligatorios"}

    bloquear_hora(fecha, hora)
    return {"status": "ok", "mensaje": f"Hora {hora} bloqueada el {fecha}"}

@app.post("/desbloquear")
async def desbloquear(request: Request):
    data = await request.json()
    fecha = data.get("fecha")
    hora = data.get("hora")
    if not all([fecha, hora]):
        return {"status": "error", "mensaje": "Faltan datos obligatorios"}

    desbloquear_hora(fecha, hora)
    return {"status": "ok", "mensaje": f"Hora {hora} desbloqueada el {fecha}"}

