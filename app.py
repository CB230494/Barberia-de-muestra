# ---------------------------------------------
# 📋 SISTEMA DE CONTROL PARA BARBERÍA - STREAMLIT
# app.py – TODO en un solo archivo, backend Google Sheets incluido
# ---------------------------------------------
import streamlit as st
import pandas as pd
import io
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional

# ==== PDF (Reporte General) ====
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# ==== Google Sheets ====
import gspread

# -----------------------------
# 🎛️ Configuración de la app
# -----------------------------
st.set_page_config(
    page_title="Barbería - Control General",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 🔌 BACKEND GOOGLE SHEETS (incluido en este archivo)
# ============================================================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1cs5I7U_nEHY7B0qCkA3WvY5_Y5hd97bd2nuifPrK6Jw/edit?usp=sharing"

SCHEMAS: Dict[str, List[str]] = {
    "Cortes":    ["id", "fecha", "barbero", "cliente", "tipo_corte", "precio", "observacion"],
    "Productos": ["id", "nombre", "descripcion", "stock", "precio_unitario"],
    "Citas":     ["id", "fecha", "hora", "cliente_nombre", "barbero", "servicio", "estado"],
    "Ingresos":  ["id", "fecha", "concepto", "monto", "observacion"],
    "Gastos":    ["id", "fecha", "concepto", "monto", "observacion"],
}

# ---- Conexión gspread
@st.cache_resource(show_spinner=False)
def _gc():
    sa = st.secrets.get("gcp_service_account")
    if not sa:
        raise RuntimeError("Falta st.secrets['gcp_service_account']. Sube tu JSON del Service Account a st.secrets y comparte la hoja con ese correo (Editor).")
    return gspread.service_account_from_dict(dict(sa))

@st.cache_resource(show_spinner=False)
def _open_sheet():
    gc = _gc()
    return gc.open_by_url(SPREADSHEET_URL)

def _get_ws(title: str):
    sh = _open_sheet()
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=2000, cols=20)
        ws.append_row(SCHEMAS[title])
    # Garantiza cabeceras correctas
    headers = ws.row_values(1)
    if headers != SCHEMAS[title]:
        if headers:
            ws.delete_rows(1)
        ws.insert_row(SCHEMAS[title], 1)
    return ws

def _next_id(ws) -> int:
    ids = ws.col_values(1)[1:]
    nums = []
    for v in ids:
        try:
            nums.append(int(str(v).strip()))
        except:
            pass
    return (max(nums) + 1) if nums else 1

def _read_all(sheet: str) -> List[Dict[str, Any]]:
    ws = _get_ws(sheet)
    rows = ws.get_all_records()
    for r in rows:
        if "id" in r:
            try: r["id"] = int(r["id"])
            except: pass
        for k in ("precio", "precio_unitario", "monto", "stock"):
            if k in r and str(r[k]).strip() != "":
                try: r[k] = float(str(r[k]).replace(",", "."))
                except: pass
    return rows

def _find_row_by_id(ws, _id: int) -> Optional[int]:
    vals = ws.col_values(1)
    for idx, v in enumerate(vals, start=1):
        if idx == 1:  # cabecera
            continue
        try:
            if int(str(v).strip()) == int(_id):
                return idx
        except:
            continue
    return None

def _append(sheet: str, values: Dict[str, Any]):
    ws = _get_ws(sheet)
    ordered = [values.get(k, "") for k in SCHEMAS[sheet]]
    ws.append_row(ordered, value_input_option="USER_ENTERED")

def _update(sheet: str, _id: int, values: Dict[str, Any]):
    ws = _get_ws(sheet)
    row = _find_row_by_id(ws, _id)
    if not row:
        return
    colmap = {name: i+1 for i, name in enumerate(SCHEMAS[sheet])}
    for k, v in values.items():
        if k not in colmap: 
            continue
        ws.update_cell(row, colmap[k], v)

