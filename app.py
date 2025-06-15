import streamlit as st
from database import (
    init_db,
    registrar_cortes,
    obtener_registros,
    obtener_resumen,
    obtener_cortes_por_mes,
    eliminar_corte,
    actualizar_corte,
    registrar_venta,
    obtener_ventas,
    obtener_resumen_mensual,
    registrar_producto,
    obtener_productos,
    eliminar_producto,
    actualizar_producto,
    registrar_gasto,
    obtener_gastos_por_mes
)
from datetime import date
import calendar

# Inicializar base de datos
init_db()

# Estilo visual
st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background-color: #002244 !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    .stButton > button {
        background-color: #8B0000;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
    }
    .stButton > button:hover {
        background-color: #B22222;
    }
    html, body, .stApp {
        background-color: white;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# Menú lateral
st.sidebar.title("📋 Menú")
opcion = st.sidebar.radio("Ir a:", ["Registro de cortes", "Gestión mensual y ventas", "Inventario"])

# Título principal
st.markdown("## 💈 Sistema de Gestión para Barbería")
if opcion == "Registro de cortes":
    st.subheader("✂️ Registro de cortes del día")

    with st.form(key="registro_cortes_form"):
        fecha = st.date_input("Fecha", value=date.today())
        cantidad = st.number_input("Cantidad de cortes", min_value=0, step=1)
        ganancia = st.number_input("Ganancia total (₡)", min_value=0.0, step=1000.0, format="%.2f")
        guardar = st.form_submit_button("Guardar")

    if guardar:
        fecha_str = fecha.strftime("%Y-%m-%d")
        if registrar_cortes(fecha_str, cantidad, ganancia):
            st.success("✅ Registro guardado correctamente.")
        else:
            st.warning("⚠️ Ya existe un registro para esta fecha.")

    st.markdown("---")
    st.subheader("📆 Historial de cortes")

    registros = obtener_registros()
    for r in registros:
        with st.expander(f"{r[0]} — {r[1]} cortes — ₡{r[2]:,.2f}"):
            nueva_cantidad = st.number_input(f"✏️ Cantidad ({r[0]})", value=r[1], key=f"cantidad_{r[0]}")
            nueva_ganancia = st.number_input(f"💰 Ganancia ({r[0]})", value=r[2], step=1000.0, format="%.2f", key=f"ganancia_{r[0]}")
            if st.button("Actualizar", key=f"act_{r[0]}"):
                actualizar_corte(r[0], nueva_cantidad, nueva_ganancia)
                st.success("✅ Registro actualizado.")
                st.experimental_rerun()
            if st.button("Eliminar", key=f"elim_{r[0]}"):
                eliminar_corte(r[0])
                st.warning("🗑️ Registro eliminado.")
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("📊 Resumen general")

    total_cortes, total_ganancias = obtener_resumen()
    st.markdown(f"**Total de cortes registrados:** {total_cortes}")
    st.markdown(f"**Ganancias acumuladas:** ₡{total_ganancias:,.2f}")
elif opcion == "Gestión mensual y ventas":
    st.subheader("📅 Gestión mensual y control de ventas")

    anio = st.number_input("Seleccione el año", value=date.today().year, step=1)

    meses_es = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
    ]
    mes = st.selectbox("Seleccione el mes", options=meses_es, format_func=lambda x: x[1])[0]

    resumen = obtener_resumen_mensual(anio, mes)

    st.markdown("---")
    st.markdown("### ✂️ Resumen de cortes")
    st.markdown(f"- Total de cortes: **{resumen['cortes_realizados']}**")
    st.markdown(f"- Ganancia por cortes: **₡{resumen['ganancia_cortes']:,.2f}**")

    st.markdown("### 🧴 Resumen de ventas de productos")
    st.markdown(f"- Productos vendidos: **{resumen['productos_vendidos']}**")
    st.markdown(f"- Ganancia por ventas: **₡{resumen['ganancia_ventas']:,.2f}**")

    st.markdown("### 💸 Resumen de gastos")
    st.markdown(f"- Total de gastos: **₡{resumen['total_gastos']:,.2f}**")

    st.markdown("---")
    st.subheader("🛒 Registro de venta de productos")

    with st.form("form_venta"):
        fecha_venta = st.date_input("Fecha de venta", value=date.today())
        producto = st.text_input("Producto vendido")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        total = st.number_input("Total ₡", min_value=0.0, step=1000.0, format="%.2f")
        if st.form_submit_button("Registrar venta"):
            registrar_venta(fecha_venta.strftime("%Y-%m-%d"), producto, cantidad, total)
            st.success("✅ Venta registrada correctamente.")
            st.experimental_rerun()

    st.subheader("💼 Registro de gastos")

    with st.form("form_gasto"):
        fecha_gasto = st.date_input("Fecha del gasto", value=date.today())
        descripcion = st.text_input("Descripción del gasto")
        monto = st.number_input("Monto ₡", min_value=0.0, step=1000.0, format="%.2f")
        if st.form_submit_button("Registrar gasto"):
            registrar_gasto(fecha_gasto.strftime("%Y-%m-%d"), descripcion, monto)
            st.success("✅ Gasto registrado correctamente.")
            st.experimental_rerun()
elif opcion == "Inventario":
    st.subheader("📦 Gestión de Inventario")

    with st.form("form_inventario"):
        nombre = st.text_input("Nombre del producto")
        cantidad = st.number_input("Cantidad en stock", min_value=0, step=1)
        costo = st.number_input("Costo unitario (₡)", min_value=0.0, step=100.0, format="%.2f")
        if st.form_submit_button("Registrar producto"):
            registrar_producto(nombre, cantidad, costo)
            st.success("✅ Producto registrado correctamente.")
            st.experimental_rerun()

    st.markdown("---")
    st.subheader("📋 Productos registrados")

    productos = obtener_productos()
    for p in productos:
        nombre, cantidad, costo = p
        alerta = " 🔴 Bajo stock" if cantidad < 3 else ""
        with st.expander(f"{nombre} — {cantidad} unidades — ₡{costo:,.2f}{alerta}"):
            nueva_cantidad = st.number_input(f"Cantidad ({nombre})", value=cantidad, step=1, key=f"cant_{nombre}")
            nuevo_costo = st.number_input(f"Costo ({nombre})", value=costo, step=100.0, format="%.2f", key=f"cost_{nombre}")
            if st.button("Actualizar", key=f"act_{nombre}"):
                actualizar_producto(nombre, nueva_cantidad, nuevo_costo)
                st.success("✅ Producto actualizado.")
                st.experimental_rerun()
            if st.button("Eliminar", key=f"elim_{nombre}"):
                eliminar_producto(nombre)
                st.warning("🗑️ Producto eliminado.")
                st.experimental_rerun()



