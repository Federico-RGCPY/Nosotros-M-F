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

        if col_fecha:
            df_hitos["_fecha_dt"] = pd.to_datetime(df_hitos[col_fecha], errors='coerce')
            df_hitos = df_hitos.sort_values(by="_fecha_dt", ascending=True)

        total_recuerdos = len(df_hitos)

        c_orden, c_vista = st.columns([1, 1])
        with c_orden:
            orden = st.selectbox("Orden:", ["Más antiguos primero (Cronológico)", "Más recientes primero"])
        with c_vista:
            filtro_autor = st.selectbox("Filtrar por autor:", ["Todos", "👩 Solo Maca", "👨 Solo Fede"])

        if orden == "Más recientes primero":
            df_hitos = df_hitos.iloc[::-1]

        col_creador = next((c for c in df_hitos.columns if "creador" in c), None)
        if col_creador:
            if filtro_autor == "👩 Solo Maca":
                df_hitos = df_hitos[df_hitos[col_creador].astype(str).str.lower().str.contains("maca")]
            elif filtro_autor == "👨 Solo Fede":
                df_hitos = df_hitos[df_hitos[col_creador].astype(str).str.lower().str.contains("fede")]

        st.caption(f"Mostrando **{len(df_hitos)}** de **{total_recuerdos}** recuerdos en total.")

        for idx, r in df_hitos.iterrows():
            id_val = str(r.get("id", datetime.now().strftime("%Y%m%d%H%M%S")))
            fecha_val = str(r.get("fecha", ""))
            titulo_val = str(r.get("titulo", ""))
            cat_val = str(r.get("categoria", ""))
            creador_val = str(r.get("creador", "")).strip().lower()
            desc_val = str(r.get("descripcion", ""))
            foto_val = str(r.get("foto", ""))

            cols_r = [c for c in df_hitos.columns if "reaccion" in c]
            try:
                r_amor = int(r[cols_r[0]]) if len(cols_r) > 0 else 0
            except Exception:
                r_amor = 0
            try:
                r_risa = int(r[cols_r[1]]) if len(cols_r) > 1 else 0
            except Exception:
                r_risa = 0
            try:
                r_aplauso = int(r[cols_r[2]]) if len(cols_r) > 2 else 0
            except Exception:
                r_aplauso = 0
            try:
                r_fuego = int(r[cols_r[3]]) if len(cols_r) > 3 else 0
            except Exception:
                r_fuego = 0

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

                c_r1, c_r2, c_r3, c_r4, _ = st.columns([1, 1, 1, 1, 4])
                with c_r1:
                    if st.button(f"❤️ {r_amor}", key=f"react_a_{fila_num}_{idx}"):
                        datos_act = [id_val, fecha_val, titulo_val, cat_val, creador_val.capitalize(), desc_val, foto_val, r_amor + 1, r_risa, r_aplauso, r_fuego]
                        actualizar_hito(fila_num, datos_act)
                        st.rerun()
                with c_r2:
                    if st.button(f"😂 {r_risa}", key=f"react_r_{fila_num}_{idx}"):
                        datos_act = [id_val, fecha_val, titulo_val, cat_val, creador_val.capitalize(), desc_val, foto_val, r_amor, r_risa + 1, r_aplauso, r_fuego]
                        actualizar_hito(fila_num, datos_act)
                        st.rerun()
                with c_r3:
                    if st.button(f"👏 {r_aplauso}", key=f"react_ap_{fila_num}_{idx}"):
                        datos_act = [id_val, fecha_val, titulo_val, cat_val, creador_val.capitalize(), desc_val, foto_val, r_amor, r_risa, r_aplauso + 1, r_fuego]
                        actualizar_hito(fila_num, datos_act)
                        st.rerun()
                with c_r4:
                    if st.button(f"🔥 {r_fuego}", key=f"react_f_{fila_num}_{idx}"):
                        datos_act = [id_val, fecha_val, titulo_val, cat_val, creador_val.capitalize(), desc_val, foto_val, r_amor, r_risa, r_aplauso, r_fuego + 1]
                        actualizar_hito(fila_num, datos_act)
                        st.rerun()

            if st.session_state.get(f"edit_mode_{fila_num}", False):
                with st.container(border=True):
                    st.info(f"✏️ Editando: {titulo_val}")
                    with st.form(f"form_edit_{fila_num}"):
                        ce1, ce2, ce3 = st.columns([1, 1, 1])
                        with ce1:
                            creador_edit = st.radio("Creador", ["👩 Maca", "👨 Fede"], index=0 if "maca" in creador_val else 1, key=f"c_ed_{fila_num}")
                        with ce2:
                            try:
                                default_dt = pd.to_datetime(fecha_val).date()
                            except Exception:
                                default_dt = hoy
                            fecha_edit = st.date_input("Fecha", value=default_dt, key=f"f_ed_{fila_num}")
                        with ce3:
                            cat_list = ["Viaje ✈️", "Anécdota 🤭", "Proyecto 🚀", "Regalo 🎁", "Cita a Distancia 💻", "Especial ❤️"]
                            cat_index = cat_list.index(cat_val) if cat_val in cat_list else 0
                            cat_edit = st.selectbox("Categoría", cat_list, index=cat_index, key=f"cat_ed_{fila_num}")

                        titulo_edit = st.text_input("Título", value=titulo_val, key=f"t_ed_{fila_num}")
                        desc_edit = st.text_area("Descripción", value=desc_val, key=f"d_ed_{fila_num}")
                        foto_edit_file = st.file_uploader("📸 Reemplazar Foto", type=["jpg", "png", "jpeg"], key=f"foto_ed_{fila_num}")

                        if st.form_submit_button("💾 Guardar Cambios"):
                            creador_clean_edit = "Maca" if "Maca" in creador_edit else "Fede"
                            foto_nueva_b64 = procesar_imagen(foto_edit_file) if foto_edit_file else foto_val

                            datos_act = [
                                id_val,
                                str(fecha_edit),
                                titulo_edit.strip(),
                                cat_edit,
                                creador_clean_edit,
                                desc_edit.strip(),
                                foto_nueva_b64,
                                r_amor, r_risa, r_aplauso, r_fuego
                            ]
                            ok_upd, err_upd = actualizar_hito(fila_num, datos_act)
                            if ok_upd:
                                st.success("✨ Actualizado.")
                                st.session_state[f"edit_mode_{fila_num}"] = False
                                st.rerun()
                            else:
                                st.error(f"Error: {err_upd}")
    else:
        st.info("Aún no hay recuerdos registrados. ¡Abre el panel superior para registrar el primero!")

