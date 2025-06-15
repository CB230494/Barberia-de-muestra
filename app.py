import streamlit as st
from database import init_db, registrar_cortes, obtener_registros, obtener_resumen
from datetime import date

init_db()

# --- Estilos: solo franjas laterales vino ---
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
        background-image:
            linear-gradient(to right, #800000 0%, #800000 15%, transparent 15%, transparent 85%, #800000 85%, #800000 100%);
        background-repeat: no-repeat;
        background-size: cover;
    }

    .info-card {
        background-color: white;
        padding: 1.2rem;
        border-radius: 1rem;
        box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.15);
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
        color: black;
    }

    h1, h2, h3 {
        color: #800000;
    }

    label, .stTextInput label, .stNumberInput label, .stDateInput label {
        color: #333333 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #002366;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span {
        color: white !important;
    }

    .stTable, .stDataFrame {
        background-color: white !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Menú lateral ---
st.sidebar.title("💈 Menú")
st.sidebar.markdown("Navega entre las secciones del sistema:")

# --- Título principal ---
st.title("💈 Barbería - Panel Básico")

# --- Resumen general ---
st.subheader("📊 Resumen general")
total_cortes, total_ganancias = obtener_resumen()

st.markdown(
    f'<div class="info-card">✂️ Total de cortes realizados: <strong>{total_cortes}</strong></div>',
    unsafe_allow_html=True
)
st.markdown(
    f'<div class="info-card">💰 Ganancias acumuladas: <strong>₡{total_ganancias:,.2f}</strong></div>',
    unsafe_allow_html=True
)

# --- Registro de cortes ---
st.subheader("📝 Registrar cortes del día")
fecha = st.date_input("Fecha", date.today())
cantidad = st.number_input("Cantidad de cortes", min_value=0, step=1)
ganancias = st.number_input("Ganancia total del día (₡)", min_value=0.0, step=100.0, format="%.2f")

if st.button("Guardar"):
    exito = registrar_cortes(str(fecha), cantidad, ganancias)
    if exito:
        st.success("✅ Registro guardado correctamente")
    else:
        st.warning("⚠️ Ya existe un registro para esa fecha.")

# --- Historial ---
st.subheader("📅 Historial de cortes registrados")
registros = obtener_registros()
if registros:
    st.table(registros)
else:
    st.info("Aún no se han registrado cortes.")

