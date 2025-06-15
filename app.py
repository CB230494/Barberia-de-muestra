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

# Estilos personalizados
st.markdown("""
    <style>
    /* Botones */
    .stButton>button {
        background-color: #005caa;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0b72c1;
    }

    /* Menú lateral azul */
    .css-1v0mbdj.ef3psqc12 {
        background-color: #005caa !important;
        border-radius: 10px;
        color: white !important;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease-in-out;
    }
    .css-1v0mbdj.ef3psqc12:hover {
        background-color: #0b72c1 !important;
        transform: scale(1.02);
    }

    /* Eliminar color de fondo general */
    html, body, .main, .stApp {
        background-color: white;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# Menú lateral
st.sidebar.title("Menú")
opcion = st.sidebar.radio("Ir a:", ["Registro de cortes", "Gestión mensual y ventas", "Inventario"])

# Encabezado general
st.markdown("## 💈 Sistema de Gestión para Barbería")


# Registro de cortes (Parte básica)
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
    if resumen and resumen[0]:
        st.success(f"💇‍♂️ Total de cortes: **{resumen[0]}** — 💰 Ganancia acumulada: **₡{resumen[1]:,.2f}**")
    else:
        st.info("Aún no se han registrado datos para mostrar el resumen.")
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

    st.subheader(f"📊 Resumen de {meses[mes]} {anio}")
    if resumen["cortes_realizados"]:
        st.write(f"💈 Cortes: **{resumen['cortes_realizados']}**")
        st.write(f"💰 Ganancia por cortes: **₡{resumen['ganancia_cortes']:,.2f}**")
        st.write(f"🧴 Productos vendidos: **{resumen['productos_vendidos']}**")
        st.write(f"💵 Ganancia por ventas: **₡{resumen['ganancia_ventas']:,.2f}**")
    else:
        st.info("No hay registros para este mes.")

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

    st.markdown("Registra productos usados o vendidos, como cremas, ceras, etc.")

    with st.form("form_inventario"):
        nombre = st.text_input("Nombre del producto")
        tipo = st.selectbox("Tipo", ["Uso interno", "Venta"])
        cantidad = st.number_input("Cantidad disponible", min_value=0, step=1)
        precio_unitario = st.number_input("Precio unitario (₡)", min_value=0.0, step=100.0, format="%.2f")
        registrar_p = st.form_submit_button("Agregar al inventario")
        if registrar_p and nombre:
            registrar_producto(nombre, tipo, cantidad, precio_unitario)
            st.success("✅ Producto registrado")
            st.experimental_rerun()

    st.subheader("📋 Productos en inventario")

    productos = obtener_productos()
    if productos:
        for i, p in enumerate(productos):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            col1.write(f"🧴 {p[0]}")
            col2.write(f"🔖 {p[1]}")
            col3.write(f"📦 {p[2]} ud.")
            col4.write(f"₡{p[3]:,.2f}")

            if p[2] < 3:
                st.warning(f"⚠️ Bajo stock: {p[0]} tiene solo {p[2]} unidades")

            with col5:
                if st.button("🗑️", key=f"del_inv_{i}"):
                    eliminar_producto(p[0], p[1])
                    st.success("✅ Producto eliminado")
                    st.experimental_rerun()

                with st.expander("✏️ Editar", expanded=False):
                    nuevo_nombre = st.text_input("Nuevo nombre", value=p[0], key=f"nomb_{i}")
                    nuevo_tipo = st.selectbox("Nuevo tipo", ["Uso interno", "Venta"], index=0 if p[1] == "Uso interno" else 1, key=f"tipo_{i}")
                    nueva_cant = st.number_input("Nueva cantidad", value=p[2], step=1, key=f"cant_{i}")
                    nuevo_precio = st.number_input("Nuevo precio (₡)", value=p[3], step=100.0, format="%.2f", key=f"prec_{i}")
                    if st.button("Guardar cambios", key=f"edit_inv_{i}"):
                        actualizar_producto(p[0], p[1], nuevo_nombre, nuevo_tipo, nueva_cant, nuevo_precio)
                        st.success("✅ Producto actualizado")
                        st.experimental_rerun()
    else:
        st.info("No hay productos en el inventario.")


