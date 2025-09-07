# ---------------------------------------------
# 📋 SISTEMA DE CONTROL PARA BARBERÍA - ADMIN
# app.py – UI + backend Google Sheets (sin Supabase)
# ---------------------------------------------
import streamlit as st
import pandas as pd
import io
from datetime import datetime, date
from typing import Dict, List, Any, Optional

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# Google Sheets
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
# 🔌 BACKEND GOOGLE SHEETS (incluido)
# ============================================================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1cs5I7U_nEHY7B0qCkA3WvY5_Y5hd97bd2nuifPrK6Jw/edit?usp=sharing"

SCHEMAS: Dict[str, List[str]] = {
    "Cortes":    ["id", "fecha", "barbero", "cliente", "tipo_corte", "precio", "observacion"],
    "Productos": ["id", "nombre", "descripcion", "stock", "precio_unitario"],
    "Citas":     ["id", "fecha", "hora", "cliente_nombre", "barbero", "servicio", "estado"],
    "Ingresos":  ["id", "fecha", "concepto", "monto", "observacion"],
    "Gastos":    ["id", "fecha", "concepto", "monto", "observacion"],
}

@st.cache_resource(show_spinner=False)
def _gc():
    sa = st.secrets.get("gcp_service_account")
    if not sa:
        raise RuntimeError(
            "Falta st.secrets['gcp_service_account']. "
            "Sube el JSON del Service Account y comparte la hoja con ese correo (Editor)."
        )
    return gspread.service_account_from_dict(dict(sa))

@st.cache_resource(show_spinner=False)
def _open_sheet():
    return _gc().open_by_url(SPREADSHEET_URL)

def _get_ws(title: str):
    """Abre/crea hoja y garantiza cabeceras en la fila 1."""
    sh = _open_sheet()
    schema = SCHEMAS[title]
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=2000, cols=max(20, len(schema)))
        ws.insert_row(schema, 1)
        return ws

    headers = ws.row_values(1)
    if not headers or [h.strip() for h in headers] != schema:
        try:
            ws.delete_rows(1)
        except Exception:
            pass
        ws.insert_row(schema, 1)
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
    """Lee registros de forma segura aunque la hoja esté vacía."""
    ws = _get_ws(sheet)
    all_vals = ws.get_all_values()
    if not all_vals or len(all_vals) == 1:
        return []
    rows = ws.get_all_records()
    # Normaliza tipos
    for r in rows:
        if "id" in r and str(r["id"]).strip() != "":
            try:
                r["id"] = int(str(r["id"]).strip())
            except:
                pass
        for k in ("precio", "precio_unitario", "monto", "stock"):
            if k in r and str(r[k]).strip() != "":
                try:
                    r[k] = float(str(r[k]).replace(",", "."))
                except:
                    pass
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
        if k in colmap:
            ws.update_cell(row, colmap[k], v)

def _delete(sheet: str, _id: int):
    ws = _get_ws(sheet)
    row = _find_row_by_id(ws, _id)
    if row:
        ws.delete_rows(row)

# ---- CRUD específicos que usa la UI ----
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
    _append("Ingresos", {"id": _next_id(ws), "fecha": fecha, "concepto": concepto, "monto": monto, "observacion": observacion})

def obtener_ingresos() -> List[Dict[str, Any]]:
    return _read_all("Ingresos")

def actualizar_ingreso(_id: int, values: Dict[str, Any]):
    _update("Ingresos", _id, values)

def eliminar_ingreso(_id: int):
    _delete("Ingresos", _id)

def insertar_gasto(fecha: str, concepto: str, monto: float, observacion: str):
    ws = _get_ws("Gastos")
    _append("Gastos", {"id": _next_id(ws), "fecha": fecha, "concepto": concepto, "monto": monto, "observacion": observacion})

def obtener_gastos() -> List[Dict[str, Any]]:
    return _read_all("Gastos")

def actualizar_gasto(_id: int, values: Dict[str, Any]):
    _update("Gastos", _id, values)

