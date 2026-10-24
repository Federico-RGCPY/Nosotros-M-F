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

st.set_page_config(page_title="Nosotros, Lo Nuestro — M&F", page_icon="❤️", layout="wide")

PASSWORD_CORRECTA = "Mafe2026"
FECHA_INICIO = date(2026, 4, 21)
SPREADSHEET_ID = "1o6dSXS4nSyC3M-20RaOQzpRsxEyVySnuu5KdzIZLyAo"

# 1. AUTENTICACIÓN
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔒 Acceso Privado — M&F")
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("form_login"):
            clave = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("💖 Entrar", use_container_width=True):
                if clave.strip() == PASSWORD_CORRECTA:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")
    st.stop()

# 2. CONEXIÓN A GOOGLE SHEETS
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def conectar_sheet():
    creds_dict = None
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
    elif "gcp_json" in st.secrets:
        try:
            creds_dict = json.loads(str(st.secrets["gcp_json"]).strip().strip("'\""), strict=False)
        except Exception as e:
            return None, f"Error en gcp_json: {e}"

    if not creds_dict:
        return None, "Falta la configuración de credenciales en Secrets."

    try:
        pk = str(creds_dict.get("private_key", ""))
        if "\\n" in pk:
            creds_dict["private_key"] = pk.replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(creds)
        return gc.open_by_key(SPREADSHEET_ID), None
    except Exception as e:
        return None, str(e)

def procesar_imagen(uploaded_file):
    if not uploaded_file:
        return ""
    try:
        img = Image.open(uploaded_file)
        img.thumbnail((800, 800))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"
    except Exception:
        return ""

def limpiar_key(txt):
    s = str(txt).lower().strip()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        s = s.replace(a, b)
    return s

def obtener_datos(pestana):
    sh, err = conectar_sheet()
    if sh:
        try:
            ws = sh.worksheet(pestana)
            vals = ws.get_all_values()
            if len(vals) >= 1:
                hdrs = [str(h).strip() for h in vals[0]]
                filas = []
                for idx, r in enumerate(vals[1:]):
                    if not any(str(c).strip() for c in r):
                        continue
                    d = {"_fila_num": idx + 2}
                    for c_idx, val in enumerate(r):
                        d[f"col_{c_idx}"] = val
                        if c_idx < len(hdrs):
                            d[limpiar_key(hdrs[c_idx])] = val
                            d[hdrs[c_idx]] = val
                    filas.append(d)
                return pd.DataFrame(filas)
        except Exception:
            pass

    if pestana == "Mandamientos":
        return pd.DataFrame([
            {"numero": "1", "titulo": "Comunicación sincera siempre", "descripcion": "Hablar de nuestras emociones con amor y transparencia."},
            {"numero": "2", "titulo": "Cuidar la distancia con detalles", "descripcion": "Recordarnos todos los días lo mucho que nos importamos."},
            {"numero": "3", "titulo": "Apoyar los sueños del otro", "descripcion": "Ser el refugio y el impulso mutuo en cada proyecto."},
            {"numero": "4", "titulo": "Celebrar cada 21", "descripcion": "Hacer de nuestro cumple mes un día especial sin importar la rutina."},
            {"numero": "5", "titulo": "Confianza ciega", "descripcion": "Construir la base de la relación en la lealtad y el respeto."},
            {"numero": "6", "titulo": "Tiempo de calidad a la distancia", "descripcion": "Compartir citas virtuales, películas o llamadas sin distracciones."},
            {"numero": "7", "titulo": "Planificar nuestro reencuentro", "descripcion": "Mantener viva la ilusión de los viajes y abrazos futuros."},
            {"numero": "8", "titulo": "Resolver los malentendidos con amor", "descripcion": "Nunca irnos a dormir enojados el uno con el otro."},
            {"numero": "9", "titulo": "Espacio personal e individualidad", "descripcion": "Acompañarnos sin perder el crecimiento propio."},
            {"numero": "10", "titulo": "Elegirnos todos los días", "descripcion": "Recordar por qué iniciamos esta historia aquel 21 de abril."}
        ])
    return pd.DataFrame()

def guardar_hito(fila):
    sh, err = conectar_sheet()
    if sh:
        try:
            sh.worksheet("Hitos").append_row([str(x) for x in fila], value_input_option="USER_ENTERED")
            return True, None
        except Exception as e:
            return False, str(e)
    return False, err

def actualizar_hito(num, fila):
    sh, err = conectar_sheet()
    if sh:
        try:
            col = chr(64 + len(fila)) if len(fila) <= 26 else "K"
            sh.works
