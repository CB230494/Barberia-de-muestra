# ---------------------------------------------
# 📋 SISTEMA DE CONTROL PARA BARBERÍA - STREAMLIT
# Pestaña 1: ✂️ Registro de Cortes
# ---------------------------------------------

import streamlit as st
import pandas as pd
import io
from datetime import date
from database import (
    insertar_corte,
    obtener_cortes,
    eliminar_corte,
    actualizar_corte
)

# -----------------------------
# 🎛️ Configuración de la app
# -----------------------------
st.set_page_config(
    page_title="Barbería - Registro de Cortes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# 📌 Menú lateral
# -----------------------------
menu = st.sidebar.radio(
    "Selecciona una sección",
    [
        "✂️ Registro de Cortes",
        "📦 Inventario",
        "📅 Citas",
        "💵 Finanzas",
        "📊 Reporte General"
    ]
)

# ---------------------------------------------
# ✂️ PESTAÑA 1: Registro de Cortes
# ---------------------------------------------
if menu == "✂️ Registro de Cortes":
    st.title("✂️ Registro de Cortes Realizados")
    st.markdown("Agrega, consulta o elimina cortes realizados por los barberos.")

    # ---------- FORMULARIO NUEVO CORTE ----------
    st.subheader("➕ Agregar nuevo corte")

    with st.form("form_nuevo_corte"):
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha = st.date_input("Fecha", value=date.today())
        with col2:
            barbero = st.text_input("Nombre del barbero")
        with col3:
            cliente = st.text_input("Nombre del cliente")

        tipo_corte = st.selectbox("Tipo de corte", ["Clásico", "Fade", "Diseño", "Barba", "Otro"])
        precio = st.number_input("Precio (₡)", min_value=0.0, step=500.0, format="%.2f")
        observacion = st.text_area("Observaciones (opcional)")
        submitted = st.form_submit_button("💾 Guardar")

        if submitted:
            if not barbero.strip() or not cliente.strip():
                st.warning("⚠️ Barbero y Cliente son campos obligatorios.")
            else:
                insertar_corte(str(fecha), barbero.strip(), cliente.strip(), tipo_corte, precio, observacion.strip())
                st.success("✅ Corte registrado correctamente")
                st.rerun()

    st.divider()

    # ---------- LISTADO DE CORTES REGISTRADOS ----------
    st.subheader("📋 Historial de cortes")

    cortes = obtener_cortes()
    if cortes:
        df = pd.DataFrame(cortes)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
        df["precio"] = df["precio"].map(lambda x: round(x, 2))

        # Botón para descargar respaldo en Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Cortes")
        st.download_button(
            label="⬇️ Descargar respaldo en Excel",
            data=output.getvalue(),
            file_name="cortes_registrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Mostrar los cortes en tarjetas editables
        for corte in cortes:
            with st.container():
                id_corte = corte["id"]
                editar = st.session_state.get(f"edit_{id_corte}", False)

                if editar:
                    st.markdown(f"### ✏️ Editando corte ID {id_corte}")
                    f = st.date_input("Fecha", value=pd.to_datetime(corte["fecha"]), key=f"fecha_{id_corte}")
                    b = st.text_input("Barbero", value=corte["barbero"], key=f"barbero_{id_corte}")
                    c = st.text_input("Cliente", value=corte["cliente"], key=f"cliente_{id_corte}")
                    t = st.selectbox("Tipo de corte", ["Clásico", "Fade", "Diseño", "Barba", "Otro"], index=0, key=f"tipo_{id_corte}")
                    p = st.number_input("Precio (₡)", value=float(corte["precio"]), step=500.0, format="%.2f", key=f"precio_{id_corte}")
                    o = st.text_area("Observación", value=corte["observacion"] or "", key=f"obs_{id_corte}")

                    col1, col2 = st.columns(2)
                    if col1.button("💾 Guardar", key=f"guardar_{id_corte}"):
                        actualizar_corte(id_corte, {
                            "fecha": str(f),
                            "barbero": b,
                            "cliente": c,
                            "tipo_corte": t,
                            "precio": p,
                            "observacion": o
                        })
                        st.session_state[f"edit_{id_corte}"] = False
                        st.success("✅ Corte actualizado")
                        st.rerun()
                    if col2.button("❌ Cancelar", key=f"cancelar_{id_corte}"):
                        st.session_state[f"edit_{id_corte}"] = False
                        st.rerun()
                else:
                    cols = st.columns([1.5, 2, 2, 2, 1.5, 3, 1, 1])
                    cols[0].markdown(f"🗓️ **{corte['fecha']}**")
                    cols[1].markdown(f"💈 **{corte['barbero']}**")
                    cols[2].markdown(f"👤 {corte['cliente']}")
                    cols[3].markdown(f"✂️ {corte['tipo_corte']}")
                    cols[4].markdown(f"💰 ₡{corte['precio']:,.2f}")
                    cols[5].markdown(f"📝 {corte['observacion'] or '—'}")
                    if cols[6].button("✏️", key=f"edit_{id_corte}"):
                        st.session_state[f"edit_{id_corte}"] = True
                        st.rerun()
                    if cols[7].button("🗑️", key=f"delete_{id_corte}"):
                        eliminar_corte(id_corte)
                        st.success("✅ Corte eliminado")
                        st.rerun()
    else:
        st.info("Aún no se han registrado cortes.")
# ---------------------------------------------
# 📦 PESTAÑA 2: Inventario
# ---------------------------------------------
elif menu == "📦 Inventario":
    from database import insertar_producto, obtener_productos  # puedes añadir editar/eliminar más adelante

    st.title("📦 Inventario de Productos")
    st.markdown("Registra productos para su venta en la barbería y controla su stock.")

    # ---------- FORMULARIO: AGREGAR PRODUCTO ----------
    st.subheader("➕ Agregar nuevo producto")

    with st.form("form_nuevo_producto"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre del producto")
        precio_unitario = col2.number_input("Precio unitario (₡)", min_value=0.0, step=100.0, format="%.2f")
        descripcion = st.text_input("Descripción (opcional)")
        stock = st.number_input("Stock inicial", min_value=0, step=1)
        enviado = st.form_submit_button("💾 Guardar producto")

        if enviado:
            if not nombre.strip():
                st.warning("⚠️ El nombre del producto es obligatorio.")
            elif stock < 0:
                st.warning("⚠️ El stock no puede ser negativo.")
            else:
                insertar_producto(nombre.strip(), descripcion.strip(), stock, precio_unitario)
                st.success("✅ Producto registrado correctamente")
                st.rerun()

    st.divider()

    # ---------- LISTADO DE PRODUCTOS ----------
    st.subheader("📋 Productos en inventario")

    productos = obtener_productos()
    if productos:
        df_prod = pd.DataFrame(productos)
        df_prod["precio_unitario"] = df_prod["precio_unitario"].map(lambda x: round(x, 2))

        # Botón de descarga Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_prod.to_excel(writer, index=False, sheet_name="Productos")
        st.download_button(
            label="⬇️ Descargar inventario en Excel",
            data=output.getvalue(),
            file_name="inventario_productos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.dataframe(df_prod, use_container_width=True)
    else:
        st.info("No hay productos registrados todavía.")



