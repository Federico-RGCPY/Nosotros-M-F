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

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y CONTROL DE ACCESO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nosotros, Lo Nuestro — M&F",
    page_icon="❤️",
    layout="wide"
)

PASSWORD_CORRECTA = "Mafe2026"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: #be123c;'>🔒 Acceso Privado</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("form_login"):
            clave = st.text_input("Contraseña:", type="password", placeholder="Ingresa la clave...")
            if st.form_submit_button("💖 Entrar", use_container_width=True):
                if clave.strip() == PASSWORD_CORRECTA:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta. Inténtalo de nuevo.")
    st.stop()

FECHA_INICIO = date(2026, 4, 21)
SPREADSHEET_ID = "1o6dSXS4nSyC3M-20RaOQzpRsxEyVySnuu5KdzIZLyAo"

# Estilos CSS Románticos protegidos contra truncado
CSS_ROMANTICO = "".join([
    "<style>",
    "@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');",
    ".stApp { background: linear-gradient(135deg, #fff5f7 0%, #ffe6eb 50%, #f3e8ff 100%); }",
    ".title-header { font-family: 'Playfair Display', serif; font-size: 3.5rem; font-weight: 700; text-align: center; background: linear-gradient(45deg, #e11d48, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0; padding-top: 1rem; }",
    ".sub-header { font-family: 'Montserrat', sans-serif; text-align: center; font-size: 1.2rem; color: #be123c; font-weight: 600; letter-spacing: 3px; margin-bottom: 2rem; }",
    ".initials-card { background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(10px); border-radius: 20px; border: 2px solid #fecdd3; padding: 30px; text-align: center; box-shadow: 0 10px 30px -5px rgba(225, 29, 72, 0.15); margin-bottom: 2rem; }",
    ".initials-text { font-family: 'Playfair Display', serif; font-size: 5rem; font-weight: 700; color: #e11d48; letter-spacing: 5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.05); }",
    ".counter-box { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: white; padding: 20px; border-radius: 20px; text-align: center; box-shadow: 0 10px 20px rgba(225, 29, 72, 0.2); }",
    ".counter-number { font-size: 3rem; font-weight: 800; font-family: 'Montserrat', sans-serif; margin: 10px 0; }",
    ".card-maca { border-left: 6px solid #ec4899; background-color: #ffffff; padding: 20px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }",
    ".card-fede { border-left: 6px solid #0284c7; background-color: #ffffff; padding: 20px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }",
    ".tag-maca { background-color: #fce7f3; color: #be185d; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; }",
    ".tag-fede { background-color: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; }",
    ".mandamiento-card { background: #ffffff; border-radius: 15px; padding: 20px; border: 1px solid #ffe4e6; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(225, 29, 72, 0.05); }",
    "</style>"
])
st.markdown(CSS_ROMANTICO, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CONEXIÓN Y OPERACIONES EN GOOGLE SHEETS
# -----------------------------------------------------------------------------
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def conectar_sheet():
    creds_dict = None
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
    elif
