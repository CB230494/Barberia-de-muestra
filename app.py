import streamlit as st
from database import init_db, registrar_cortes, obtener_registros, obtener_resumen
from datetime import date

# Inicializar base de datos
init_db()

# --- Estilos personalizados ---
st.markdown("""
    <style>
    /* Fondo degradado */
    .stApp {
        background: linear-gradient(to bottom right, #f2f6ff, #e6e6ff);
        color: #000000;
    }

    /* Tarjetas de resumen */
    .info-card {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 1rem;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #001F54;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #002366;
    }
    .css-1d391kg {  /* encabezado sidebar */
        color: white;
    }
    .css-1v3fvcr {  /* texto en sidebar */
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Menú lateral ---
st.sidebar.title("Menú 💈")
opcion = st.sidebar.radio("Ir a:", ["Resumen general", "Registrar cortes", "Historial de cortes"])

# --- Página: Resumen general ---
if opcion == "Resumen general":
    st.title("💈 Barbería - Panel General")
    total_cortes, total_ganancias = obtener_resumen()
    
    st.markdown('<div class="info-card">✂️ Total de cortes realizados: <strong>{}</strong></div>'.format(total_cortes or 0), unsafe_allow_html=True)
    st.markdown('<div class="info-card">💰 Ganancias acumuladas: <strong>₡{:,.2f}</strong></div>'.format(total_ganancias or 0), unsafe_allow_html=True)

# --- Página: Registro ---
elif opcion == "Registrar cortes":
    st.title("📅 Registrar cortes del día")
    
    fecha = st.date_input("Fecha", date.today())
    cantidad = st.number_input("Cantidad de cortes", min_value=0, step=1)
    ganancias = st.number_input("Ganancia total del día (₡)", min_value=0.0, step=100.0, format="%.2f")

    if st.button("Guardar"):
        exito = registrar_cortes(str(fecha), cantidad, ganancias)
        if exito:
            st.success("✅ Registro guardado correctamente")
        else:
            st.warning("⚠️ Ya existe un registro para esa fecha.")

# --- Página: Historial ---
elif opcion == "Historial de cortes":
    st.title("📊 Historial de cortes")
    registros = obtener_registros()
    if registros:
        st.table(registros)
    else:
        st.info("Aún no se han registrado cortes.")


