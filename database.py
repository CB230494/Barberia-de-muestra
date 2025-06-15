import sqlite3

def init_db():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    # Tabla para cortes de cabello
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cortes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL UNIQUE,
            cantidad_cortes INTEGER NOT NULL,
            ganancias REAL NOT NULL
        )
    """)

    # Tabla para ventas de productos (cremas, ceras, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()
def registrar_cortes(fecha, cantidad, ganancias):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO cortes (fecha, cantidad_cortes, ganancias) VALUES (?, ?, ?)",
                       (fecha, cantidad, ganancias))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

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
    return resumen if resumen else (0, 0)
def obtener_cortes_por_mes(anio, mes):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, cantidad_cortes, ganancias 
        FROM cortes 
        WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
        ORDER BY fecha
    """, (str(anio), f"{mes:02}"))
    datos = cursor.fetchall()
    conn.close()
    return datos
def registrar_venta(fecha, producto, cantidad, total):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ventas (fecha, producto, cantidad, total) VALUES (?, ?, ?, ?)",
                   (fecha, producto, cantidad, total))
    conn.commit()
    conn.close()

def obtener_ventas():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, producto, cantidad, total FROM ventas ORDER BY fecha DESC")
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_ventas_por_mes(anio, mes):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, producto, cantidad, total 
        FROM ventas 
        WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
        ORDER BY fecha
    """, (str(anio), f"{mes:02}"))
    datos = cursor.fetchall()
    conn.close()
    return datos
def obtener_resumen_mensual(anio, mes):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    # Cortes
    cursor.execute("""
        SELECT SUM(cantidad_cortes), SUM(ganancias) 
        FROM cortes 
        WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
    """, (str(anio), f"{mes:02}"))
    total_cortes, total_ganancias_cortes = cursor.fetchone()

    # Ventas
    cursor.execute("""
        SELECT SUM(cantidad), SUM(total) 
        FROM ventas 
        WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
    """, (str(anio), f"{mes:02}"))
    total_productos, total_ganancias_ventas = cursor.fetchone()

    conn.close()

    return {
        "cortes_realizados": total_cortes or 0,
        "ganancia_cortes": total_ganancias_cortes or 0,
        "productos_vendidos": total_productos or 0,
        "ganancia_ventas": total_ganancias_ventas or 0
    }