def _delete(sheet: str, _id: int):
    ws = _get_ws(sheet)
    row = _find_row_by_id(ws, _id)
    if row:
        ws.delete_rows(row)

# ---- Funciones específicas (mismo nombre que usabas)
# Cortes
def insertar_corte(fecha: str, barbero: str, cliente: str, tipo_corte: str, precio: float, observacion: str):
    ws = _get_ws("Cortes")
    _append("Cortes", {
        "id": _next_id(ws),
        "fecha": fecha,
        "barbero": barbero,
        "cliente": cliente,
        "tipo_corte": tipo_corte,
        "precio": precio,
        "observacion": observacion
    })

def obtener_cortes() -> List[Dict[str, Any]]:
    return _read_all("Cortes")

def actualizar_corte(_id: int, values: Dict[str, Any]):
    _update("Cortes", _id, values)

def eliminar_corte(_id: int):
    _delete("Cortes", _id)

# Productos
def insertar_producto(nombre: str, descripcion: str, stock: int, precio_unitario: float):
    ws = _get_ws("Productos")
    _append("Productos", {
        "id": _next_id(ws),
        "nombre": nombre,
        "descripcion": descripcion,
        "stock": stock,
        "precio_unitario": precio_unitario
    })

def obtener_productos() -> List[Dict[str, Any]]:
    return _read_all("Productos")

def actualizar_producto(_id: int, values: Dict[str, Any]):
    _update("Productos", _id, values)

def eliminar_producto(_id: int):
    _delete("Productos", _id)

# Citas
def insertar_cita(fecha: str, hora: str, cliente_nombre: str, barbero: str, servicio: str):
    ws = _get_ws("Citas")
    _append("Citas", {
        "id": _next_id(ws),
        "fecha": fecha,
        "hora": hora,
        "cliente_nombre": cliente_nombre,
        "barbero": barbero,
        "servicio": servicio,
        "estado": "pendiente"
    })

def obtener_citas() -> List[Dict[str, Any]]:
    return _read_all("Citas")

def actualizar_cita(_id: int, values: Dict[str, Any]):
    _update("Citas", _id, values)

def actualizar_estado_cita(_id: int, nuevo_estado: str):
    _update("Citas", _id, {"estado": nuevo_estado})

def eliminar_cita(_id: int):
    _delete("Citas", _id)

# Ingresos / Gastos
def insertar_ingreso(fecha: str, concepto: str, monto: float, observacion: str):
    ws = _get_ws("Ingresos")
    _append("Ingresos", {
        "id": _next_id(ws),
        "fecha": fecha,
        "concepto": concepto,
        "monto": monto,
        "observacion": observacion
    })

def obtener_ingresos() -> List[Dict[str, Any]]:
    return _read_all("Ingresos")

def actualizar_ingreso(_id: int, values: Dict[str, Any]):
    _update("Ingresos", _id, values)

def eliminar_ingreso(_id: int):
    _delete("Ingresos", _id)

def insertar_gasto(fecha: str, concepto: str, monto: float, observacion: str):
    ws = _get_ws("Gastos")
    _append("Gastos", {
        "id": _next_id(ws),
        "fecha": fecha,
        "concepto": concepto,
        "monto": monto,
        "observacion": observacion
    })

def obtener_gastos() -> List[Dict[str, Any]]:
    return _read_all("Gastos")

def actualizar_gasto(_id: int, values: Dict[str, Any]):
    _update("Gastos", _id, values)

def eliminar_gasto(_id: int):
    _delete("Gastos", _id)

