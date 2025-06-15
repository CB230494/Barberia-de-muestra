import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, time

# Configuración de la página
st.set_page_config(page_title="💈 Barbería - Agenda de Citas", layout="centered")

# Conexión y creación de base de datos
conn = sqlite3.connect("barberia.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS citas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora TEXT NOT NULL,
        registrado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# Función para registrar cita
def registrar_cita(nombre, fecha, hora):
    # Verificar duplicados
    c.execute("SELECT * FROM citas WHERE nombre=? AND fecha=? AND hora=?", (nombre, fecha, hora))
    if c.fetchone():
        return False
    c.execute("INSERT INTO citas (nombre, fecha, hora) VALUES (?, ?, ?)", (nombre, fecha, hora))
    conn.commit()
    return True

# Función para obtener todas las citas
def obtener_citas():
    return pd.read_sql_query("SELECT id, nombre, fecha, hora, registrado_en FROM citas ORDER BY fecha, hora", conn)

# Función para obtener citas del día
def citas_de_hoy():
    hoy = date.today().strftime('%Y-%m-%d')
    return pd.read_sql_query("SELECT id, nombre, fecha, hora FROM citas WHERE fecha = ? ORDER BY hora", conn, params=(hoy,))

# Función para eliminar cita
def eliminar_cita(id_cita):
    c.execute("DELETE FROM citas WHERE id=?", (id_cita,))
    conn.commit()

# Interfaz principal
st.title("💈 Barbería Colonia Carvajal")
st.subheader("Agenda de Citas")

# Formulario de registro
with st.form("formulario_registro"):
    nombre = st.text_input("Nombre del cliente")
    fecha = st.date_input("Fecha de la cita", min_value=date.today())
    hora = st.time_input("Hora de la cita", value=time(10, 0))

    enviar = st.form_submit_button("➕ Registrar cita")

    if enviar:
        if nombre and fecha and hora:
            exito = registrar_cita(nombre.strip(), fecha.strftime('%Y-%m-%d'), hora.strftime('%H:%M'))
            if exito:
                st.success(f"Cita registrada para {nombre} el {fecha} a las {hora.strftime('%H:%M')}")
            else:
                st.warning("⚠️ Ya existe una cita registrada con ese nombre, fecha y hora.")
        else:
            st.error("Todos los campos son obligatorios.")

st.markdown("---")

# Mostrar citas de hoy
st.subheader("📅 Citas para hoy")
df_hoy = citas_de_hoy()
if df_hoy.empty:
    st.info("No hay citas registradas para hoy.")
else:
    st.dataframe(df_hoy.drop(columns=["id"]), use_container_width=True)

st.markdown("---")

# Mostrar todas las citas
st.subheader("📋 Todas las citas")
df_todas = obtener_citas()

if not df_todas.empty:
    for idx, row in df_todas.iterrows():
        st.markdown(f"""
        🔸 **{row['nombre']}**  
        📅 {row['fecha']} ⏰ {row['hora']}  
        🕒 Registrado en: *{row['registrado_en']}*
        """)
        col1, col2 = st.columns([0.8, 0.2])
        with col2:
            if st.button("🗑️ Eliminar", key=f"eliminar_{row['id']}"):
                eliminar_cita(row['id'])
                st.experimental_rerun()
else:
    st.info("No hay citas registradas.")

