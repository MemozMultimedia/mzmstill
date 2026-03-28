import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import re

# =====================
# DB SETUP
# =====================
conn = sqlite3.connect("datos_app.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    correo TEXT,
    telefono TEXT,
    descripcion TEXT,
    fecha TEXT
)
""")
conn.commit()

def validar_email(email):
    patron = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(patron, email)

def guardar(nombre, correo, telefono, descripcion, fecha):
    if nombre and correo and validar_email(correo):
        cursor.execute("""
        INSERT INTO registros (nombre, correo, telefono, descripcion, fecha)
        VALUES (?, ?, ?, ?, ?)
        """, (nombre, correo, telefono, descripcion, fecha))
        conn.commit()
        return True
    return False

def obtener_datos():
    return pd.read_sql_query("SELECT * FROM registros ORDER BY fecha DESC", conn)

# =====================
# UI STREAMLIT - Formulario YAMB
# =====================
st.set_page_config(page_title="Formulario YAMB", layout="wide")

st.title("📋 Formulario YAMB - CRM de Contactos")

st.sidebar.header("➕ Nuevo Registro")

with st.sidebar.form("registro_form"):
    nombre = st.text_input("Nombre")
    correo = st.text_input("Correo")
    telefono = st.text_input("Teléfono")
    descripcion = st.text_area("Descripción")
    fecha = st.date_input("Fecha", datetime.today())
    submit = st.form_submit_button("Guardar")

if submit:
    if not validar_email(correo):
        st.sidebar.error("⚠️ Formato de correo inválido")
    elif guardar(nombre, correo, telefono, descripcion, str(fecha)):
        st.sidebar.success("✅ Guardado correctamente")
        st.rerun()
    else:
        st.sidebar.error("⚠️ Nombre y Correo válido son obligatorios")

st.subheader("📊 Registros Existentes")

df = obtener_datos()
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No hay registros todavía.")
