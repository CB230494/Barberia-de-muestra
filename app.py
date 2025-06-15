import streamlit as st
from database import init_db, registrar_cortes, obtener_registros, obtener_resumen
from datetime import date
import sqlite3
import pandas as pd

init_db()

# --- ESTILOS PARA MÓVIL (FULLSCREEN + NATIVO) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #800000;
        height: 100vh;
        margin: 0;
        padding: 0;
        overflow-x: hidden;
    }

    .block-container {
        background-color: white;
        padding: 2rem 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        margin: 0 auto;
        max-width: 600px;
        color: black;
    }

    .info-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.2rem;
        font-size: 1.1rem;
        color: black;
    }

    h1, h2, h3, label, .stTextInput label, .stNumberInput label, .stDateInput label {
        color: #800000 !important;
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

    button[kind="primary"] {
        background-color: #800000 !important;
        color: white !important;
        border: none;
        border-radius: 8px;
    }

    button[kind="primary"]:hover {
        background-color: #a00000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
st.sidebar.title("💈 Menú")
st.sidebar.markdown("Navega entre las secciones del sistema:")

# --- CONTENIDO CENTRAL ---
with st.container():
    st.title("💈 Barbería - Panel Básico")

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

    st.subheader("📅 Historial de cortes registrados")
    registros = obtener_registros()

    if registros:
        df = pd.DataFrame(registros, columns=["Fecha", "Cantidad de cortes", "Ganancias"])

        for i, row in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2.5, 1.5, 2, 1, 1])
            with col1:
                st.write(f"📅 {row['Fecha']}")
            with col2:
                st.write(f"✂️ {int(row['Cantidad de cortes'])}")
            with col3:
                st.write(f"💰 ₡{row['Ganancias']:.2f}")
            with col4:
                if st.button("✏️ Editar", key=f"edit_{i}"):
                    with st.form(f"form_edit_{i}", clear_on_submit=False):
                        new_cortes = st.number_input("Editar cantidad de cortes", min_value=0, value=int(row['Cantidad de cortes']), key=f"cortes_{i}")
                        new_ganancias = st.number_input("Editar ganancia (₡)", min_value=0.0, value=float(row['Ganancias']), step=0.01, format="%.2f", key=f"ganancia_{i}")
                        submitted = st.form_submit_button("Actualizar")
                        if submitted:
                            conn = sqlite3.connect("barberia.db")
                            cursor = conn.cursor()
                            cursor.execute("UPDATE cortes SET cantidad_cortes = ?, ganancias = ? WHERE fecha = ?",
                                           (new_cortes, new_ganancias, row["Fecha"]))
                            conn.commit()
                            conn.close()
                            st.success("✅ Registro actualizado correctamente")
                            st.experimental_rerun()
            with col5:
                if st.button("🗑️", key=f"del_{i}"):
                    conn = sqlite3.connect("barberia.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM cortes WHERE fecha = ?", (row["Fecha"],))
                    conn.commit()
                    conn.close()
                    st.experimental_rerun()
    else:
        st.info("Aún no se han registrado cortes.")

    # --- RESUMEN FINAL ---
    st.subheader("📊 Resumen general")
    total_cortes, total_ganancias = obtener_resumen()
    st.markdown(
        f'<div class="info-card">✂️ Total de cortes realizados: <strong>{total_cortes}</strong></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="info-card">💰 Ganancias acumuladas: <strong>₡{total_ganancias:.2f}</strong></div>',
        unsafe_allow_html=True
    )


