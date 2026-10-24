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

def verificar_contrasena():
    if st.session_state.get("autenticado", False):
        return True

    st.title("❤️ Nosotros, Lo Nuestro")
    st.subheader("M & F — Macarena & Federico")
    st.info("🔒 Ingresa la contraseña para acceder a nuestro espacio.")

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("form_login_mf"):
            clave = st.text_input("Contraseña:", type="password", placeholder="Ingresa la clave...")
            btn_acceder = st.form_submit_button("💖 Entrar", use_container_width=True)

            if btn_acceder:
                if clave == PASSWORD_CORRECTA:
                    st.session_state["autenticado"] = True
                    st.success("¡Bienvenido! ❤️")
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta. Inténtalo de nuevo.")

    return False

if not verificar_contrasena():
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
            creds_dict = json.loads(str(st.secrets["gcp_json"]).strip("'\""), strict=False)
        except Exception as e:
            return None, f"Error en gcp_json: {e}"

    if not creds_dict:
        return None, "Falta la configuración de credenciales en Secrets."

    try:
        pk = creds_dict.get("private_key", "")
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
    """Carga todas las filas sin límite desde la pestaña seleccionada."""
    sh, err = conectar_sheet()
    if sh:
        try:
            ws = sh.worksheet(pestana_nombre)
            vals = ws.get_all_values()

            if len(vals) >= 1:
                headers_raw = [str(h).strip() for h in vals[0]]
                data = vals[1:]

                rows_clean = []
                for idx, r in enumerate(data):
                    # Solo ignorar filas donde literalmente no haya texto en ninguna columna
                    if not any(str(c).strip() for c in r):
                        continue

                    row_dict = {}
                    for c_idx, val in enumerate(r):
                        row_dict[f"col_{c_idx}"] = val
                        if c_idx < len(headers_raw):
                            clean_k = limpiar_key(headers_raw[c_idx])
                            row_dict[clean_k] = val
                            row_dict[headers_raw[c_idx]] = val

                    # Guardar número de fila exacto en Sheets para editar/borrar
                    row_dict["_fila_num"] = idx + 2
                    rows_clean.append(row_dict)

                return pd.DataFrame(rows_clean)
        except Exception:
            pass

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

dias_mostrar = max(0, dias_juntos)
meses_mostrar = max(0, meses_cumplidos)

col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric(label="Días Juntos", value=f"{dias_mostrar} días")
with col_m2:
    st.metric(label="Meses de Historia", value=f"{meses_mostrar} meses", delta="Desde el 21 de Abril de 2026")

if hoy.day == 21:
    st.balloons()
    st.success(f"🎉 ¡FELIZ CUMPLE MES MI AMOR! Hoy celebramos {meses_mostrar} meses de elegirnos. ❤️")

# -----------------------------------------------------------------------------
# 5. MENÚ DE NAVEGACIÓN Y CERRAR SESIÓN
# -----------------------------------------------------------------------------
c_menu, c_logout = st.columns([0.85, 0.15])
with c_menu:
    menu = st.radio(
        "Navegación:",
        ["📖 Nuestra Línea de Tiempo", "📜 Los 10 Mandamientos", "📲 Celebrar en WhatsApp"],
        horizontal=True
    )
with c_logout:
    st.write("")
    if st.button("🔒 Salir"):
        st.session_state["autenticado"] = False
        st.rerun()

st.divider()

