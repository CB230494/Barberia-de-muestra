import sqlite3
from datetime import datetime

def conectar():
    return sqlite3.connect("barberia.db")

def init_db():
    crear_tabla_cortes()
    crear_tabla_ventas()
    crear_tabla_inventario()
    crear_tabla_gastos()
def crear_tabla_cortes():
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cortes (
            fecha TEXT PRIMARY KEY,
            cantidad INTEGER,
            ganancia REAL DEFAULT 0.0
        )
    """)
    # Verifica si falta la columna 'ganancia' y la agrega si no existe
    c.execute("PRAGMA table_info(cortes);")
    columnas = [col[1] for col in c.fetchall()]
    if "ganancia" not in columnas:
        c.execute("ALTER TABLE cortes ADD COLUMN ganancia REAL DEFAULT 0.0")
    conn.commit()
    conn.close()

def registrar_cortes(fecha, cantidad, ganancia):
    conn = conectar()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO cortes (fecha, cantidad, ganancia) VALUES (?, ?, ?)", (fecha, cantidad, ganancia))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def obtener_registros():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT fecha, cantidad, ganancia FROM cortes ORDER BY fecha DESC")
    datos = c.fetchall()
    conn.close()
    return datos

def actualizar_corte(fecha, nueva_cantidad, nueva_ganancia):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE cortes SET cantidad = ?, ganancia = ? WHERE fecha = ?", (nueva_cantidad, nueva_ganancia, fecha))
    conn.commit()
    conn.close()

def eliminar_corte(fecha):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM cortes WHERE fecha = ?", (fecha,))
    conn.commit()
    conn.close()

def obtener_resumen():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT SUM(cantidad), SUM(ganancia) FROM cortes")
    resumen = c.fetchone()
    conn.close()
    return resumen or (0, 0.0)

def obtener_cortes_por_mes(anio, mes):
    conn = conectar()
    c = conn.cursor()
    fecha_inicio = f"{anio}-{mes:02d}-01"
    fecha_fin = f"{anio}-{mes:02d}-31"
    c.execute("SELECT fecha, cantidad, ganancia FROM cortes WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC", (fecha_inicio, fecha_fin))
    resultados = c.fetchall()
    conn.close()
    return resultados
def crear_tabla_ventas():
    conn = conectar()
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
    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO ventas (fecha, producto, cantidad, total) VALUES (?, ?, ?, ?)", (fecha, producto, cantidad, total))
    conn.commit()
    conn.close()

def obtener_ventas():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT fecha, producto, cantidad, total FROM ventas ORDER BY fecha DESC")
    datos = c.fetchall()
    conn.close()
    return datos

def crear_tabla_gastos():
    conn = conectar()
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
    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO gastos (fecha, descripcion, monto) VALUES (?, ?, ?)", (fecha, descripcion, monto))
    conn.commit()
    conn.close()

def obtener_gastos_por_mes(anio, mes):
    conn = conectar()
    c = conn.cursor()
    fecha_inicio = f"{anio}-{mes:02d}-01"
    fecha_fin = f"{anio}-{mes:02d}-31"
    c.execute("SELECT fecha, descripcion, monto FROM gastos WHERE fecha BETWEEN ? AND ?", (fecha_inicio, fecha_fin))
    resultados = c.fetchall()
    conn.close()
    return resultados

def obtener_resumen_mensual(anio, mes):
    conn = conectar()
    c = conn.cursor()

    # Cortes
    fecha_inicio = f"{anio}-{mes:02d}-01"
    fecha_fin = f"{anio}-{mes:02d}-31"
    c.execute("SELECT SUM(cantidad), SUM(ganancia) FROM cortes WHERE fecha BETWEEN ? AND ?", (fecha_inicio, fecha_fin))
    resumen_cortes = c.fetchone()
    cortes_realizados = resumen_cortes[0] or 0
    ganancia_cortes = resumen_cortes[1] or 0.0

    # Ventas
    c.execute("SELECT SUM(cantidad), SUM(total) FROM ventas WHERE fecha BETWEEN ? AND ?", (fecha_inicio, fecha_fin))
    resumen_ventas = c.fetchone()
    productos_vendidos = resumen_ventas[0] or 0
    ganancia_ventas = resumen_ventas[1] or 0.0

    # Gastos
    c.execute("SELECT SUM(monto) FROM gastos WHERE fecha BETWEEN ? AND ?", (fecha_inicio, fecha_fin))
    total_gastos = c.fetchone()[0] or 0.0

    conn.close()
    return {
        "cortes_realizados": cortes_realizados,
        "ganancia_cortes": ganancia_cortes,
        "productos_vendidos": productos_vendidos,
        "ganancia_ventas": ganancia_ventas,
        "total_gastos": total_gastos
    }
def crear_tabla_inventario():
    conn = conectar()
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
    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO inventario (nombre, cantidad, costo) VALUES (?, ?, ?)", (nombre, cantidad, costo))
    conn.commit()
    conn.close()

def obtener_productos():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT nombre, cantidad, costo FROM inventario ORDER BY nombre ASC")
    productos = c.fetchall()
    conn.close()
    return productos

def actualizar_producto(nombre, nueva_cantidad, nuevo_costo):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE inventario SET cantidad = ?, costo = ? WHERE nombre = ?", (nueva_cantidad, nuevo_costo, nombre))
    conn.commit()
    conn.close()

def eliminar_producto(nombre):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM inventario WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()