elif menu == "📜 Los 10 Mandamientos":
    st.subheader("📜 Nuestras Promesas")
    st.caption("Reglas que guían y protegen nuestra historia.")

    df_mandamientos = obtener_datos("Mandamientos")

    if not df_mandamientos.empty:
        col_m1, col_m2 = st.columns(2)

        for idx, r in df_mandamientos.iterrows():
            target_col = col_m1 if idx % 2 == 0 else col_m2
            num_val = r.get("numero", idx + 1)
            titulo_val = r.get("titulo", "")
            desc_val = r.get("descripcion", "")

            with target_col:
                with st.container(border=True):
                    st.markdown(f"**Mandamiento #{num_val}**")
                    st.subheader(titulo_val)
                    st.write(desc_val)

elif menu == "📲 Celebrar en WhatsApp":
    st.subheader("💬 Enviar Mensaje")

    destinatario = st.radio("¿A quién le vas a enviar el mensaje?", ["A Macarena 👩🇨🇱", "A Federico 👨🇵🇾"], horizontal=True)

    msj_default = f"¡Feliz Cumple Mes #{max(0, meses_cumplidos)} mi amor! ❤️\n\nHoy celebramos {max(0, dias_juntos)} días construyendo nuestra historia. Gracias por elegirme todos los días a pesar de la distancia.\n\nTe amo muchísimo, de Chile a Paraguay y de regreso. ✈️💖"

    mensaje_personalizado = st.text_area("Edita tu mensaje aquí:", value=msj_default, height=150)

    msj_encoded = urllib.parse.quote(mensaje_personalizado)
    url_wa = f"https://api.whatsapp.com/send?text={msj_encoded}"

    st.link_button("🟢 Abrir en WhatsApp y Enviar", url_wa, use_container_width=True)
