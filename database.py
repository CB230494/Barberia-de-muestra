import sqlite3

def init_db():
    crear_tabla_cortes()
    crear_tabla_ventas()
    crear_tabla_inventario()

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

def obtener_resumen_mensual(anio, mes):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            SUM(c.cantidad_cortes),
            SUM(c.ganancias),
            SUM(v.cantidad),
            SUM(v.total)
        FROM cortes c
        LEFT JOIN ventas v ON strftime('%Y', c.fecha) = strftime('%Y', v.fecha) AND strftime('%m', c.fecha) = strftime('%m', v.fecha)
        WHERE strftime('%Y', c.fecha) = ? AND strftime('%m', c.fecha) = ?
    """, (str(anio), f"{mes:02d}"))
    resultado = cursor.fetchone()
    conn.close()
    return {
        "cortes_realizados": resultado[0],
        "ganancia_cortes": resultado[1],
        "productos_vendidos": resultado[2],
        "ganancia_ventas": resultado[3]
    }
def crear_tabla_inventario():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            nombre TEXT,
            tipo TEXT,
            cantidad INTEGER,
            precio_unitario REAL
        )
    """)
    conn.commit()
    conn.close()

def registrar_producto(nombre, tipo, cantidad, precio_unitario):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO inventario (nombre, tipo, cantidad, precio_unitario)
        VALUES (?, ?, ?, ?)
    """, (nombre, tipo, cantidad, precio_unitario))
    conn.commit()
    conn.close()

def obtener_productos():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, tipo, cantidad, precio_unitario FROM inventario")
    productos = cursor.fetchall()
    conn.close()
    return productos

def eliminar_producto(nombre, tipo):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventario WHERE nombre = ? AND tipo = ?", (nombre, tipo))
    conn.commit()
    conn.close()

def actualizar_producto(nombre_ant, tipo_ant, nombre, tipo, cantidad, precio_unitario):
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE inventario
        SET nombre = ?, tipo = ?, cantidad = ?, precio_unitario = ?
        WHERE nombre = ? AND tipo = ?
    """, (nombre, tipo, cantidad, precio_unitario, nombre_ant, tipo_ant))
    conn.commit()
    conn.close()