def eliminar_gasto(_id: int):
    _delete("Gastos", _id)

# ============================================================
# 🧭 UI – 5 pestañas
# ============================================================
menu = st.sidebar.radio(
    "Selecciona una sección",
    ["✂️ Registro de Cortes", "📦 Inventario", "📅 Citas", "💵 Finanzas", "📊 Reporte General"]
)

# ---------------------------------------------
# ✂️ Registro de Cortes
# ---------------------------------------------
if menu == "✂️ Registro de Cortes":
    st.title("✂️ Registro de Cortes Realizados")
    st.markdown("Agrega, consulta o elimina cortes realizados por los barberos.")

    st.subheader("➕ Agregar nuevo corte")
    with st.form("form_nuevo_corte"):
        col1, col2, col3 = st.columns(3)
        fecha = col1.date_input("Fecha", value=date.today())
        barbero = col2.text_input("Nombre del barbero")
        cliente = col3.text_input("Nombre del cliente")
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
        try:
            df["precio"] = pd.to_numeric(df["precio"], errors="coerce").round(2)
        except Exception:
            pass

        # Excel respaldo
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Cortes")
        st.download_button(
            "⬇️ Descargar respaldo en Excel",
            output.getvalue(),
            "cortes_registrados.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        for corte in cortes:
            id_corte = int(corte["id"])
            editando = st.session_state.get(f"edit_{id_corte}", False)

            if editando:
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
                    actualizar_corte(id_corte, {"fecha": str(f), "barbero": b, "cliente": c, "tipo_corte": t, "precio": p, "observacion": o})
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
                try:
                    cols[4].markdown(f"💰 ₡{float(corte.get('precio') or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                except:
                    cols[4].markdown(f"💰 ₡{corte.get('precio')}")
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
# 📦 Inventario
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
        try:
            df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce")
        except Exception:
            pass

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Productos")
        st.download_button(
            "⬇️ Descargar inventario en Excel",
            output.getvalue(),
            "inventario_productos.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        for producto in productos:
            idp = int(producto["id"])
            editando = st.session_state.get(f"edit_prod_{idp}", False)

            if editando:
                st.markdown(f"### ✏️ Editando producto ID {idp}")
                col1, col2 = st.columns(2)
                nombre_edit = col1.text_input("Nombre", value=producto["nombre"], key=f"nombre_{idp}")
                precio_edit = col2.number_input("Precio (₡)", value=float(producto.get("precio_unitario") or 0), step=100.0, format="%.2f", key=f"precio_{idp}")
                descripcion_edit = st.text_input("Descripción", value=producto.get("descripcion") or "", key=f"desc_{idp}")
                stock_edit = st.number_input("Stock", value=int(float(producto.get("stock") or 0)), step=1, key=f"stock_{idp}")
                col1b, col2b = st.columns(2)
                if col1b.button("💾 Guardar", key=f"guardar_{idp}"):
                    actualizar_producto(idp, {"nombre": nombre_edit, "precio_unitario": precio_edit, "descripcion": descripcion_edit, "stock": stock_edit})
                    st.session_state[f"edit_prod_{idp}"] = False
                    st.success("✅ Producto actualizado")
                    st.rerun()
                if col2b.button("❌ Cancelar", key=f"cancelar_{idp}"):
                    st.session_state[f"edit_prod_{idp}"] = False
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
                if cols[4].button("✏️", key=f"edit_{idp}"):
                    st.session_state[f"edit_prod_{idp}"] = True
                    st.rerun()
                if cols[5].button("🗑️", key=f"del_{idp}"):
                    eliminar_producto(idp)
                    st.success("✅ Producto eliminado")
                    st.rerun()
    else:
        st.info("No hay productos registrados todavía.")

# ---------------------------------------------
# 📅 Citas (admin)
# ---------------------------------------------
elif menu == "📅 Citas":
    st.title("📅 Gestión de Citas")
    st.markdown("Revisa y administra las citas solicitadas por los clientes.")

    citas = obtener_citas()
    df = pd.DataFrame(citas)

    # 🔧 Normaliza hora a HH:MM para evitar '8:30' vs '08:30'
    if not df.empty and "hora" in df.columns:
        def _norm_hhmm(x):
            x = str(x).strip()
            if ":" not in x: return x
            h, m = x.split(":", 1)
            try: return f"{int(h):02d}:{int(m):02d}"
            except: return x
        df["hora"] = df["hora"].astype(str).map(_norm_hhmm)

    if df.empty:
        st.info("No hay citas registradas.")
    else:
        estados = ["todas", "pendiente", "aceptada", "rechazada"]
        estado_filtro = st.selectbox("🔍 Filtrar por estado", estados)
        if estado_filtro != "todas":
            df = df[df["estado"] == estado_filtro]

        for cita in df.to_dict(orient="records"):
            cid = int(cita["id"])
            st.markdown(f"### 🧾 Cita ID {cid}")
            col1, col2, col3 = st.columns(3)
            try:
                fecha_show = pd.to_datetime(cita["fecha"]).strftime("%d/%m/%Y")
            except:
                fecha_show = str(cita["fecha"])
            col1.markdown(f"**📅 Fecha:** {fecha_show}")
            col2.markdown(f"**🕒 Hora:** {cita['hora']}")
            col3.markdown(f"**🧴 Servicio:** {cita['servicio']}")
            st.markdown(f"**👤 Cliente:** {cita['cliente_nombre']}")
            st.markdown(f"**✂️ Barbero asignado:** {cita.get('barbero') or 'Sin asignar'}")
            st.markdown(f"**📌 Estado actual:** `{cita['estado']}`")

            with st.expander("✏️ Editar cita"):
                # Fecha
                try:
                    valor_fecha = pd.to_datetime(cita["fecha"]).date()
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
                    actualizar_cita(cid, {"fecha": nueva_fecha.strftime("%Y-%m-%d"), "hora": nueva_hora.strftime("%H:%M"), "barbero": nuevo_barbero})
                    st.success("✅ Cita actualizado")
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
# 💵 Finanzas
# ---------------------------------------------
elif menu == "💵 Finanzas":
    st.title("💵 Control de Finanzas")
    st.markdown("Registra ingresos y gastos y consulta el balance general.")

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
        if ingresos:
            for ingreso in ingresos:
                _id = int(ingreso["id"])
                st.markdown(f"📅 {pd.to_datetime(ingreso['fecha']).strftime('%d/%m/%Y')} | 💰 ₡{float(ingreso.get('monto') or 0):,.2f} | 📄 {ingreso['concepto']}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.markdown(f"📝 {ingreso.get('observacion') or '—'}")
                c1, c2 = st.columns(2)
                if c1.button("✏️ Editar", key=f"editar_i_{_id}"):
                    st.session_state[f"edit_ingreso_{_id}"] = True
                if c2.button("🗑️ Eliminar", key=f"eliminar_i_{_id}"):
                    eliminar_ingreso(_id); st.rerun()

            for ingreso in ingresos:
                _id = int(ingreso["id"])
                if st.session_state.get(f"edit_ingreso_{_id}"):
                    st.markdown(f"#### ✏️ Editando ingreso ID {_id}")
                    f = st.date_input("Fecha", value=pd.to_datetime(ingreso["fecha"]), key=f"fecha_i_{_id}")
                    c = st.text_input("Concepto", value=ingreso["concepto"], key=f"concepto_i_{_id}")
                    m = st.number_input("Monto (₡)", value=float(ingreso.get("monto") or 0), key=f"monto_i_{_id}", step=500.0)
                    o = st.text_input("Observación", value=ingreso.get("observacion") or "", key=f"obs_i_{_id}")
                    cc1, cc2 = st.columns(2)
                    if cc1.button("💾 Guardar", key=f"guardar_i_{_id}"):
                        actualizar_ingreso(_id, {"fecha": str(f), "concepto": c, "monto": m, "observacion": o})
                        st.session_state[f"edit_ingreso_{_id}"] = False; st.rerun()
                    if cc2.button("❌ Cancelar", key=f"cancelar_i_{_id}"):
                        st.session_state[f"edit_ingreso_{_id}"] = False; st.rerun()
        else:
            st.info("No hay ingresos registrados.")

    with col2:
        st.markdown("### 📋 Gastos")
        if gastos:
            for gasto in gastos:
                _id = int(gasto["id"])
                st.markdown(f"📅 {pd.to_datetime(gasto['fecha']).strftime('%d/%m/%Y')} | 💸 ₡{float(gasto.get('monto') or 0):,.2f} | 📄 {gasto['concepto']}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.markdown(f"📝 {gasto.get('observacion') or '—'}")
                c1, c2 = st.columns(2)
                if c1.button("✏️ Editar", key=f"editar_g_{_id}"):
                    st.session_state[f"edit_gasto_{_id}"] = True
                if c2.button("🗑️ Eliminar", key=f"eliminar_g_{_id}"):
                    eliminar_gasto(_id); st.rerun()

            for gasto in gastos:
                _id = int(gasto["id"])
                if st.session_state.get(f"edit_gasto_{_id}"):
                    st.markdown(f"#### ✏️ Editando gasto ID {_id}")
                    f = st.date_input("Fecha", value=pd.to_datetime(gasto["fecha"]), key=f"fecha_g_{_id}")
                    c = st.text_input("Concepto", value=gasto["concepto"], key=f"concepto_g_{_id}")
                    m = st.number_input("Monto (₡)", value=float(gasto.get("monto") or 0), key=f"monto_g_{_id}", step=500.0)
                    o = st.text_input("Observación", value=gasto.get("observacion") or "", key=f"obs_g_{_id}")
                    cc1, cc2 = st.columns(2)
                    if cc1.button("💾 Guardar", key=f"guardar_g_{_id}"):
                        actualizar_gasto(_id, {"fecha": str(f), "concepto": c, "monto": m, "observacion": o})
                        st.session_state[f"edit_gasto_{_id}"] = False; st.rerun()
                    if cc2.button("❌ Cancelar", key=f"cancelar_g_{_id}"):
                        st.session_state[f"edit_gasto_{_id}"] = False; st.rerun()
        else:
            st.info("No hay gastos registrados.")

# ---------------------------------------------
# 📊 Reporte General
# ---------------------------------------------
elif menu == "📊 Reporte General":
    st.title("📊 Reporte General")
    st.markdown("Resumen de actividad y finanzas por período de tiempo.")

    col1, col2 = st.columns(2)
    fecha_inicio = col1.date_input("📅 Desde", value=date(2025, 1, 1))
    fecha_fin = col2.date_input("📅 Hasta", value=date.today())

    df_cortes = pd.DataFrame(obtener_cortes())
    df_ingresos = pd.DataFrame(obtener_ingresos())
    df_gastos = pd.DataFrame(obtener_gastos())

    def filtrar(df, col="fecha"):
        if df.empty: return df
        df[col] = pd.to_datetime(df[col]).dt.date
        return df[(df[col] >= fecha_inicio) & (df[col] <= fecha_fin)]

    df_cortes = filtrar(df_cortes)
    df_ingresos = filtrar(df_ingresos)
    df_gastos = filtrar(df_gastos)

    st.subheader("💈 Cortes realizados")
    if not df_cortes.empty:
        tot = len(df_cortes)
        por_barbero = df_cortes["barbero"].value_counts().reset_index()
        por_barbero.columns = ["Barbero", "Cantidad de cortes"]
        st.markdown(f"**Total de cortes:** {tot}")
        st.dataframe(por_barbero, use_container_width=True)
    else:
        st.info("No hay cortes en el rango.")

    st.subheader("💰 Ingresos")
    if not df_ingresos.empty:
        df_ingresos["monto"] = pd.to_numeric(df_ingresos["monto"], errors="coerce")
        total_ingresos = df_ingresos["monto"].sum()
        st.markdown(f"**Total de ingresos:** ₡{total_ingresos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.dataframe(df_ingresos[["fecha", "concepto", "monto", "observacion"]], use_container_width=True)
    else:
        total_ingresos = 0
        st.info("No hay ingresos en el rango.")

    st.subheader("💸 Gastos")
    if not df_gastos.empty:
        df_gastos["monto"] = pd.to_numeric(df_gastos["monto"], errors="coerce")
        total_gastos = df_gastos["monto"].sum()
        st.markdown(f"**Total de gastos:** ₡{total_gastos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.dataframe(df_gastos[["fecha", "concepto", "monto", "observacion"]], use_container_width=True)
    else:
        total_gastos = 0
        st.info("No hay gastos en el rango.")

    st.divider()
    st.subheader("📉 Balance del período")
    balance = (total_ingresos or 0) - (total_gastos or 0)
    color = "green" if balance >= 0 else "red"
    st.markdown(
        f"<strong>Balance final:</strong> <span style='color:{color}; font-weight:bold;'>₡{balance:,.2f}</span>"
        .replace(",", "X").replace(".", ",").replace("X", "."),
        unsafe_allow_html=True
    )

    # PDF
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

    elements.append(Paragraph("Informe Financiero", style_title))
    elements.append(Paragraph("Este informe fue generado automáticamente por la Barbería [Nombre de la Barbería].", style_normal))
    elements.append(Paragraph(f"<i>Período: {fecha_inicio.strftime('%d-%m-%Y')} al {fecha_fin.strftime('%d-%m-%Y')}</i>", style_normal))

    # Ingresos
    if not df_ingresos.empty:
        elements.append(color_box("Ingresos", colors.HexColor("#cfe2ff")))
        elements.append(Paragraph(f"Total ingresos: CRC {total_ingresos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), style_normal))
        ingresos_data = df_ingresos[["fecha", "concepto", "monto"]].astype(str).values.tolist()
        elements.append(crear_tabla(ingresos_data, ["Fecha", "Concepto", "Monto"]))
    else:
        elements.append(color_box("Ingresos", colors.HexColor("#cfe2ff")))
        elements.append(Paragraph("No se registraron ingresos en este período.\nTotal ingresos: CRC 0.00.", style_normal))

    # Gastos
    if not df_gastos.empty:
        elements.append(color_box("Gastos", colors.HexColor("#f8d7da")))
        elements.append(Paragraph(f"Total gastos: CRC {total_gastos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), style_normal))
        gastos_data = df_gastos[["fecha", "concepto", "monto"]].astype(str).values.tolist()
        elements.append(crear_tabla(gastos_data, ["Fecha", "Concepto", "Monto"]))
    else:
        elements.append(color_box("Gastos", colors.HexColor("#f8d7da")))
        elements.append(Paragraph("No se registraron gastos en este período.\nTotal gastos: CRC 0.00.", style_normal))

    # Balance final
    balance_color = "#d1e7dd" if balance >= 0 else "#f8d7da"
    balance_text_color = "#198754" if balance >= 0 else "#dc3545"
    balance_text = f"<b>Balance final:</b> <font color='{balance_text_color}'>CRC {balance:,.2f}</font>".replace(",", "X").replace(".", ",").replace("X", ".")
    elements.append(color_box("Balance final", colors.HexColor(balance_color)))
    elements.append(Paragraph(balance_text, style_normal))

    def _pie(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(A4[0] - 2*cm, 1.5*cm, f"Página {doc.page} - Barbería")
        canvas.restoreState()

    doc.build(elements, onLaterPages=_pie, onFirstPage=_pie)

    st.download_button(
        "📄 Descargar informe financiero (PDF)",
        pdf_buffer.getvalue(),
        "informe_financiero.pdf",
        "application/pdf"
    )








