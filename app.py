import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import urllib.parse
import base64
from PIL import Image
import io
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Nosotros, Lo Nuestro — M&F",
    page_icon="❤️",
    layout="wide"
)

# -------------------------------------------------------------
# 1. CONTROL DE ACCESO
# -------------------------------------------------------------
PASSWORD_CORRECTA = "Mafe2026"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔒 Acceso Privado")
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("form_login"):
            clave = st.text_input(
                "Contraseña:",
                type="password",
                placeholder="Ingresa la clave..."
            )
            if st.form_submit_button("💖 Entrar", use_container_width=True):
                if clave.strip() == PASSWORD_CORRECTA:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")
    st.stop()

# -------------------------------------------------------------
# 2. CONFIGURACIÓN Y ESTILOS (LÍNEAS CORTAS SIN CORTE)
# -------------------------------------------------------------
FECHA_INICIO = date(2026, 4, 21)
SPREADSHEET_ID = "1o6dSXS4nSyC3M-20RaOQzpRsxEyVySnuu5KdzIZLyAo"

css_parts = [
    "<style>",
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Montserrat:wght@400;600;800&"
    "family=Playfair+Display:ital,wght@0,700;1,400"
    "&display=swap');",
    ".stApp {",
    "  background: linear-gradient(",
    "    135deg, #fff5f7 0%, #ffe6eb 50%, #f3e8ff 100%",
    "  );",
    "}",
    ".title-header {",
    "  font-family: 'Playfair Display', serif;",
    "  font-size: 3.5rem;",
    "  font-weight: 700;",
    "  text-align: center;",
    "  background: linear-gradient(45deg, #e11d48, #9333ea);",
    "  -webkit-background-clip: text;",
    "  -webkit-text-fill-color: transparent;",
    "  margin-bottom: 0;",
    "  padding-top: 1rem;",
    "}",
    ".sub-header {",
    "  font-family: 'Montserrat', sans-serif;",
    "  text-align: center;",
    "  font-size: 1.2rem;",
    "  color: #be123c;",
    "  font-weight: 600;",
    "  letter-spacing: 3px;",
    "  margin-bottom: 2rem;",
    "}",
    ".initials-card {",
    "  background: rgba(255, 255, 255, 0.6);",
    "  backdrop-filter: blur(10px);",
    "  border-radius: 20px;",
    "  border: 2px solid #fecdd3;",
    "  padding: 30px;",
    "  text-align: center;",
    "  margin-bottom: 2rem;",
    "}",
    ".initials-text {",
    "  font-family: 'Playfair Display', serif;",
    "  font-size: 5rem;",
    "  font-weight: 700;",
    "  color: #e11d48;",
    "  letter-spacing: 5px;",
    "}",
    ".counter-box {",
    "  background: linear-gradient(135deg, #e11d48, #be123c);",
    "  color: white;",
    "  padding: 20px;",
    "  border-radius: 20px;",
    "  text-align: center;",
    "}",
    ".counter-number {",
