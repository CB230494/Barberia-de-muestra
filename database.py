from supabase import create_client, Client

# ----------------- CONEXIÓN A SUPABASE -----------------
SUPABASE_URL = "https://gnefywpfdmpjnrmwvkre.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImduZWZ5d3BmZG1wam5ybXd2a3JlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3ODU3NjgsImV4cCI6MjA2NjM2MTc2OH0.zgitDqpn9hrS26shbpPGSwBpNgtoU9oCSgk6KWVf_x8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------- ✂️ CORTES -----------------
def insertar_corte(fecha, barbero, cliente, tipo_corte, precio, observacion=""):
    data = {
        "fecha": fecha,
        "barbero": barbero,
        "cliente": cliente,
        "tipo_corte": tipo_corte,
        "precio": precio,
        "observacion": observacion or None
    }
    return supabase.table("cortes").insert(data).execute()

def obtener_cortes():
    return supabase.table("cortes").select("*").order("fecha", desc=True).execute().data

def eliminar_corte(corte_id):
    return supabase.table("cortes").delete().eq("id", corte_id).execute()

def actualizar_corte(corte_id, data_actualizada):
    return supabase.table("cortes").update(data_actualizada).eq("id", corte_id).execute()

# ----------------- 📦 PRODUCTOS -----------------
def insertar_producto(nombre, descripcion, stock, precio_unitario):
    data = {
        "nombre": nombre,
        "descripcion": descripcion or None,
        "stock": stock,
        "precio_unitario": precio_unitario
    }
    return supabase.table("productos").insert(data).execute()

def obtener_productos():
    return supabase.table("productos").select("*").order("id", desc=False).execute().data

def actualizar_producto(producto_id, data_actualizada):
    return supabase.table("productos").update(data_actualizada).eq("id", producto_id).execute()

def eliminar_producto(producto_id):
    return supabase.table("productos").delete().eq("id", producto_id).execute()

# ----------------- 📅 CITAS -----------------
def insertar_cita(fecha, hora, cliente_nombre, barbero, servicio):
    data = {
        "fecha": fecha,
        "hora": hora,
        "cliente_nombre": cliente_nombre,
        "barbero": barbero,
        "servicio": servicio,
        "estado": "pendiente"
    }
    return supabase.table("citas").insert(data).execute()

def obtener_citas():
    return supabase.table("citas").select("*").order("fecha", desc=False).execute().data

def actualizar_estado_cita(cita_id, nuevo_estado):
    return supabase.table("citas").update({"estado": nuevo_estado}).eq("id", cita_id).execute()

def actualizar_cita(cita_id, data_actualizada):
    return supabase.table("citas").update(data_actualizada).eq("id", cita_id).execute()

def eliminar_cita(cita_id):
    return supabase.table("citas").delete().eq("id", cita_id).execute()

# ----------------- 💵 INGRESOS -----------------
def insertar_ingreso(fecha, concepto, monto, observacion=""):
    data = {
        "fecha": fecha,
        "concepto": concepto,
        "monto": monto,
        "observacion": observacion or None
    }
    return supabase.table("ingresos").insert(data).execute()

def obtener_ingresos():
    return supabase.table("ingresos").select("*").order("fecha", desc=True).execute().data

def actualizar_ingreso(ingreso_id, data_actualizada):
    return supabase.table("ingresos").update(data_actualizada).eq("id", ingreso_id).execute()

def eliminar_ingreso(ingreso_id):
    return supabase.table("ingresos").delete().eq("id", ingreso_id).execute()

# ----------------- 💸 GASTOS -----------------
def insertar_gasto(fecha, concepto, monto, observacion=""):
    data = {
        "fecha": fecha,
        "concepto": concepto,
        "monto": monto,
        "observacion": observacion or None
    }
    return supabase.table("gastos").insert(data).execute()

def obtener_gastos():
    return supabase.table("gastos").select("*").order("fecha", desc=True).execute().data

def actualizar_gasto(gasto_id, data_actualizada):
    return supabase.table("gastos").update(data_actualizada).eq("id", gasto_id).execute()

def eliminar_gasto(gasto_id):
    return supabase.table("gastos").delete().eq("id", gasto_id).execute()

