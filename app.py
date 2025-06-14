import streamlit as st
from datetime import datetime, timedelta
from database import (
    init_db, registrar_cita, obtener_citas, obtener_citas_por_fecha,
    bloquear_hora, desbloquear_hora
)

init_db()

st.title("📅 Agenda de Citas - Barbería Carlos")
st.markdown("Horario: **Lunes a Sábado, 8:00am - 7:00pm**, cada media hora")

# Selección de fecha
fecha = st.date_input("Selecciona una fecha:", min_value=datetime.today())

# Mostrar horas disponibles
hora_inicio = datetime.strptime("08:00", "%H:%M")
hora_fin = datetime.strptime("19:00", "%H:%M")
intervalo = timedelta(minutes=30)

# Ver citas ocupadas o bloqueadas
horas_ocupadas = obtener_citas_por_fecha(fecha.strftime("%Y-%m-%d"))

horas_disponibles = []
actual = hora_inicio
while actual < hora_fin:
    hora_str = actual.strftime("%H:%M")
    if hora_str not in horas_ocupadas:
        horas_disponibles.append(hora_str)
    actual += intervalo

# 🟢 AGENDAR UNA CITA
st.subheader("✂️ Agendar nueva cita")
if horas_disponibles:
    hora = st.selectbox("Selecciona una hora disponible:", horas_disponibles)
    nombre = st.text_input("¿Cuál es tu nombre completo?")
    if st.button("Agendar cita"):
        registrar_cita(nombre, fecha.strftime("%Y-%m-%d"), hora)
        st.success(f"Cita agendada para {nombre} el {fecha.strftime('%d-%m-%Y')} a las {hora}")
else:
    st.warning("No hay horas disponibles para este día.")

# 🔒 BLOQUEAR HORAS
st.subheader("🚫 Bloquear horas (almuerzo o eventualidad)")
hora_bloqueo = st.selectbox("Selecciona hora a bloquear:", [h for h in horas_disponibles])
if st.button("Bloquear esta hora"):
    bloquear_hora(fecha.strftime("%Y-%m-%d"), hora_bloqueo)
    st.success(f"Hora {hora_bloqueo} bloqueada exitosamente")

# 🔓 DESBLOQUEAR HORAS
st.subheader("🔓 Desbloquear hora")
horas_bloqueadas = [h for h in obtener_citas_por_fecha(fecha.strftime("%Y-%m-%d")) if h not in horas_ocupadas and h not in horas_disponibles]
if horas_bloqueadas:
    hora_desbloqueo = st.selectbox("Selecciona hora a desbloquear:", horas_bloqueadas)
    if st.button("Desbloquear esta hora"):
        desbloquear_hora(fecha.strftime("%Y-%m-%d"), hora_desbloqueo)
        st.success(f"Hora {hora_desbloqueo} desbloqueada correctamente")

# 👀 Citas del día seleccionado
st.subheader("📋 Citas agendadas para este día")
citas_dia = [c for c in obtener_citas() if c[1] == fecha.strftime("%Y-%m-%d")]
if citas_dia:
    for c in sorted(citas_dia, key=lambda x: x[2]):
        if c[0] != "BLOQUEADO":
            st.write(f"🧔 {c[0]} - {c[2]}")
        else:
            st.write(f"🚫 Hora bloqueada - {c[2]}")
else:
    st.write("No hay citas para este día.")
