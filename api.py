from fastapi import FastAPI, Request
from pydantic import BaseModel
import sqlite3
from database import init_db

app = FastAPI()
init_db()

class Cita(BaseModel):
    nombre: str
    fecha: str
    hora: str

@app.post("/agendar")
async def agendar(cita: Cita):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute("SELECT * FROM citas WHERE fecha=? AND hora=?", (cita.fecha, cita.hora))
    if c.fetchone():
        conn.close()
        return {"status": "error", "message": "Hora ya ocupada o bloqueada"}

    c.execute("INSERT INTO citas (nombre, fecha, hora) VALUES (?, ?, ?)",
              (cita.nombre, cita.fecha, cita.hora))
    conn.commit()
    conn.close()
    return {"status": "ok", "message": "Cita registrada exitosamente"}
