import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("citas.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def registrar_cita(nombre, fecha, hora):
    conn = sqlite3.connect("citas.db")
    c = conn.cursor()
    c.execute("INSERT INTO citas (nombre, fecha, hora) VALUES (?, ?, ?)", (nombre, fecha, hora))
    conn.commit()
    conn.close()

def obtener_citas():
    conn = sqlite3.connect("citas.db")
    c = conn.cursor()
    c.execute("SELECT nombre, fecha, hora FROM citas ORDER BY fecha, hora")
    citas = c.fetchall()
    conn.close()
    return citas