# =============================================================================
# SECCIÓN 1: LÍNEA DE TIEMPO DE HITOS (CARGA COMPLETA Y ORDENADA)
# =============================================================================
if menu == "📖 Nuestra Línea de Tiempo":

    with st.expander("✨ Agregar un Nuevo Recuerdo", expanded=False):
        with st.form("form_hito", clear_on_submit=True):
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                creador = st.radio("¿Quién registra?", ["👩 Maca", "👨 Fede"], horizontal=True)
            with c2:
                fecha_hito = st.date_input("Fecha del Recuerdo", value=hoy)
            with c3:
                categoria = st.selectbox("Categoría", ["Viaje ✈️", "Anécdota 🤭", "Proyecto 🚀", "Regalo 🎁", "Cita a Distancia 💻", "Especial ❤️"])

            titulo = st.text_input("Título *", placeholder="Ej: Nuestra primera videollamada...")
            descripcion = st.text_area("Descripción / Sentimientos *", placeholder="Escribe aquí los detalles...")
            foto_file = st.file_uploader("📸 Adjuntar Fotografía (Opcional)", type=["jpg", "png", "jpeg"])

            submitted = st.form_submit_button("💖 Guardar Recuerdo")

            if submitted:
                if not titulo or not descripcion:
                    st.error("Por favor ingresa un título y una descripción.")
                else:
                    creador_clean = "Maca" if "Maca" in creador else "Fede"
                    foto_b64 = procesar_imagen(foto_file)

                    nuevo_registro = [
                        datetime.now().strftime("%Y%m%d%H%M%S"),
                        str(fecha_hito),
                        titulo.strip(),
                        categoria,
                        creador_clean,
                        descripcion.strip(),
                        foto_b64,
                        0, 0, 0, 0
                    ]
                    exito, msg_err = guardar_hito(nuevo_registro)
                    if exito:
                        st.success("✨ ¡Recuerdo guardado con éxito!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error al guardar: {msg_err}")

    st.subheader("⏳ Nuestra Historia")

    df_hitos = obtener_datos("Hitos")

    if not df_hitos.empty:
        col_fecha = None
        for col in df_hitos.columns:
            if "fecha" in str(col).lower():
                col_fecha = col
                break

        if not col_fecha and "col_1" in df_hitos.columns:
            col_fecha = "col_1"

        if col_fecha:
            df_hitos["_fecha_dt"] = pd.to_datetime(df_hitos[col_fecha], errors='coerce')
            df_hitos = df_hitos.sort_values(by="_fecha_dt", ascending=True)

        total_recuerdos = len(df_hitos)

        # Filtros de visualización para asegurar carga total sin trabar el navegador
        c_orden, c_vista = st.columns([1, 1])
        with c_orden:
            orden = st.selectbox("Orden:", ["Más antiguos primero (Cronológico)", "Más recientes primero"])
        with c_vista:
            filtro_autor = st.selectbox("Filtrar por autor:", ["Todos", "👩 Solo Maca", "👨 Solo Fede"])

        if orden == "Más recientes primero":
            df_hitos = df_hitos.iloc[::-1]

        if filtro_autor == "👩 Solo Maca":
            df_hitos = df_hitos[df_hitos["col_4"].astype(str).str.lower().str.contains("maca")]
        elif filtro_autor == "👨 Solo Fede":
            df_hitos = df_hitos[df_hitos["col_4"].astype(str).str.lower().str.contains("fede")]

        st.caption(f"Mostrando **{len(df_hitos)}** de **{total_recuerdos}** recuerdos registrados en total.")

        for idx, r in df_hitos.iterrows():
            id_val = str(r.get("id", r.get("col_0", datetime.now().strftime("%Y%m%d%H%M%S"))))
            fecha_val = str(r.get("fecha", r.get("col_1", "")))
            titulo_val = str(r.get("titulo", r.get("col_2", "")))
            cat_val = str(r.get("categoria", r.get("col_3", "")))
            creador_val = str(r.get("creador", r.get("col_4", ""))).strip().lower()
            desc_val = str(r.get("descripcion", r.get("col_5", "")))
            foto_val = str(r.get("foto", r.get("col_6", "")))

            try: r_amor = int(r.get("col_7", 0))
            except Exception: r_amor = 0
            try: r_risa = int(r.get("col_8", 0))
            except Exception: r_risa = 0
            try: r_aplauso = int(r.get("col_9", 0))
            except Exception: r_aplauso = 0
            try: r_fuego = int(r.get("col_10", 0))
            except Exception: r_fuego = 0

            fila_num = r.get("_fila_num")
            avatar = "👩 Maca" if "maca" in creador_val else "👨 Fede"

            with st.container(border=True):
                c_top1, c_top2 = st.columns([0.85, 0.15])
                with c_top1:
                    st.markdown(f"**{avatar}** &nbsp;|&nbsp; 📅 {fecha_val} &nbsp;|&nbsp; 🏷️ {cat_val}")
                    st.subheader(titulo_val)
                    st.write(desc_val)
                with c_top2:
                    c_ed, c_dl = st.columns(2)
                    with c_ed:
                        if st.button("✏️", key=f"btn_edit_{fila_num}_{idx}", help="Editar"):
                            st.session_state[f"edit_mode_{fila_num}"] = not st.session_state.get(f"edit_mode_{fila_num}", False)
                    with c_dl:
                        if st.button("❌", key=f"btn_del_{fila_num}_{idx}", help="Eliminar"):
                            ok_del, err_del = eliminar_hito(fila_num)
                            if ok_del:
                                st.success("Eliminado.")
                                st.rerun()
                            else:
                                st.error(f"Error: {err_del}")

                if foto_val and foto_val.startswith("data:image"):
                    st.image(foto_val, width=400)

                c_r1, c_r
