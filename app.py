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
# 1. CONFIGURACIÓN Y CONSTANTES
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nosotros, Lo Nuestro — M&F",
    page_icon="❤️",
    layout="wide"
)

FECHA_INICIO = date(2026, 4, 21)
SPREADSHEET_ID = "1o6dSXS4nSyC3M-20RaOQzpRsxEyVySnuu5KdzIZLyAo"
PASSWORD_CORRECTA = "Mafe2026"

MANDAMIENTOS_DEFAULT = [
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
]

# -----------------------------------------------------------------------------
# 2. ACCESO PROTEGIDO
# -----------------------------------------------------------------------------
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
            btn_entrar = st.form_submit_button("💖 Entrar", use_container_width=True)
            if btn_entrar:
                if clave.strip() == PASSWORD_CORRECTA:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta. Inténtalo de nuevo.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. CONEXIÓN A GOOGLE SHEETS
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
        return None, "Faltan las credenciales en st.secrets."

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
        bytes_data = buffered.getvalue()
        b64_bytes = base64.b64encode(bytes_data)
        img_str = b64_bytes.decode()
        return f"data:image/jpeg;base64,{img_str}"
    except Exception:
        return ""

def limpiar_key(texto):
    reemplazos = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"))
    s = str(texto).lower().strip()
    for a, b in reemplazos:
        s = s.replace(a, b)
    return s

def obtener_datos(pestana_nombre):
    sh, err = conectar_sheet()
    if not sh:
        st.warning(f"Aviso de conexión ({pestana_nombre}): {err}")
        return pd.DataFrame(MANDAMIENTOS_DEFAULT if pestana_nombre == "Mandamientos" else [])

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
        return pd.DataFrame(MANDAMIENTOS_DEFAULT)
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
        try:
            ws = sh.worksheet("Hitos")
            num_cols = len(datos_actualizados)
            col_letra = chr(64 + num_cols) if num_cols <= 26 else "K"
            rango = f"A{fila_num}:{col_letra}{fila_num}"
            ws.update(rango, [[str(x) for x in datos_actualizados]], value_input_option="USER_ENTERED")
            return True, None
        except Exception as e:
            return False, str(e)
    return False, err

def eliminar_hito(fila_num):
    sh, err = conectar_sheet()
    if sh:
        try:
            ws = sh.worksheet("Hitos")
            ws.delete_rows(int(fila_num))
            return True, None
        except Exception as e:
            return False, str(e)
    return False, err

# -----------------------------------------------------------------------------
# 4. ENCABEZADO Y CONTADOR
# -----------------------------------------------------------------------------
st.title("NOSOTROS, LO NUESTRO")
st.caption("CHILE 🇨🇱 ✈️ 🇵🇾 PARAGUAY | Macarena & Federico")

hoy = date.today()
dias_juntos = (hoy - FECHA_INICIO).days
meses_cumplidos = (hoy.year - FECHA_INICIO.year) * 12 + hoy.month - FECHA_INICIO.month

col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric(label="Días Juntos", value=f"{max(0, dias_juntos)} días")
with col_m2:
    st.metric(label="Meses de Historia", value=f"{max(0, meses_cumplidos)} meses", delta="Desde el 21 de Abril de 2026")

if hoy.day == 21:
    st.balloons()
    st.success(f"🎉 ¡FELIZ CUMPLE MES MI AMOR! Hoy celebramos {max(0, meses_cumplidos)} meses de elegirnos. ❤️")

# -----------------------------------------------------------------------------
# 5. NAVEGACIÓN
# -----------------------------------------------------------------------------
c_menu, c_
