import streamlit as st
from datetime import datetime, timedelta, date
from database import insertar_cita, obtener_citas
import pandas as pd

st.set_page_config(page_title="Agendar Cita - Barbería", layout="centered")

st.title("💈 Agenda tu cita")
st.markdown("Selecciona una fecha, horario y servicio. Tu cita quedará **pendiente de aprobación** por el administrador.")

# ---------- CONFIGURACIÓN ----------
HORARIO_INICIO = 8  # 8:00 am
HORARIO_FIN = 19    # 7:00 pm
INTERVALO_MINUTOS = 30

SERVICIOS = ["Corte clásico", "Corte moderno", "Barba", "Color", "Combo completo"]

# ---------- INPUTS ----------
fecha = st.date_input("📅 Fecha", min_value=date.today())

# ---------- FUNCIONES ----------
def generar_horarios_del_dia(fecha):
    try:
        citas = obtener_citas()
        df = pd.DataFrame(citas)

        if not {"fecha", "hora", "estado"}.issubset(df.columns):
            df = pd.DataFrame(columns=["fecha", "hora", "estado"])

        df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
        df["hora"] = df["hora"].astype(str).str[:5]  # Formato HH:MM

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
            estado = coincidencias.iloc[0]["estado"]

        horarios_dia.append({
            "hora": hora_str,
            "estado": estado
        })

        actual += timedelta(minutes=INTERVALO_MINUTOS)

    return horarios_dia

# ---------- MOSTRAR RESUMEN ----------
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

# ---------- AGENDAR SI HAY DISPONIBLES ----------
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


