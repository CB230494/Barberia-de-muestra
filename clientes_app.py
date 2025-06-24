import streamlit as st
from datetime import datetime, timedelta, date
from database import insertar_cita, obtener_citas
import pandas as pd

st.set_page_config(page_title="Agendar Cita - Barbería", layout="centered")

st.title("💈 Agenda tu cita")
st.markdown("Selecciona una fecha, horario y servicio. Tu cita quedará pendiente de aprobación por el administrador.")

# ---------- CONFIGURACIÓN ----------
HORARIO_INICIO = 8  # 8:00 am
HORARIO_FIN = 19    # 7:00 pm
INTERVALO_MINUTOS = 30

# ---------- SERVICIOS DISPONIBLES ----------
SERVICIOS = ["Corte clásico", "Corte moderno", "Barba", "Color", "Combo completo"]

# ---------- INPUTS ----------
fecha = st.date_input("📅 Fecha", min_value=date.today())

# Horarios disponibles
def generar_horarios_disponibles(fecha):
    citas = obtener_citas()
    df = pd.DataFrame(citas)
    if df.empty:
        df = pd.DataFrame(columns=["fecha", "hora"])
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

    horarios_ocupados = df[df["fecha"] == fecha]["hora"].tolist()

    horas_disponibles = []
    actual = datetime.combine(fecha, datetime.min.time()).replace(hour=HORARIO_INICIO)
    fin = actual.replace(hour=HORARIO_FIN)

    while actual < fin:
        hora_str = actual.strftime("%H:%M")
        if hora_str not in horarios_ocupados:
            horas_disponibles.append(hora_str)
        actual += timedelta(minutes=INTERVALO_MINUTOS)

    return horas_disponibles

horas_disponibles = generar_horarios_disponibles(fecha)

if horas_disponibles:
    hora = st.selectbox("🕒 Hora disponible", horas_disponibles)
    cliente_nombre = st.text_input("👤 Tu nombre completo")
    servicio = st.selectbox("🧴 Servicio", SERVICIOS)

    if st.button("📥 Reservar cita"):
        if not cliente_nombre.strip():
            st.warning("⚠️ Debes ingresar tu nombre.")
        else:
            insertar_cita(str(fecha), hora, cliente_nombre.strip(), "", servicio)
            st.success("✅ Cita registrada exitosamente. El administrador la aprobará.")
else:
    st.warning("⛔ No hay horarios disponibles para esta fecha.")
