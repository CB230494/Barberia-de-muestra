import streamlit as st
from datetime import date
import calendar
from database import (
    init_db, registrar_cortes, obtener_registros, actualizar_corte, eliminar_corte,
    obtener_resumen, obtener_cortes_por_mes, registrar_venta, obtener_ventas,
    registrar_gasto, obtener_gastos_por_mes, obtener_resumen_mensual,
    registrar_producto, obtener_productos, actualizar_producto, eliminar_producto
)

# Inicializa la base de datos
init_db()

# Configuración de página
st.set_page_config(page_title="Barbería App", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
    /* Menú lateral */
    section[data-testid="stSidebar"] {
        background-color: #003366;
    }
    section[data-testid="stSidebar"] .st-bk {
        color: white;
    }
    /* Botones tipo 3D */
    div.stButton > button {
        background-color: #800000;
        color: white;
        border: none;
        padding: 10px 16px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #990000;
        transform: scale(1.03);
    }
    /* Cajas de info */
    .info-card {
        background-color: #f7f7f7;
        padding: 15px;
        border-left: 5px solid #003366;
        margin-bottom: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Menú lateral
opcion = st.sidebar.radio("Menú Principal", ["Registro de cortes", "Gestión mensual y ventas", "Inventario"])

# Encabezado general
st.title("💈 Sistema de Gestión - Barbería Moderna")
if opcion == "Registro de cortes":
    st.subheader("✂️ Registro de Cortes Diarios")

    with st.form("form_cortes"):
        fecha = st.date_input("Fecha", value=date.today())
        cantidad = st.number_input("Cantidad de cortes", min_value=0, step=1)
        ganancia = st.number_input("Ganancia total (₡)", min_value=0.0, step=100.0, format="%.2f")
        submitted = st.form_submit_button("Guardar")
        if submitted:
            exito = registrar_cortes(str(fecha), cantidad, ganancia)
            if exito:
                st.success("✅ Cortes registrados correctamente.")
            else:
                st.warning("⚠️ Ya existen cortes para esa fecha. Si desea cambiar los datos, edite el registro.")
    
    st.markdown("---")
    st.subheader("📅 Historial de cortes")

    registros = obtener_registros()
    for reg in registros:
        fecha, cantidad, ganancia = reg
        with st.expander(f"{fecha} — {cantidad} cortes — ₡{ganancia:,.2f}"):
            nueva_cantidad = st.number_input(f"Cantidad ({fecha})", value=cantidad, key=f"cantidad_{fecha}", step=1)
            nueva_ganancia = st.number_input(f"Ganancia ({fecha})", value=ganancia, key=f"ganancia_{fecha}", step=100.0, format="%.2f")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Actualizar", key=f"act_{fecha}"):
                    actualizar_corte(fecha, nueva_cantidad, nueva_ganancia)
                    st.success("✅ Registro actualizado.")
                    st.experimental_rerun()
            with col2:
                if st.button("Eliminar", key=f"elim_{fecha}"):
                    eliminar_corte(fecha)
                    st.warning("🗑️ Registro eliminado.")
                    st.experimental_rerun()

    st.markdown("---")
    st.subheader("📊 Resumen general")
    total_cortes, total_ganancias = obtener_resumen()
    st.markdown(f'<div class="info-card">✂️ Total de cortes: <strong>{total_cortes}</strong></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">💰 Ganancias acumuladas: <strong>₡{total_ganancias:,.2f}</strong></div>', unsafe_allow_html=True)
elif opcion == "Gestión mensual y ventas":
    st.subheader("📆 Parte Media del Proyecto: Gestión mensual, ventas y control de gastos")
    st.markdown("Esta sección incluye todas las funciones básicas, más el control mensual y registro de ventas/gastos.")

    meses_es = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
        "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }

    mes_nombre = st.selectbox("Seleccione el mes", list(meses_es.keys()))
    anio = st.number_input("Año", min_value=2020, max_value=2100, value=date.today().year)
    mes = meses_es[mes_nombre]

    st.markdown("### 📌 Cortes del mes seleccionado")
    cortes_mes = obtener_cortes_por_mes(anio, mes)
    for f, c, g in cortes_mes:
        st.markdown(f"- {f}: {c} cortes — ₡{g:,.2f}")

    st.markdown("---")
    st.markdown("### 🧴 Registro de venta de productos")
    with st.form("form_ventas"):
        fecha_venta = st.date_input("Fecha de venta", value=date.today(), key="fecha_venta")
        producto = st.text_input("Producto vendido", key="producto")
        cantidad = st.number_input("Cantidad", min_value=1, step=1, key="cantidad")
        total = st.number_input("Total ₡", min_value=0.0, step=100.0, format="%.2f", key="total")
        venta_guardada = st.form_submit_button("Registrar venta")
        if venta_guardada:
            registrar_venta(str(fecha_venta), producto, cantidad, total)
            st.success("✅ Venta registrada.")

    st.markdown("### 📌 Registro de gastos")
    with st.form("form_gastos"):
        fecha_gasto = st.date_input("Fecha del gasto", value=date.today(), key="fecha_gasto")
        descripcion = st.text_input("Descripción del gasto", key="desc_gasto")
        monto = st.number_input("Monto ₡", min_value=0.0, step=100.0, format="%.2f", key="monto_gasto")
        gasto_guardado = st.form_submit_button("Registrar gasto")
        if gasto_guardado:
            registrar_gasto(str(fecha_gasto), descripcion, monto)
            st.success("✅ Gasto registrado.")

    st.markdown("---")
    st.markdown("### 📈 Resumen del mes")
    resumen = obtener_resumen_mensual(anio, mes)
    st.markdown(f'<div class="info-card">✂️ Cortes realizados: <strong>{resumen["cortes_realizados"]}</strong></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">💰 Ganancia por cortes: <strong>₡{resumen["ganancia_cortes"]:,.2f}</strong></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">🧴 Productos vendidos: <strong>{resumen["productos_vendidos"]}</strong></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">💸 Ganancia por ventas: <strong>₡{resumen["ganancia_ventas"]:,.2f}</strong></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">📉 Total de gastos: <strong>₡{resumen["total_gastos"]:,.2f}</strong></div>', unsafe_allow_html=True)
elif opcion == "Inventario":
    st.subheader("📦 Gestión de Inventario")

    st.markdown("### ➕ Agregar producto al inventario")
    with st.form("form_inventario"):
        nombre = st.text_input("Nombre del producto", key="nombre_inv")
        cantidad = st.number_input("Cantidad", min_value=0, step=1, key="cantidad_inv")
        costo = st.number_input("Costo ₡", min_value=0.0, step=100.0, format="%.2f", key="costo_inv")
        agregar = st.form_submit_button("Guardar producto")
        if agregar and nombre:
            registrar_producto(nombre, cantidad, costo)
            st.success(f"✅ Producto '{nombre}' agregado.")

    st.markdown("### 📋 Productos registrados")
    productos = obtener_productos()

    for p in productos:
        nombre, cantidad, costo = p
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"- **{nombre}** — Cantidad: {cantidad}, Costo: ₡{costo:,.2f}")
            if cantidad < 3:
                st.warning("⚠️ Bajo stock")

        with col2:
            editar = st.button(f"✏️", key=f"edit_{nombre}")
            eliminar = st.button(f"🗑️", key=f"del_{nombre}")

        if editar:
            with st.form(f"edit_form_{nombre}"):
                nueva_cantidad = st.number_input("Nueva cantidad", value=cantidad, min_value=0, step=1, key=f"new_qty_{nombre}")
                nuevo_costo = st.number_input("Nuevo costo ₡", value=costo, min_value=0.0, step=100.0, format="%.2f", key=f"new_cost_{nombre}")
                confirmar = st.form_submit_button("Actualizar")
                if confirmar:
                    actualizar_producto(nombre, nueva_cantidad, nuevo_costo)
                    st.success("✅ Producto actualizado.")
                    st.experimental_rerun()

        if eliminar:
            eliminar_producto(nombre)
            st.warning(f"🗑️ Producto '{nombre}' eliminado.")
            st.experimental_rerun()



