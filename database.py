import sqlite3
from datetime import datetime

def init_db():
    crear_tabla_cortes()
    crear_tabla_ventas()
    crear_tabla_inventario()
    crear_tabla_gastos()
def crear_tabla_cortes():
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cortes (
            fecha TEXT PRIMARY KEY,
            cantidad INTEGER,
            ganancia REAL
        )
    """)
    conn.commit()
    conn.close()

def registrar_cortes(fecha, cantidad, ganancia):
    try:
        conn = sqlite3.connect("barberia.db")
        c = conn.cursor()
        c.execute("INSERT INTO cortes (fecha, cantidad, ganancia) VALUES (?, ?, ?)", (fecha, cantidad, ganancia))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def obtener_registros():
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cortes ORDER BY fecha DESC")
    data = c.fetchall()
    conn.close()
    return data

def obtener_resumen():
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("SELECT SUM(cantidad), SUM(ganancia) FROM cortes")
    data = c.fetchone()
    conn.close()
    return data

def obtener_cortes_por_mes(anio, mes):
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    mes_str = f"{mes:02d}"
    c.execute("SELECT * FROM cortes WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ? ORDER BY fecha", (str(anio), mes_str))
    data = c.fetchall()
    conn.close()
    return data

def eliminar_corte(fecha):
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("DELETE FROM cortes WHERE fecha = ?", (fecha,))
    conn.commit()
    conn.close()

def actualizar_corte(fecha, cantidad, ganancia):
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("UPDATE cortes SET cantidad = ?, ganancia = ? WHERE fecha = ?", (cantidad, ganancia, fecha))
    conn.commit()
    conn.close()
def crear_tabla_ventas():
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
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
    c = conn.cursor()
    c.execute("INSERT INTO ventas (fecha, producto, cantidad, total) VALUES (?, ?, ?, ?)", (fecha, producto, cantidad, total))
    conn.commit()
    conn.close()

def obtener_ventas():
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("SELECT * FROM ventas ORDER BY fecha DESC")
    data = c.fetchall()
    conn.close()
    return data

def obtener_resumen_mensual(anio, mes):
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    mes_str = f"{mes:02d}"

    c.execute("SELECT SUM(cantidad), SUM(ganancia) FROM cortes WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?", (str(anio), mes_str))
    cortes = c.fetchone()

    c.execute("SELECT SUM(cantidad), SUM(total) FROM ventas WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?", (str(anio), mes_str))
    ventas = c.fetchone()

    c.execute("SELECT SUM(monto) FROM gastos WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?", (str(anio), mes_str))
    gastos = c.fetchone()

    conn.close()
    return {
        "cortes_realizados": cortes[0] or 0,
        "ganancia_cortes": cortes[1] or 0.0,
        "productos_vendidos": ventas[0] or 0,
        "ganancia_ventas": ventas[1] or 0.0,
        "total_gastos": gastos[0] or 0.0
    }
def crear_tabla_inventario():
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            nombre TEXT PRIMARY KEY,
            cantidad INTEGER,
            costo REAL
        )
    """)
    conn.commit()
    conn.close()

def registrar_producto(nombre, cantidad, costo):
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("INSERT INTO inventario (nombre, cantidad, costo) VALUES (?, ?, ?)", (nombre, cantidad, costo))
    conn.commit()
    conn.close()

def obtener_productos():
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("SELECT * FROM inventario ORDER BY nombre ASC")
    data = c.fetchall()
    conn.close()
    return data

def actualizar_producto(nombre, nueva_cantidad, nuevo_costo):
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("UPDATE inventario SET cantidad = ?, costo = ? WHERE nombre = ?", (nueva_cantidad, nuevo_costo, nombre))
    conn.commit()
    conn.close()

def eliminar_producto(nombre):
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("DELETE FROM inventario WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()
def crear_tabla_gastos():
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            fecha TEXT,
            descripcion TEXT,
            monto REAL
        )
    """)
    conn.commit()
    conn.close()

def registrar_gasto(fecha, descripcion, monto):
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    c.execute("INSERT INTO gastos (fecha, descripcion, monto) VALUES (?, ?, ?)", (fecha, descripcion, monto))
    conn.commit()
    conn.close()

def obtener_gastos_por_mes(anio, mes):
    conn = sqlite3.connect("barberia.db")
    c = conn.cursor()
    mes_str = f"{mes:02d}"
    c.execute("SELECT * FROM gastos WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ? ORDER BY fecha DESC", (str(anio), mes_str))
    data = c.fetchall()
    conn.close()
    return data

