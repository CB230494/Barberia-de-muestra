import streamlit as st
from database import (
    init_db,
    registrar_cortes,
    obtener_registros,
    obtener_resumen,
    obtener_cortes_por_mes,
    registrar_venta,
    obtener_ventas,
    obtener_resumen_mensual,
    registrar_producto,
    obtener_productos,
    eliminar_producto,
    actualizar_producto
)
from datetime import date, datetime
import calendar
import sqlite3

# Inicializar base de datos
init_db()

# Estilo CSS personalizado
st.markdown("""
    <style>
    /* Menú lateral azul oscuro */
    section[data-testid="stSidebar"] {
        background-color: #002244 !important;
    }

    /* Texto del menú lateral */
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Botones generales */
    .stButton > button {
        background-color: #005caa;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
    }

    .stButton > button:hover {
        background-color: #0b72c1;
    }

    /* Fondo blanco general */
    html, body, .stApp {
        background-color: white;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# Menú lateral
st.sidebar.title("Menú")
opcion = st.sidebar.radio("Ir a:", ["Registro de cortes", "Gestión mensual y ventas", "Inventario"])

# Encabezado principal
st.markdown("## 💈 Sistema de Gestión para Barbería")
if opcion == "Registro de cortes":
    st.subheader("✂️ Registro diario de cortes")

    with st.form("registro_cortes"):
        fecha = st.date_input("Fecha", value=date.today())
        cantidad = st.number_input("Cantidad de cortes", min_value=0, step=1)
        ganancias = st.number_input("Ganancia total del día (₡)", min_value=0.0, step=100.0, format="%.2f")
        registrar = st.form_submit_button("Guardar")

        if registrar:
            fecha_str = fecha.strftime("%Y-%m-%d")
            exito = registrar_cortes(fecha_str, cantidad, ganancias)
            if exito:
                st.success("✅ Corte registrado correctamente")
            else:
                st.error("⚠️ Ya existe un registro para esta fecha.")

    st.subheader("📅 Historial de cortes registrados")
    registros = obtener_registros()
    if registros:
        for reg in registros:
            st.write(f"📌 **{reg[0]}** — Cortes: {reg[1]}, Ganancia: ₡{reg[2]:,.2f}")
    else:
        st.info("No hay cortes registrados todavía.")

    st.subheader("📊 Resumen general")
    resumen = obtener_resumen()
    total_cortes = resumen[0] or 0
    total_ganancias = resumen[1] or 0.0
    st.success(f"💇‍♂️ Total de cortes: **{total_cortes}** — 💰 Ganancia acumulada: **₡{total_ganancias:,.2f}**")
elif opcion == "Gestión mensual y ventas":
    st.subheader("📆 Gestión mensual y ventas de productos")

    hoy = date.today()
    anio_actual = hoy.year
    mes_actual = hoy.month

    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    anio = st.selectbox("Año", list(range(anio_actual, anio_actual - 5, -1)))
    mes = st.selectbox("Mes", list(meses.keys()), format_func=lambda x: meses[x])

    resumen = obtener_resumen_mensual(anio, mes)

    # Validación para evitar errores de formato con None
    cortes = resumen.get("cortes_realizados") or 0
    gan_cortes = resumen.get("ganancia_cortes") or 0.0
    productos = resumen.get("productos_vendidos") or 0
    gan_ventas = resumen.get("ganancia_ventas") or 0.0

    st.subheader(f"📊 Resumen de {meses[mes]} {anio}")
    st.write(f"💈 Cortes: **{cortes}**")
    st.write(f"💰 Ganancia por cortes: **₡{gan_cortes:,.2f}**")
    st.write(f"🧴 Productos vendidos: **{productos}**")
    st.write(f"💵 Ganancia por ventas: **₡{gan_ventas:,.2f}**")

    st.subheader("🧾 Registrar venta de productos")
    with st.form("form_venta"):
        fecha_venta = st.date_input("Fecha", value=date.today(), key="venta_fecha")
        producto = st.text_input("Producto")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        total = st.number_input("Total (₡)", min_value=0.0, step=100.0, format="%.2f")
        registrar_v = st.form_submit_button("Registrar venta")
        if registrar_v and producto:
            registrar_venta(fecha_venta.strftime("%Y-%m-%d"), producto, cantidad, total)
            st.success("✅ Venta registrada correctamente")
            st.experimental_rerun()

    st.subheader("📋 Historial de ventas")
    ventas = obtener_ventas()
    if ventas:
        filtro = st.text_input("🔎 Filtrar por producto")
        for i, v in enumerate(ventas):
            if filtro.lower() in v[1].lower():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                col1.write(f"📅 {v[0]}")
                col2.write(f"🧴 {v[1]}")
                col3.write(f"{v[2]} ud.")
                col4.write(f"₡{v[3]:,.2f}")
                with col5:
                    if st.button("🗑️", key=f"del_venta_{i}"):
                        conn = sqlite3.connect("barberia.db")
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM ventas WHERE fecha = ? AND producto = ? AND cantidad = ? AND total = ? LIMIT 1",
                                       (v[0], v[1], v[2], v[3]))
                        conn.commit()
                        conn.close()
                        st.success("✅ Venta eliminada")
                        st.experimental_rerun()
    else:
        st.info("No hay ventas registradas.")
elif opcion == "Inventario":
    st.subheader("📦 Gestión de Inventario")

    with st.form("form_inventario"):
        nombre = st.text_input("Nombre del producto")
        stock = st.number_input("Cantidad disponible", min_value=0, step=1)
        precio = st.number_input("Precio unitario (₡)", min_value=0.0, step=100.0, format="%.2f")
        guardar = st.form_submit_button("Guardar")

        if guardar and nombre:
            registrar_producto(nombre, stock, precio)
            st.success("✅ Producto registrado correctamente")
            st.experimental_rerun()

    st.subheader("📋 Productos registrados")
    productos = obtener_productos()
    if productos:
        for i, p in enumerate(productos):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 1])
            col1.write(f"🧴 {p[1]}")
            col2.write(f"{p[2]} ud.")
            col3.write(f"₡{p[3]:,.2f}")

            if p[2] < 3:
                col3.markdown("⚠️ <span style='color:red'>Stock bajo</span>", unsafe_allow_html=True)

            with col4:
                if st.button("✏️", key=f"edit_{i}"):
                    nuevo_stock = st.number_input("Nuevo stock", value=p[2], key=f"new_stock_{i}")
                    nuevo_precio = st.number_input("Nuevo precio", value=p[3], key=f"new_price_{i}", format="%.2f")
                    if st.button("Actualizar", key=f"update_{i}"):
                        actualizar_producto(p[0], nuevo_stock, nuevo_precio)
                        st.success("✅ Producto actualizado")
                        st.experimental_rerun()
            with col5:
                if st.button("🗑️", key=f"del_{i}"):
                    eliminar_producto(p[0])
                    st.success("✅ Producto eliminado")
                    st.experimental_rerun()
    else:
        st.info("No hay productos registrados.")
