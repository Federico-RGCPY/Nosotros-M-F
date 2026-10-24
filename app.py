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
            sh.worksheet("Hitos").update(f"A{num}:{col}{num}", [[str(x) for x in fila]], value_input_option="USER_ENTERED")
            return True, None
        except Exception as e:
            return False, str(e)
    return False, err

def eliminar_hito(num):
    sh, err = conectar_sheet()
    if sh:
        try:
            sh.worksheet("Hitos").delete_rows(int(num))
            return True, None
        except Exception as e:
            return False, str(e)
    return False, err

# 3. ENCABEZADO Y CONTADOR
st.title("NOSOTROS, LO NUESTRO ❤️")
st.caption("CHILE 🇨🇱 ✈️ 🇵🇾 PARAGUAY | Macarena & Federico")

hoy = date.today()
dias_juntos = max(0, (hoy - FECHA_INICIO).days)
meses_cumplidos = max(0, (hoy.year - FECHA_INICIO.year) * 12 + hoy.month - FECHA_INICIO.month)

col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric(label="Días Juntos", value=f"{dias_juntos} Días")
with col_m2:
    st.metric(label="Meses Construyendo Nuestra Historia", value=f"{meses_cumplidos} Meses", delta="Desde el 21 de Abril de 2026")

if hoy.day == 21:
    st.balloons()
    st.success(f"🎉 ¡FELIZ CUMPLE MES! Hoy celebramos {meses_cumplidos} meses juntos.")

# 4. NAVEGACIÓN
c_menu, c_logout = st.columns([0.88, 0.12])
with c_menu:
    menu = st.radio("Secciones:", ["📖 Nuestra Línea de Tiempo", "📜 Los 10 Mandamientos", "📲 Celebrar en WhatsApp"], horizontal=True)
with c_logout:
    st.write("")
    if st.button("🔒 Salir"):
        st.session_state["autenticado"] = False
        st.rerun()

st.divider()

