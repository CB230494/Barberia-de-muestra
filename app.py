import streamlit as st
from datetime import date
import pandas as pd
from database import (
    init_db,
    registrar_cortes,
    obtener_registros,
    obtener_resumen,
    obtener_cortes_por_mes,
    registrar_venta,
    obtener_ventas,
    obtener_resumen_mensual
)

init_db()

# --- ESTILOS ---
st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background-color: #002366;
    }
    section[data-testid="stSidebar"] div.stRadio > label {
        display: block;
        padding: 0.5rem 1rem;
        background-color: #800000;
        color: white;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        transition: 0.2s;
    }
    section[data-testid="stSidebar"] div.stRadio > label:hover {
        background-color: #a00000;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
st.sidebar.title("💈 Menú")
opcion = st.sidebar.radio("Ir a:", ["Registro de cortes", "Gestión mensual y ventas"])

# --- REGISTRO DE CORTES (parte básica) ---
if opcion == "Registro de cortes":
    st.title("💈 Registro de cortes")

    with st.form("form_registro"):
        st.subheader("📝 Registrar cortes del día")
        fecha = st.date_input("Fecha", date.today())
        cantidad = st.number_input("Cantidad de cortes", min_value=0, step=1)
        ganancias = st.number_input("Ganancia total del día (₡)", min_value=0.0, step=100.0, format="%.2f")
        submit = st.form_submit_button("Guardar")
        if submit:
            exito = registrar_cortes(str(fecha), cantidad, ganancias)
            if exito:
                st.success("✅ Registro guardado correctamente")
            else:
                st.warning("⚠️ Ya existe un registro para esa fecha.")

    st.subheader("📅 Historial de cortes registrados")
    registros = obtener_registros()
    if registros:
        df = pd.DataFrame(registros, columns=["Fecha", "Cantidad de cortes", "Ganancias"])
        st.table(df)
    else:
        st.info("Aún no se han registrado cortes.")

    st.subheader("📊 Resumen general")
    total_cortes, total_ganancias = obtener_resumen()
    st.markdown(f"✂️ **Total de cortes realizados:** {total_cortes}")
    st.markdown(f"💰 **Ganancias acumuladas:** ₡{total_ganancias:.2f}")

# --- GESTIÓN MENSUAL Y VENTAS (parte media) ---
elif opcion == "Gestión mensual y ventas":
    st.title("📦 Barbería - Parte Media del Proyecto")
    st.caption("Esta sección incluye todo lo del módulo básico (registro de cortes) y añade: resumen mensual y control de ventas.")

    # --- Filtro mensual de cortes ---
    st.subheader("📅 Filtro mensual de cortes")
    col1, col2 = st.columns(2)
    with col1:
        anio = st.selectbox("Año", list(range(2023, date.today().year + 1)))
    with col2:
        mes = st.selectbox("Mes", list(range(1, 13)))

    cortes_mes = obtener_cortes_por_mes(anio, mes)
    if cortes_mes:
        df_cortes = pd.DataFrame(cortes_mes, columns=["Fecha", "Cantidad de cortes", "Ganancias"])
        st.table(df_cortes)
    else:
        st.info("No hay cortes registrados en ese mes.")

    # --- Registro de ventas ---
    st.subheader("🧴 Registro de ventas de productos")
    with st.form("form_ventas"):
        fecha_venta = st.date_input("Fecha de venta", date.today())
        producto = st.text_input("Producto vendido (ej. cera, crema)")
        cantidad = st.number_input("Cantidad vendida", min_value=1, step=1)
        total = st.number_input("Total vendido (₡)", min_value=0.0, step=100.0, format="%.2f")
        enviar_venta = st.form_submit_button("Registrar venta")
        if enviar_venta and producto:
            registrar_venta(str(fecha_venta), producto, cantidad, total)
            st.success("✅ Venta registrada exitosamente")

    # --- Historial de ventas ---
    st.subheader("🧾 Historial de ventas")
    ventas = obtener_ventas()
    if ventas:
        df_ventas = pd.DataFrame(ventas, columns=["Fecha", "Producto", "Cantidad", "Total"])
        st.table(df_ventas)
    else:
        st.info("Aún no hay ventas registradas.")

    # --- Resumen mensual combinado ---
    st.subheader("📊 Resumen mensual combinado")
    resumen = obtener_resumen_mensual(anio, mes)
    st.markdown(f"- ✂️ Cortes realizados: **{resumen['cortes_realizados']}**")
    st.markdown(f"- 💰 Ganancia por cortes: **₡{resumen['ganancia_cortes']:.2f}**")
    st.markdown(f"- 🧴 Productos vendidos: **{resumen['productos_vendidos']}**")
    st.markdown(f"- 💸 Ganancia por ventas: **₡{resumen['ganancia_ventas']:.2f}**")



