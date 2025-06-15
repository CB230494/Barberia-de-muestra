import streamlit as st
from database import init_db, registrar_cortes, obtener_registros, obtener_resumen
from datetime import date

# Inicializar base de datos
init_db()

# --- Estilos personalizados con franjas y colores ---
st.markdown("""
    <style>
    /* Fondo principal con franjas en la esquina superior derecha */
    .stApp {
        background: linear-gradient(to top right, #ffffff 0%, #ffffff 75%, #ff0000 75%, #ff0000 100%);
        color: #000000;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Tarjetas de resumen */
    .info-card {
        background-color: white;
        padding: 1.2rem;
        border-radius: 1rem;
        box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.15);
        margin-bottom: 1.5rem;
        font-size: 1.2rem;
    }

    h1, h2, h3 {
        color: #B30000;
    }

    /* Sidebar fondo azul y letras blancas */
    section[data-testid="stSidebar"] {
        background-color: #002366;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span {
        color: white !important;
    }

    </style>
""", unsafe_allow_html=True)

# --- Menú lateral ---
st.sidebar.title("💈 Menú")
st.sidebar.markdown("Navega entre las secciones del sistema:")

# Título principal
st.title("💈 Barbería - Panel Básico")

# --- Mostrar resumen general ---
st.subheader("📊 Resumen general")

total_cortes, total_ganancias = obtener_resumen()
st.markdown(f'<div class="info-card">✂️ Total de cortes realizados: <strong>{total_cortes or 0}</strong></div>', unsafe_allow_html=True)
st.markdown(f'<div class="info-card">💰 Ganancias acumuladas: <strong>₡{total_ganancias:,.2f}</strong></div>', unsafe_allow_html=True)

# --- Registrar nuevo corte ---
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

# --- Historial de cortes ---
st.subheader("📅 Historial de cortes registrados")

registros = obtener_registros()
if registros:
    st.table(registros)
else:
    st.info("Aún no se han registrado cortes.")



