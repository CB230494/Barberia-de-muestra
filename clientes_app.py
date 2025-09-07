# ---------------------------------------------
# 💈 Agenda de Citas – Cliente
# app_clientes.py – Backend Google Sheets incluido
# ---------------------------------------------
import streamlit as st
from datetime import datetime, timedelta, date
import pandas as pd
from typing import Dict, List, Any, Optional
import gspread

st.set_page_config(page_title="Agendar Cita - Barbería", layout="centered")
st.title("💈 Agenda tu cita")
st.markdown("Selecciona una fecha, horario y servicio. Tu cita quedará **pendiente de aprobación** por el administrador.")

# ====== Config ======
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1cs5I7U_nEHY7B0qCkA3WvY5_Y5hd97bd2nuifPrK6Jw/edit?usp=sharing"
SCHEMA_CITAS = ["id", "fecha", "hora", "cliente_nombre", "barbero", "servicio", "estado"]

HORARIO_INICIO = 8   # 8:00 am
HORARIO_FIN = 19     # 7:00 pm (exclusivo)
INTERVALO_MINUTOS = 30
SERVICIOS = ["Corte clásico", "Corte moderno", "Barba", "Color", "Combo completo"]

# ====== Backend Sheets (incluido) ======
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

def _get_ws():
    sh = _open_sheet()
    try:
        ws = sh.worksheet("Citas")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title="Citas", rows=2000, cols=20)
        ws.append_row(SCHEMA_CITAS)
    headers = ws.row_values(1)
    if headers != SCHEMA_CITAS:
        if headers:
            ws.delete_rows(1)
        ws.insert_row(SCHEMA_CITAS, 1)
    return ws

def _next_id(ws) -> int:
    ids = ws.col_values(1)[1:]
    nums = []
    for v in ids:
        try: nums.append(int(str(v).strip()))
        except: pass
    return (max(nums) + 1) if nums else 1

def obtener_citas() -> List[Dict[str, Any]]:
    ws = _get_ws()
    return ws.get_all_records()

def insertar_cita(fecha: str, hora: str, cliente_nombre: str, barbero: str, servicio: str):
    ws = _get_ws()
    ws.append_row(
        [ _next_id(ws), fecha, hora, cliente_nombre, barbero, servicio, "pendiente" ],
        value_input_option="USER_ENTERED"
    )

# ====== UI ======
fecha = st.date_input("📅 Fecha", min_value=date.today())

def generar_horarios_del_dia(fecha):
    try:
        citas = obtener_citas()
        df = pd.DataFrame(citas)
        if not {"fecha", "hora", "estado"}.issubset(df.columns):
            df = pd.DataFrame(columns=["fecha", "hora", "estado"])
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
        df["hora"] = df["hora"].astype(str).str[:5]
    except Exception as e:
        st.warning(f"⚠️ Error al procesar citas: {e}")
        df = pd.DataFrame(columns=["fecha", "hora", "estado"])

    horarios_dia = []
    actual = datetime.combine(fecha, datetime.min.time()).replace(hour=HORARIO_INICIO)
    fin = actual.replace(hour=HORARIO_FIN)

    while actual < fin:
        hora_str = actual.strftime("%H:%M")
        estado = "disponible"
        coincidencias = df[(df["fecha"] == fecha) & (df["hora"] == hora_str)]
        if not coincidencias.empty:
            # si hay varias, toma la primera (todas deberían tener mismo estado en ese horario)
            estado = coincidencias.iloc[0]["estado"] or "pendiente"
        horarios_dia.append({"hora": hora_str, "estado": estado})
        actual += timedelta(minutes=INTERVALO_MINUTOS)
    return horarios_dia

st.subheader("📋 Horarios para el día seleccionado")
horarios = generar_horarios_del_dia(fecha)
df_horarios = pd.DataFrame(horarios)

estado_emojis = {
    "disponible": "🟢 Disponible",
    "pendiente": "⏳ Pendiente",
    "aceptada": "✅ Aceptada",
    "rechazada": "❌ Rechazada"
}

if not df_horarios.empty:
    df_horarios["estado"] = df_horarios["estado"].map(estado_emojis)
    st.dataframe(df_horarios, use_container_width=True)
else:
    st.info("No hay información de horarios aún.")

horas_disponibles = [h["hora"] for h in horarios if h["estado"] == "disponible"]

if horas_disponibles:
    st.subheader("📝 Reservar nueva cita")
    hora = st.selectbox("🕒 Hora disponible", horas_disponibles)
    cliente_nombre = st.text_input("👤 Tu nombre completo")
    servicio = st.selectbox("🧴 Servicio", SERVICIOS)

    if st.button("📥 Reservar cita"):
        if not cliente_nombre.strip():
            st.warning("⚠️ Debes ingresar tu nombre.")
        else:
            insertar_cita(str(fecha), hora, cliente_nombre.strip(), "", servicio)
            st.success("✅ Cita registrada. Espera aprobación del administrador.")
            st.rerun()
else:
    st.warning("⛔ No hay horarios disponibles para esta fecha.")



