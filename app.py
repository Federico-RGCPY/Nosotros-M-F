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
# 1. CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nosotros, Lo Nuestro — M&F",
    page_icon="❤️",
    layout="wide"
)

FECHA_INICIO = date(2026, 4, 21)
SPREADSHEET_ID = "1o6dSXS4nSyC3M-20RaOQzpRsxEyVySnuu5KdzIZLyAo"

# -----------------------------------------------------------------------------
# 2. CONTROL DE ACCESO POR CONTRASEÑA
# -----------------------------------------------------------------------------
PASSWORD_CORRECTA = "Mafe2026"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("❤️ Nosotros, Lo Nuestro")
    st.subheader("M & F — Macarena & Federico")
    st.info("🔒 Ingresa la contraseña para acceder a nuestro espacio.")

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("form_login_mf"):
            clave = st.text_input("Contraseña:", type="password", placeholder="Ingresa la clave...")
            btn_acceder = st.form_submit_button("💖 Entrar", use_container_width=True)

            if btn_acceder:
                if clave.strip() == PASSWORD_CORRECTA:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta. Inténtalo de nuevo.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. CONEXIÓN Y OPERACIONES EN GOOGLE SHEETS
# -----------------------------------------------------------------------------
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def conectar_sheet():
    creds_dict = None
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
    elif "gcp_json" in st.secrets:
        try:
            raw = str(st.secrets["gcp_json"]).strip().strip("'\"")
            creds_dict = json.loads(raw, strict=False)
        except Exception as e:
            return None, f"Error en formato gcp_json: {e}"

    if not creds_dict:
        return None, "Faltan las credenciales en st.secrets (gcp_service_account o gcp_json)."

    try:
        pk = str(creds_dict.get("private_key", ""))
        if "\\n" in pk:
            creds_dict["private_key"] = pk.replace("\\n", "\n")

        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(credentials)
        sh = gc.open_by_key(SPREADSHEET_ID)
        return sh, None
    except Exception as e:
        return None, str(e)

def procesar_imagen(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        image = Image.open(uploaded_file)
        image.thumbnail((800, 800))
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=75)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    except Exception:
        return ""

def limpiar_key(texto):
    replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
    s = str(texto).lower().strip()
    for a, b in replacements:
        s = s.replace(a, b)
    return s

def obtener_datos(pestana_nombre):
    sh, err = conectar_sheet()
    if not sh:
        st.warning(f"Aviso de conexión ({pestana_nombre}): {err}")
        return pd.DataFrame()

    try:
        ws = sh.worksheet(pestana_nombre)
        vals = ws.get_all_values()

        if len(vals) >= 2:
            headers = [limpiar_key(h) for h in vals[0]]
            data = vals[1:]

            data_filtrada = []
            filas_num = []
            for i, row in enumerate(data):
                if any(str(c).strip() for c in row):
                    if len(row) < len(headers):
                        row = row + [""] * (len(headers) - len(row))
                    else:
                        row = row[:len(headers)]
                    data_filtrada.append(row)
                    filas_num.append(i + 2)

            df = pd.DataFrame(data_filtrada, columns=headers)
            df["_fila_num"] = filas_num
            return df
    except Exception as e:
        st.warning(f"No se pudo leer la pestaña '{pestana_nombre}': {e}")

    if pestana_nombre == "Mandamientos":
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

def guardar_hito(nuevo_hito):
    sh, err = conectar_sheet()
    if sh:
        try:
            ws = sh.worksheet("Hitos")
            ws.append_row([str(x) for x in nuevo_hito], value_input_option="USER_ENTERED")
            return True, None
        except Exception as e:
            return False, f"Error al escribir en Hitos: {e}"
    return False, f"Sin conexión: {err}"

def actualizar_hito(fila_num, datos_actualizados):
    sh, err = conectar_sheet()
    if sh:
