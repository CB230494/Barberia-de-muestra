import streamlit as st
from database import init_db, registrar_cortes, obtener_registros
from datetime import date

# Inicializar la base de datos
init_db()

# Título principal
st.title("Barbería - Versión Básica 💈")

# Menú de navegación
tabs = st.tabs(["Registrar cortes", "Historial de cortes"])

# --- Tab 1: Registro diario ---
with tabs[0]:
    st.header("Registrar cortes del día")

    fecha = st.date_input("Fecha", date.today())
    cantidad = st.number_input("Cantidad de cortes", min_value=0, step=1)
    ganancias = st.number_input("Ganancia total del día (₡)", min_value=0.0, step=100.0, format="%.2f")

    if st.button("Guardar"):
        registrar_cortes(str(fecha), cantidad, ganancias)
        st.success("Registro guardado correctamente")

# --- Tab 2: Historial ---
with tabs[1]:
    st.header("Historial de cortes")
    registros = obtener_registros()
    if registros:
        st.table(registros)
    else:
        st.info("Aún no se han registrado cortes.")


