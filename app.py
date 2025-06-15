import sqlite3

def init_db():
    crear_tabla_cortes()
    crear_tabla_ventas()
    crear_tabla_inventario()
    crear_tabla_gastos()
def crear_tabla_cortes():
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

def registrar_cortes(fecha, cantidad, ganancias):
    try:
        conn = sqlite3.connect("barberia.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cortes (fecha, cantidad_cortes, ganancias) VALUES (?, ?, ?)",
                       (fecha, cantidad, ganancias))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def obtener_registros():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, cantidad_cortes, ganancias FROM cortes ORDER BY fecha DESC")
    registros = cursor.fetchall()
    conn.close()
    return registros

def obtener_resumen():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(cantidad_cortes), SUM(ganancias) FROM cortes")
    resumen = cursor.fetchone()
    conn.close()
    return resumen

def obtener_cortes_por_mes(anio, mes):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, cantidad_cortes, ganancias FROM cortes
        WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
        ORDER BY fecha DESC
    """, (str(anio), f"{mes:02d}"))
    cortes_mes = cursor.fetchall()
    conn.close()
    return cortes_mes

def eliminar_corte(fecha):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cortes WHERE fecha = ?", (fecha,))
    conn.commit()
    conn.close()

def actualizar_corte(fecha_original, nueva_cantidad, nueva_ganancia):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE cortes
        SET cantidad_cortes = ?, ganancias = ?
        WHERE fecha = ?
    """, (nueva_cantidad, nueva_ganancia, fecha_original))
    conn.commit()
    conn.close()
def crear_tabla_ventas():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            producto TEXT,
            cantidad INTEGER,
            total REAL
        )
    """)
    conn.commit()
    conn.close()

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
    ventas = cursor.fetchall()
    conn.close()
    return ventas
def crear_tabla_gastos():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            descripcion TEXT,
            monto REAL
        )
    """)
    conn.commit()
    conn.close()

def registrar_gasto(fecha, descripcion, monto):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos (fecha, descripcion, monto) VALUES (?, ?, ?)",
                   (fecha, descripcion, monto))
    conn.commit()
    conn.close()

def obtener_gastos_por_mes(anio, mes):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, descripcion, monto FROM gastos
        WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
        ORDER BY fecha DESC
    """, (str(anio), f"{mes:02d}"))
    gastos = cursor.fetchall()
    conn.close()
    return gastos
def obtener_resumen_mensual(anio, mes):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(cantidad_cortes), SUM(ganancias) FROM cortes WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?", (str(anio), f"{mes:02d}"))
    cortes = cursor.fetchone()

    cursor.execute("SELECT SUM(cantidad), SUM(total) FROM ventas WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?", (str(anio), f"{mes:02d}"))
    ventas = cursor.fetchone()

    cursor.execute("SELECT SUM(monto) FROM gastos WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?", (str(anio), f"{mes:02d}"))
    gastos = cursor.fetchone()

    conn.close()

    return {
        "cortes_realizados": cortes[0] if cortes[0] else 0,
        "ganancia_cortes": cortes[1] if cortes[1] else 0.0,
        "productos_vendidos": ventas[0] if ventas[0] else 0,
        "ganancia_ventas": ventas[1] if ventas[1] else 0.0,
        "total_gastos": gastos[0] if gastos[0] else 0.0
    }
