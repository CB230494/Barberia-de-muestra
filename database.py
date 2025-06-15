import sqlite3
from datetime import date

def init_db():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cortes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL UNIQUE,
            cantidad_cortes INTEGER NOT NULL,
            ganancias REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def registrar_cortes(fecha, cantidad_cortes, ganancias):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO cortes (fecha, cantidad_cortes, ganancias) VALUES (?, ?, ?)",
                       (fecha, cantidad_cortes, ganancias))
        conn.commit()
        exito = True
    except sqlite3.IntegrityError:
        exito = False  # Ya existe registro para esa fecha
    conn.close()
    return exito

def obtener_registros():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, cantidad_cortes, ganancias FROM cortes ORDER BY fecha DESC")
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_resumen():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(cantidad_cortes), SUM(ganancias) FROM cortes")
    resumen = cursor.fetchone()
    conn.close()
    return resumen if resumen else (0, 0.0)