# ============================================================
# 🧭 UI – Misma app que ya tenías (con las 5 pestañas)
# ============================================================
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
    st.subheader("📋 Historial de cortes")

    cortes = obtener_cortes()
    if cortes:
        df = pd.DataFrame(cortes)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
        df["precio"] = df["precio"].map(lambda x: round(x, 2) if isinstance(x, (float, int)) else x)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Cortes")
        st.download_button(
            label="⬇️ Descargar respaldo en Excel",
            data=output.getvalue(),
            file_name="cortes_registrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        for corte in cortes:
            with st.container():
                id_corte = int(corte["id"])
                editar = st.session_state.get(f"edit_{id_corte}", False)

                if editar:
                    st.markdown(f"### ✏️ Editando corte ID {id_corte}")
                    f = st.date_input("Fecha", value=pd.to_datetime(corte["fecha"]), key=f"fecha_{id_corte}")
                    b = st.text_input("Barbero", value=corte["barbero"], key=f"barbero_{id_corte}")
                    c = st.text_input("Cliente", value=corte["cliente"], key=f"cliente_{id_corte}")
                    tipos = ["Clásico", "Fade", "Diseño", "Barba", "Otro"]
                    try:
                        idx = tipos.index(corte["tipo_corte"])
                    except:
                        idx = 0
                    t = st.selectbox("Tipo de corte", tipos, index=idx, key=f"tipo_{id_corte}")
                    p = st.number_input("Precio (₡)", value=float(corte.get("precio") or 0), step=500.0, format="%.2f", key=f"precio_{id_corte}")
                    o = st.text_area("Observación", value=corte.get("observacion") or "", key=f"obs_{id_corte}")

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
                    cols[0].markdown(f"🗓️ **{pd.to_datetime(corte['fecha']).strftime('%d/%m/%Y')}**")
                    cols[1].markdown(f"💈 **{corte['barbero']}**")
                    cols[2].markdown(f"👤 {corte['cliente']}")
                    cols[3].markdown(f"✂️ {corte['tipo_corte']}")
                    precio_val = corte.get("precio")
                    try:
                        precio_val = float(precio_val)
                        cols[4].markdown(f"💰 ₡{precio_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    except:
                        cols[4].markdown(f"💰 ₡{precio_val}")
                    cols[5].markdown(f"📝 {corte.get('observacion') or '—'}")
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
    st.title("📦 Inventario de Productos")
    st.markdown("Administra los productos disponibles y su stock.")

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
            else:
                insertar_producto(nombre.strip(), descripcion.strip(), stock, precio_unitario)
                st.success("✅ Producto registrado correctamente")
                st.rerun()

    st.divider()
    st.subheader("📋 Productos en inventario")

    productos = obtener_productos()
    if productos:
        df = pd.DataFrame(productos)
        def fnum(v): 
            try: return float(v)
            except: return v
        df["precio_unitario"] = df["precio_unitario"].map(fnum)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Productos")
        st.download_button(
            label="⬇️ Descargar inventario en Excel",
            data=output.getvalue(),
            file_name="inventario_productos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        for producto in productos:
            id_producto = int(producto["id"])
            editando = st.session_state.get(f"edit_prod_{id_producto}", False)

            if editando:
                st.markdown(f"### ✏️ Editando producto ID {id_producto}")
                col1, col2 = st.columns(2)
                nombre_edit = col1.text_input("Nombre", value=producto["nombre"], key=f"nombre_{id_producto}")
                precio_edit = col2.number_input("Precio (₡)", value=float(producto.get("precio_unitario") or 0), step=100.0, format="%.2f", key=f"precio_{id_producto}")
                descripcion_edit = st.text_input("Descripción", value=producto.get("descripcion") or "", key=f"desc_{id_producto}")
                stock_edit = st.number_input("Stock", value=int(float(producto.get("stock") or 0)), step=1, key=f"stock_{id_producto}")
                col1b, col2b = st.columns(2)
                if col1b.button("💾 Guardar", key=f"guardar_{id_producto}"):
                    actualizar_producto(id_producto, {
                        "nombre": nombre_edit,
                        "precio_unitario": precio_edit,
                        "descripcion": descripcion_edit,
                        "stock": stock_edit
                    })
                    st.session_state[f"edit_prod_{id_producto}"] = False
                    st.success("✅ Producto actualizado")
                    st.rerun()
                if col2b.button("❌ Cancelar", key=f"cancelar_{id_producto}"):
                    st.session_state[f"edit_prod_{id_producto}"] = False
                    st.rerun()
            else:
                cols = st.columns([2, 2, 2, 2, 1, 1])
                cols[0].markdown(f"📦 **{producto['nombre']}**")
                cols[1].markdown(f"🧾 {producto.get('descripcion') or '—'}")
                try:
                    cols[2].markdown(f"💰 ₡{float(producto.get('precio_unitario') or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                except:
                    cols[2].markdown(f"💰 ₡{producto.get('precio_unitario')}")
                cols[3].markdown(f"📦 Stock: {int(float(producto.get('stock') or 0))}")
                if cols[4].button("✏️", key=f"edit_{id_producto}"):
                    st.session_state[f"edit_prod_{id_producto}"] = True
                    st.rerun()
                if cols[5].button("🗑️", key=f"del_{id_producto}"):
                    eliminar_producto(id_producto)
                    st.success("✅ Producto eliminado")
                    st.rerun()
    else:
        st.info("No hay productos registrados todavía.")

# ---------------------------------------------
# 📅 PESTAÑA 3: Gestión de Citas (admin)
# ---------------------------------------------
elif menu == "📅 Citas":
    st.title("📅 Gestión de Citas")
    st.markdown("Revisa y administra las citas solicitadas por los clientes.")

    citas = obtener_citas()
    df = pd.DataFrame(citas)

    if df.empty:
        st.info("No hay citas registradas.")
    else:
        estados = ["todas", "pendiente", "aceptada", "rechazada"]
        estado_filtro = st.selectbox("🔍 Filtrar por estado", estados)

        if estado_filtro != "todas":
            df = df[df["estado"] == estado_filtro]

        for cita in df.to_dict(orient="records"):
            with st.container():
                cid = int(cita["id"])
                fecha_str = cita["fecha"]
                try:
                    fecha_str_show = pd.to_datetime(fecha_str).strftime("%d/%m/%Y")
                except:
                    fecha_str_show = fecha_str

                st.markdown(f"### 🧾 Cita ID {cid}")
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"**📅 Fecha:** {fecha_str_show}")
                col2.markdown(f"**🕒 Hora:** {cita['hora']}")
                col3.markdown(f"**🧴 Servicio:** {cita['servicio']}")
                st.markdown(f"**👤 Cliente:** {cita['cliente_nombre']}")
                st.markdown(f"**✂️ Barbero asignado:** {cita.get('barbero') or 'Sin asignar'}")
                st.markdown(f"**📌 Estado actual:** `{cita['estado']}`")

                with st.expander("✏️ Editar cita"):
                    # Fecha
                    try:
                        valor_fecha = datetime.strptime(cita["fecha"], "%Y-%m-%d").date()
                    except:
                        try:
                            valor_fecha = datetime.strptime(cita["fecha"], "%d/%m/%Y").date()
                        except:
                            valor_fecha = date.today()
                    nueva_fecha = st.date_input("📅 Nueva fecha", value=valor_fecha, key=f"fecha_{cid}")
                    # Hora
                    try:
                        hora_original = datetime.strptime(cita["hora"], "%H:%M").time()
                    except:
                        try:
                            hora_original = datetime.strptime(cita["hora"], "%H:%M:%S").time()
                        except:
                            hora_original = datetime.strptime("08:00", "%H:%M").time()
                    nueva_hora = st.time_input("🕒 Nueva hora", value=hora_original, key=f"hora_{cid}")
                    nuevo_barbero = st.text_input("✂️ Asignar barbero", value=cita.get("barbero") or "", key=f"barbero_{cid}")

                    col_e1, col_e2 = st.columns(2)
                    if col_e1.button("💾 Guardar cambios", key=f"guardar_cita_{cid}"):
                        actualizar_cita(cid, {
                            "fecha": nueva_fecha.strftime("%Y-%m-%d"),
                            "hora": nueva_hora.strftime("%H:%M"),
                            "barbero": nuevo_barbero
                        })
                        st.success("✅ Cita actualizada")
                        st.rerun()

                    if col_e2.button("🗑️ Eliminar cita", key=f"eliminar_cita_{cid}"):
                        eliminar_cita(cid)
                        st.success("✅ Cita eliminada")
                        st.rerun()

                col_a1, col_a2 = st.columns(2)
                if cita["estado"] == "pendiente":
                    if col_a1.button("✅ Aceptar", key=f"aceptar_{cid}"):
                        actualizar_estado_cita(cid, "aceptada")
                        st.success("📬 Cita aceptada")
                        st.rerun()
                    if col_a2.button("❌ Rechazar", key=f"rechazar_{cid}"):
                        actualizar_estado_cita(cid, "rechazada")
                        st.warning("📭 Cita rechazada")
                        st.rerun()

# ---------------------------------------------
# 💵 PESTAÑA 4: Finanzas
# ---------------------------------------------
elif menu == "💵 Finanzas":
    st.title("💵 Control de Finanzas")
    st.markdown("Registra ingresos y gastos de la barbería, y consulta el balance general.")

    # -------- Ingreso --------
    st.subheader("➕ Agregar Ingreso")
    with st.form("form_ingreso"):
        col1, col2 = st.columns(2)
        fecha_i = col1.date_input("Fecha del ingreso", value=date.today())
        concepto_i = col2.text_input("Concepto del ingreso")
        monto_i = st.number_input("Monto (₡)", min_value=0.0, step=500.0, format="%.2f", key="monto_ingreso")
        observacion_i = st.text_area("Observación (opcional)")
        enviar_i = st.form_submit_button("💾 Guardar ingreso")
        if enviar_i:
            if not concepto_i.strip():
                st.warning("⚠️ El concepto es obligatorio.")
            else:
                insertar_ingreso(str(fecha_i), concepto_i.strip(), monto_i, observacion_i.strip())
                st.success("✅ Ingreso registrado")
                st.rerun()

    # -------- Gasto --------
    st.subheader("➖ Agregar Gasto")
    with st.form("form_gasto"):
        col1, col2 = st.columns(2)
        fecha_g = col1.date_input("Fecha del gasto", value=date.today())
        concepto_g = col2.text_input("Concepto del gasto")
        monto_g = st.number_input("Monto (₡)", min_value=0.0, step=500.0, format="%.2f", key="monto_gasto")
        observacion_g = st.text_area("Observación (opcional)", key="obs_gasto")
        enviar_g = st.form_submit_button("💾 Guardar gasto")
        if enviar_g:
            if not concepto_g.strip():
                st.warning("⚠️ El concepto es obligatorio.")
            else:
                insertar_gasto(str(fecha_g), concepto_g.strip(), monto_g, observacion_g.strip())
                st.success("✅ Gasto registrado")
                st.rerun()

    st.divider()
    st.subheader("📊 Resumen de movimientos")

    ingresos = obtener_ingresos()
    gastos = obtener_gastos()

    df_i = pd.DataFrame(ingresos) if ingresos else pd.DataFrame()
    df_g = pd.DataFrame(gastos) if gastos else pd.DataFrame()

    total_i = sum(float(i.get("monto") or 0) for i in ingresos)
    total_g = sum(float(g.get("monto") or 0) for g in gastos)
    balance = total_i - total_g
    color = "green" if balance >= 0 else "red"

    st.markdown(f"**💰 Total Ingresos:** ₡{total_i:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown(f"**💸 Total Gastos:** ₡{total_g:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown(
        f"<strong>🧾 Balance general:</strong> <span style='color:{color}; font-weight:bold;'>₡{balance:,.2f}</span>"
        .replace(",", "X").replace(".", ",").replace("X", "."),
        unsafe_allow_html=True
    )

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📋 Ingresos")
        if not df_i.empty:
            df_i["fecha"] = pd.to_datetime(df_i["fecha"]).dt.strftime("%d/%m/%Y")
            df_i["monto"] = pd.to_numeric(df_i["monto"], errors="coerce")
            for ingreso in ingresos:
                _id = int(ingreso["id"])
                editando = st.session_state.get(f"edit_ingreso_{_id}", False)

                if editando:
                    st.markdown(f"#### ✏️ Editando ingreso ID {_id}")
                    f = st.date_input("Fecha", value=pd.to_datetime(ingreso["fecha"]), key=f"fecha_i_{_id}")
                    c = st.text_input("Concepto", value=ingreso["concepto"], key=f"concepto_i_{_id}")
                    m = st.number_input("Monto (₡)", value=float(ingreso.get("monto") or 0), key=f"monto_i_{_id}", step=500.0)
                    o = st.text_input("Observación", value=ingreso.get("observacion") or "", key=f"obs_i_{_id}")
                    col1a, col2a = st.columns(2)
                    if col1a.button("💾 Guardar", key=f"guardar_i_{_id}"):
                        actualizar_ingreso(_id, {"fecha": str(f), "concepto": c, "monto": m, "observacion": o})
                        st.session_state[f"edit_ingreso_{_id}"] = False
                        st.rerun()
                    if col2a.button("❌ Cancelar", key=f"cancelar_i_{_id}"):
                        st.session_state[f"edit_ingreso_{_id}"] = False
                        st.rerun()
                else:
                    st.markdown(f"📅 {pd.to_datetime(ingreso['fecha']).strftime('%d/%m/%Y')} | 💰 ₡{float(ingreso.get('monto') or 0):,.2f} | 📄 {ingreso['concepto']}".replace(",", "X").replace(".", ",").replace("X", "."))
                    st.markdown(f"📝 {ingreso.get('observacion') or '—'}")
                    col1b, col2b = st.columns(2)
                    if col1b.button("✏️ Editar", key=f"editar_i_{_id}"):
                        st.session_state[f"edit_ingreso_{_id}"] = True
                        st.rerun()
                    if col2b.button("🗑️ Eliminar", key=f"eliminar_i_{_id}"):
                        eliminar_ingreso(_id)
                        st.success("✅ Ingreso eliminado")
                        st.rerun()
        else:
            st.info("No hay ingresos registrados.")

    with col2:
        st.markdown("### 📋 Gastos")
        if not df_g.empty:
            df_g["fecha"] = pd.to_datetime(df_g["fecha"]).dt.strftime("%d/%m/%Y")
            df_g["monto"] = pd.to_numeric(df_g["monto"], errors="coerce")
            for gasto in gastos:
                _id = int(gasto["id"])
                editando = st.session_state.get(f"edit_gasto_{_id}", False)

                if editando:
                    st.markdown(f"#### ✏️ Editando gasto ID {_id}")
                    f = st.date_input("Fecha", value=pd.to_datetime(gasto["fecha"]), key=f"fecha_g_{_id}")
                    c = st.text_input("Concepto", value=gasto["concepto"], key=f"concepto_g_{_id}")
                    m = st.number_input("Monto (₡)", value=float(gasto.get("monto") or 0), key=f"monto_g_{_id}", step=500.0)
                    o = st.text_input("Observación", value=gasto.get("observacion") or "", key=f"obs_g_{_id}")
                    col1a, col2a = st.columns(2)
                    if col1a.button("💾 Guardar", key=f"guardar_g_{_id}"):
                        actualizar_gasto(_id, {"fecha": str(f), "concepto": c, "monto": m, "observacion": o})
                        st.session_state[f"edit_gasto_{_id}"] = False
                        st.rerun()
                    if col2a.button("❌ Cancelar", key=f"cancelar_g_{_id}"):
                        st.session_state[f"edit_gasto_{_id}"] = False
                        st.rerun()
                else:
                    st.markdown(f"📅 {pd.to_datetime(gasto['fecha']).strftime('%d/%m/%Y')} | 💸 ₡{float(gasto.get('monto') or 0):,.2f} | 📄 {gasto['concepto']}".replace(",", "X").replace(".", ",").replace("X", "."))
                    st.markdown(f"📝 {gasto.get('observacion') or '—'}")
                    col1b, col2b = st.columns(2)
                    if col1b.button("✏️ Editar", key=f"editar_g_{_id}"):
                        st.session_state[f"edit_gasto_{_id}"] = True
                        st.rerun()
                    if col2b.button("🗑️ Eliminar", key=f"eliminar_g_{_id}"):
                        eliminar_gasto(_id)
                        st.success("✅ Gasto eliminado")
                        st.rerun()
        else:
            st.info("No hay gastos registrados.")

# ---------------------------------------------
# 📊 PESTAÑA 5: Reporte General
# ---------------------------------------------
elif menu == "📊 Reporte General":
    st.title("📊 Reporte General")
    st.markdown("Resumen de actividad y finanzas por período de tiempo.")

    col1, col2 = st.columns(2)
    fecha_inicio = col1.date_input("📅 Desde", value=date(2025, 1, 1))
    fecha_fin = col2.date_input("📅 Hasta", value=date.today())

    cortes = obtener_cortes()
    ingresos = obtener_ingresos()
    gastos = obtener_gastos()

    df_cortes = pd.DataFrame(cortes)
    df_ingresos = pd.DataFrame(ingresos)
    df_gastos = pd.DataFrame(gastos)

    def filtrar_por_fecha(df, columna="fecha"):
        if df.empty:
            return df
        df[columna] = pd.to_datetime(df[columna]).dt.date
        return df[(df[columna] >= fecha_inicio) & (df[columna] <= fecha_fin)]

    df_cortes = filtrar_por_fecha(df_cortes)
    df_ingresos = filtrar_por_fecha(df_ingresos)
    df_gastos = filtrar_por_fecha(df_gastos)

    st.subheader("💈 Cortes realizados")
    if not df_cortes.empty:
        total_cortes = len(df_cortes)
        total_por_barbero = df_cortes["barbero"].value_counts().reset_index()
        total_por_barbero.columns = ["Barbero", "Cantidad de cortes"]
        st.markdown(f"**Total de cortes:** {total_cortes}")
        st.dataframe(total_por_barbero, use_container_width=True)
    else:
        st.info("No hay cortes registrados en el rango seleccionado.")

    st.subheader("💰 Ingresos")
    if not df_ingresos.empty:
        df_ingresos["monto"] = pd.to_numeric(df_ingresos["monto"], errors="coerce")
        total_ingresos = df_ingresos["monto"].sum()
        st.markdown(f"**Total de ingresos:** ₡{total_ingresos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.dataframe(df_ingresos[["fecha", "concepto", "monto", "observacion"]], use_container_width=True)
    else:
        total_ingresos = 0
        st.info("No hay ingresos registrados en el rango seleccionado.")

    st.subheader("💸 Gastos")
    if not df_gastos.empty:
        df_gastos["monto"] = pd.to_numeric(df_gastos["monto"], errors="coerce")
        total_gastos = df_gastos["monto"].sum()
        st.markdown(f"**Total de gastos:** ₡{total_gastos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.dataframe(df_gastos[["fecha", "concepto", "monto", "observacion"]], use_container_width=True)
    else:
        total_gastos = 0
        st.info("No hay gastos registrados en el rango seleccionado.")

    st.divider()
    st.subheader("📉 Balance del período")
    balance = (total_ingresos or 0) - (total_gastos or 0)
    color = "green" if balance >= 0 else "red"
    st.markdown(
        f"<strong>Balance final:</strong> <span style='color:{color}; font-weight:bold;'>₡{balance:,.2f}</span>"
        .replace(",", "X").replace(".", ",").replace("X", "."),
        unsafe_allow_html=True
    )

    # ===== Descargar informe PDF =====
    st.divider()
    st.subheader("⬇️ Descargar informe financiero (PDF)")

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    style_title = ParagraphStyle("title", fontSize=16, alignment=1, textColor=colors.white, backColor=colors.HexColor("#007bff"), spaceAfter=12, spaceBefore=6, leading=20)
    style_section_title = ParagraphStyle("section", fontSize=12, textColor=colors.white, leftIndent=0, spaceBefore=12, spaceAfter=6, leading=14)
    style_normal = styles["Normal"]; style_normal.spaceAfter = 6

    def color_box(text, bgcolor):
        return Table([[Paragraph(text, style_section_title)]], colWidths=[doc.width], style=[
            ("BACKGROUND", (0, 0), (-1, -1), bgcolor),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4)
        ])

    def crear_tabla(data, headers):
        table_data = [headers] + data
        return Table(table_data, style=[
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ], hAlign='LEFT')

    # Título
    elements.append(Paragraph("Informe Financiero", style_title))
    elements.append(Paragraph("Este informe fue generado automáticamente por la Barbería [Nombre de la Barbería].", style_normal))
    elements.append(Paragraph(f"<i>Período: {fecha_inicio.strftime('%d-%m-%Y')} al {fecha_fin.strftime('%d-%m-%Y')}</i>", style_normal))

    # Ingresos
    elements.append(color_box("Ingresos", colors.HexColor("#cfe2ff")))
    if not df_ingresos.empty:
        elements.append(Paragraph(f"Total ingresos: CRC {total_ingresos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), style_normal))
        ingresos_data = df_ingresos[["fecha", "concepto", "monto"]].astype(str).values.tolist()
        elements.append(crear_tabla(ingresos_data, ["Fecha", "Concepto", "Monto"]))
    else:
        elements.append(Paragraph("No se registraron ingresos en este período.", style_normal))
        elements.append(Paragraph("Total ingresos: CRC 0.00.", style_normal))

    # Gastos
    elements.append(color_box("Gastos", colors.HexColor("#f8d7da")))
    if not df_gastos.empty:
        elements.append(Paragraph(f"Total gastos: CRC {total_gastos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), style_normal))
        gastos_data = df_gastos[["fecha", "concepto", "monto"]].astype(str).values.tolist()
        elements.append(crear_tabla(gastos_data, ["Fecha", "Concepto", "Monto"]))
    else:
        elements.append(Paragraph("No se registraron gastos en este período.", style_normal))
        elements.append(Paragraph("Total gastos: CRC 0.00.", style_normal))

    # Balance final
    balance_color = "#d1e7dd" if balance >= 0 else "#f8d7da"
    balance_text_color = "#198754" if balance >= 0 else "#dc3545"
    balance_text = f"<b>Balance final:</b> <font color='{balance_text_color}'>CRC {balance:,.2f}</font>".replace(",", "X").replace(".", ",").replace("X", ".")
    elements.append(color_box("Balance final", colors.HexColor(balance_color)))
    elements.append(Paragraph(balance_text, style_normal))

    def agregar_pie(canvas, doc):
        canvas.saveState()
        footer_text = "Página %d - Barbería [Nombre de la Barbería]" % (doc.page)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(A4[0] - 2*cm, 1.5*cm, footer_text)
        canvas.restoreState()

    doc.build(elements, onLaterPages=agregar_pie, onFirstPage=agregar_pie)

    st.download_button(
        label="📄 Descargar informe financiero (PDF)",
        data=pdf_buffer.getvalue(),
        file_name="informe_financiero.pdf",
        mime="application/pdf"
    )