# SECCIÓN 1: HITOS
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

            if st.form_submit_button("💖 Guardar Recuerdo"):
                if not titulo or not descripcion:
                    st.error("Por favor ingresa un título y una descripción.")
                else:
                    creador_clean = "Maca" if "Maca" in creador else "Fede"
                    nuevo_registro = [
                        datetime.now().strftime("%Y%m%d%H%M%S"),
                        str(fecha_hito),
                        titulo.strip(),
                        categoria,
                        creador_clean,
                        descripcion.strip(),
                        procesar_imagen(foto_file),
                        0, 0, 0, 0
                    ]
                    exito, msg_err = guardar_hito(nuevo_registro)
                    if exito:
                        st.success("¡Recuerdo guardado con éxito!")
                        st.rerun()
                    else:
                        st.error(f"Error al guardar: {msg_err}")

    st.subheader("⏳ Nuestra Historia")
    df_hitos = obtener_datos("Hitos")

    if not df_hitos.empty:
        col_fecha = next((c for c in df_hitos.columns if "fecha" in str(c).lower()), "col_1" if "col_1" in df_hitos.columns else None)
        if col_fecha:
            df_hitos["_fecha_dt"] = pd.to_datetime(df_hitos[col_fecha], errors='coerce')
            df_hitos = df_hitos.sort_values(by="_fecha_dt", ascending=True)

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
                c_top1, c_top2 = st.columns([0.88, 0.12])
                with c_top1:
                    st.caption(f"{avatar} | 📅 {fecha_val} | {cat_val}")
                    st.subheader(titulo_val)
                    st.write(desc_val)
                with c_top2:
                    c_ed, c_del = st.columns(2)
                    with c_ed:
                        if st.button("✏️", key=f"edit_{fila_num}_{idx}"):
                            st.session_state[f"mode_{fila_num}"] = not st.session_state.get(f"mode_{fila_num}", False)
                    with c_del:
                        if st.button("❌", key=f"del_{fila_num}_{idx}"):
                            ok, err_del = eliminar_hito(fila_num)
                            if ok:
                                st.rerun()
                            else:
                                st.error(err_del)

                if foto_val and foto_val.startswith("data:image"):
                    st.image(foto_val, width=400)

                c1, c2, c3, c4, _ = st.columns([1, 1, 1, 1, 4])
                with c1:
                    if st.button(f"❤️ {r_amor}", key=f"r1_{fila_num}_{idx}"):
                        actualizar_hito(fila_num, [id_val, fecha_val, titulo_val, cat_val, creador_val.capitalize(), desc_val, foto_val, r_amor + 1, r_risa, r_aplauso, r_fuego])
                        st.rerun()
                with c2:
                    if st.button(f"😂 {r_risa}", key=f"r2_{fila_num}_{idx}"):
                        actualizar_hito(fila_num, [id_val, fecha_val, titulo_val, cat_val, creador_val.capitalize(), desc_val, foto_val, r_amor, r_risa + 1, r_aplauso, r_fuego])
                        st.rerun()
                with c3:
                    if st.button(f"👏 {r_aplauso}", key=f"r3_{fila_num}_{idx}"):
                        actualizar_hito(fila_num, [id_val, fecha_val, titulo_val, cat_val, creador_val.capitalize(), desc_val, foto_val, r_amor, r_risa, r_aplauso + 1, r_fuego])
                        st.rerun()
                with c4:
                    if st.button(f"🔥 {r_fuego}", key=f"r4_{fila_num}_{idx}"):
                        actualizar_hito(fila_num, [id_val, fecha_val, titulo_val, cat_val, creador_val.capitalize(), desc_val, foto_val, r_amor, r_risa, r_aplauso, r_fuego + 1])
                        st.rerun()

            if st.session_state.get(f"mode_{fila_num}", False):
                with st.container(border=True):
                    st.write(f"✏️ Editando: **{titulo_val}**")
                    with st.form(f"form_ed_{fila_num}"):
                        ce1, ce2, ce3 = st.columns([1, 1, 1])
                        with ce1:
                            c_edit = st.radio("Creador", ["👩 Maca", "👨 Fede"], index=0 if "maca" in creador_val else 1, key=f"c_{fila_num}")
                        with ce2:
                            try: dt_val = pd.to_datetime(fecha_val).date()
                            except Exception: dt_val = hoy
                            f_edit = st.date_input("Fecha", value=dt_val, key=f"f_{fila_num}")
                        with ce3:
                            opts = ["Viaje ✈️", "Anécdota 🤭", "Proyecto 🚀", "Regalo 🎁", "Cita a Distancia 💻", "Especial ❤️"]
                            idx_cat = opts.index(cat_val) if cat_val in opts else 0
                            cat_edit = st.selectbox("Categoría", opts, index=idx_cat, key=f"cat_{fila_num}")

                        t_edit = st.text_input("Título", value=titulo_val, key=f"t_{fila_num}")
                        d_edit = st.text_area("Descripción", value=desc_val, key=f"d_{fila_num}")
                        f_edit_file = st.file_uploader("Reemplazar foto", type=["jpg", "png", "jpeg"], key=f"file_{fila_num}")

                        if st.form_submit_button("Guardar Cambios"):
                            c_clean = "Maca" if "Maca" in c_edit else "Fede"
                            f_b64 = procesar_imagen(f_edit_file) if f_edit_file else foto_val
                            actualizar_hito(fila_num, [id_val, str(f_edit), t_edit.strip(), cat_edit, c_clean, d_edit.strip(), f_b64, r_amor, r_risa, r_aplauso, r_fuego])
                            st.session_state[f"mode_{fila_num}"] = False
                            st.rerun()
    else:
        st.info("Aún no hay recuerdos registrados. ¡Abre el panel de arriba para registrar el primero!")

# SECCIÓN 2: MANDAMIENTOS
elif menu == "📜 Los 10 Mandamientos":
    st.subheader("📜 Nuestras Promesas")
    df_m = obtener_datos("Mandamientos")
    if not df_m.empty:
        col_m1, col_m2 = st.columns(2)
        for idx, r in df_m.iterrows():
            target = col_m1 if idx % 2 == 0 else col_m2
            with target:
                with st.container(border=True):
                    st.caption(f"Mandamiento #{r.get('numero', idx+1)}")
                    st.subheader(r.get('titulo', ''))
                    st.write(r.get('descripcion', ''))

# SECCIÓN 3: WHATSAPP
elif menu == "📲 Celebrar en WhatsApp":
    st.subheader("💬 Enviar Mensaje Romántico")
    dest = st.radio("Destinatario:", ["A Macarena 👩🇨🇱", "A Federico 👨🇵🇾"], horizontal=True)
    msj = st.text_area("Mensaje:", value=f"¡Feliz Cumple Mes #{meses_cumplidos} mi amor! ❤️\n\nHoy celebramos {dias_juntos} días juntos a pesar de la distancia.\n\nTe amo muchísimo de Chile a Paraguay. ✈️💖", height=150)
    url_wa = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msj)}"
    st.link_button("🟢 Abrir en WhatsApp y Enviar", url_wa, use_container_width=True)
