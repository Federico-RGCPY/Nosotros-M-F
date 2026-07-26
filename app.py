import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nosotros, Lo Nuestro — M&F",
    page_icon="❤️",
    layout="wide"
)

# 🗓️ FECHA DE INICIO DE LA RELACIÓN
FECHA_INICIO = date(2026, 4, 21)  

# 🔑 ID DE TU GOOGLE SHEET
SPREADSHEET_ID = "1cvt3CXiA4yWn-_OVUxbc3_-QoI4gLBW3"

# Estilos CSS Románticos y Modernos
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #fff5f7 0%, #ffe6eb 50%, #f3e8ff 100%);
    }
    
    .title-header {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(45deg, #e11d48, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
        padding-top: 1rem;
    }

    .sub-header {
        font-family: 'Montserrat', sans-serif;
        text-align: center;
        font-size: 1.2rem;
        color: #be123c;
        font-weight: 600;
        letter-spacing: 3px;
        margin-bottom: 2rem;
    }

    .initials-card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 2px solid #fecdd3;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px -5px rgba(225, 29, 72, 0.15);
        margin-bottom: 2rem;
    }

    .initials-text {
        font-family: 'Playfair Display', serif;
        font-size: 5rem;
        font-weight: 700;
        color: #e11d48;
        letter-spacing: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }

    .counter-box {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        color: white;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 20px rgba(225, 29, 72, 0.2);
    }

    .counter-number {
        font-size: 3rem;
        font-weight: 800;
        font-family: 'Montserrat', sans-serif;
        margin: 10px 0;
    }

    /* Tarjetas de Línea de Tiempo */
    .card-maca {
        border-left: 6px solid #ec4899;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    .card-fede {
        border-left: 6px solid #0284c7;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    .tag-maca {
        background-color: #fce7f3;
        color: #be185d;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .tag-fede {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* Pizarra de Mandamientos */
    .mandamiento-card {
        background: #ffffff;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #ffe4e6;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(225, 29, 72, 0.05);
        transition: transform 0.2s;
    }
    .mandamiento-card:hover {
        transform: translateY(-2px);
        border-color: #fecdd3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 2. CONEXIÓN Y LIMPIEZA DE CREDENCIALES
# -----------------------------------------------------------------------------
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def limpiar_private_key(key_raw: str) -> str:
    """Asegura que la clave PEM tenga el formato de saltos de línea correcto."""
    if not key_raw:
        return ""
    key = str(key_raw).strip("'\"")
    # Convertir secuencias escapadas en saltos de línea reales
    key = key.replace("\\\\n", "\n").replace("\\n", "\n")
    # Formatear encabezados si quedaron comprimidos
    if "-----BEGIN PRIVATE KEY-----" in key and "\n" not in key:
        key = key.replace("-----BEGIN PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----\n")
        key = key.replace("-----END PRIVATE KEY-----", "\n-----END PRIVATE KEY-----")
    return key.strip()

def conectar_sheet():
    creds_dict = None
    
    # Intento 1: Sección [gcp_service_account]
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
    # Intento 2: Bloque JSON gcp_json
    elif "gcp_json" in st.secrets:
        try:
            json_raw = str(st.secrets["gcp_json"]).strip("'\"")
            creds_dict = json.loads(json_raw, strict=False)
        except Exception as e:
            return None, f"Error al parsear gcp_json: {e}"
            
    if not creds_dict:
        return None, "Falta la configuración de credenciales en los Secrets de Streamlit."

    try:
        if "private_key" in creds_dict:
            creds_dict["private_key"] = limpiar_private_key(creds_dict["private_key"])
            
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(credentials)
        sh = gc.open_by_key(SPREADSHEET_ID)
        return sh, None
    except Exception as e:
        return None, str(e)

def obtener_datos(pestana_nombre):
    sh, err = conectar_sheet()
    if sh:
        try:
            ws = sh.worksheet(pestana_nombre)
            vals = ws.get_all_values()
            if len(vals) > 1:
                headers = [str(h).strip() for h in vals[0]]
                data = vals[1:]
                max_cols = len(headers)
                data_clean = [r + [""] * (max_cols - len(r)) for r in data]
                return pd.DataFrame(data_clean, columns=headers)
        except Exception:
            pass
            
    # Mandamientos por defecto si la conexión falla
    if pestana_nombre == "Mandamientos":
        return pd.DataFrame([
            {"Numero": 1, "Titulo": "Comunicación sincera siempre", "Descripcion": "Hablar de nuestras emociones con amor y transparencia."},
            {"Numero": 2, "Titulo": "Cuidar la distancia con detalles", "Descripcion": "Recordarnos todos los días lo mucho que nos importamos."},
            {"Numero": 3, "Titulo": "Apoyar los sueños del otro", "Descripcion": "Ser el refugio y el impulso mutuo en cada proyecto."},
            {"Numero": 4, "Titulo": "Celebrar cada 21", "Descripcion": "Hacer de nuestro cumple mes un día especial sin importar la rutina."},
            {"Numero": 5, "Titulo": "Confianza ciega", "Descripcion": "Construir la base de la relación en la lealtad y el respeto."},
            {"Numero": 6, "Titulo": "Tiempo de calidad a la distancia", "Descripcion": "Compartir citas virtuales, películas o llamadas sin distracciones."},
            {"Numero": 7, "Titulo": "Planificar nuestro reencuentro", "Descripcion": "Mantener viva la ilusión de los viajes y abrazos futuros."},
            {"Numero": 8, "Titulo": "Resolver los malentendidos con amor", "Descripcion": "Nunca irnos a dormir enojados el uno con el otro."},
            {"Numero": 9, "Titulo": "Espacio personal e individualidad", "Descripcion": "Acompañarnos sin perder el crecimiento propio."},
            {"Numero": 10, "Titulo": "Elegirnos todos los días", "Descripcion": "Recordar por qué iniciamos esta historia aquel 21 de abril."}
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
            return False, f"Error escribiendo en Hitos: {e}"
    return False, f"Sin conexión: {err}"

# -----------------------------------------------------------------------------
# 3. ENCABEZADO Y CONTADOR
# -----------------------------------------------------------------------------
st.markdown("<div class='title-header'>NOSOTROS, LO NUESTRO</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>CHILE 🇨🇱 ✈️ 🇵🇾 PARAGUAY</div>", unsafe_allow_html=True)

col_izq, col_der = st.columns([1, 1.5])

with col_izq:
    st.markdown(
        """
        <div class='initials-card'>
            <div class='initials-text'>M & F</div>
            <p style='color: #881337; font-weight: 600; font-size: 1.2rem; margin-top: 10px;'>Macarena & Federico</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_der:
    hoy = date.today()
    dias_juntos = (hoy - FECHA_INICIO).days
    meses_cumplidos = (hoy.year - FECHA_INICIO.year) * 12 + hoy.month - FECHA_INICIO.month

    dias_mostrar = max(0, dias_juntos)
    meses_mostrar = max(0, meses_cumplidos)

    st.markdown(
        f"""
        <div class='counter-box'>
            <div style='font-size: 1.1rem; text-transform: uppercase; letter-spacing: 2px;'>Días Construyendo Nuestra Historia</div>
            <div class='counter-number'>{dias_mostrar} DÍAS</div>
            <div style='font-size: 1rem;'>Desde el 21 de Abril de 2026 ({meses_mostrar} meses hermosos)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

if hoy.day == 21:
    st.balloons()
    st.success(f"🎉 ¡FELIZ CUMPLE MES MI AMOR! Hoy celebramos {meses_mostrar} meses de elegirnos. ❤️")

# -----------------------------------------------------------------------------
# 4. MENÚ DE NAVEGACIÓN
# -----------------------------------------------------------------------------
menu = st.radio(
    "Navegación:",
    ["📖 Nuestra Línea de Tiempo", "📜 Los 10 Mandamientos", "📲 Celebrar en WhatsApp"],
    horizontal=True
)

st.markdown("---")

# Comprobación de conexión en vivo
sh_test, err_test = conectar_sheet()
if not sh_test:
    st.warning(f"⚠️ **Atención:** La aplicación no está conectada a Google Sheets. Motivo: `{err_test}`")

# =============================================================================
# SECCIÓN 1: LÍNEA DE TIEMPO DE HITOS
# =============================================================================
if menu == "📖 Nuestra Línea de Tiempo":
    
    with st.expander("✨ Agregar un Nuevo Recuerdo a Nuestra Historia", expanded=False):
        with st.form("form_hito", clear_on_submit=True):
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                creador = st.radio("¿Quién registra?", ["👩 Maca", "👨 Fede"], horizontal=True)
            with c2:
                fecha_hito = st.date_input("Fecha del Recuerdo", value=hoy)
            with c3:
                categoria = st.selectbox("Categoría", ["Viaje ✈️", "Anécdota 🤭", "Proyecto 🚀", "Regalo 🎁", "Cita a Distancia 💻", "Especial ❤️"])

            titulo = st.text_input("Título *", placeholder="Ej: Nuestra primera llamada infinita...")
            descripcion = st.text_area("Descripción / Sentimientos *", placeholder="Escribe aquí los detalles que hicieron especial este momento...")

            submitted = st.form_submit_button("💖 Guardar en Nuestro Corazón")

            if submitted:
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
                        descripcion.strip()
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
        col_fecha = [c for c in df_hitos.columns if "fecha" in c.lower()]
        if col_fecha:
            df_hitos["Fecha_DT"] = pd.to_datetime(df_hitos[col_fecha[0]], errors='coerce')
            df_hitos = df_hitos.sort_values(by="Fecha_DT", ascending=False)

        for _, r in df_hitos.iterrows():
            creador_val = str(r.get("Creador", r.get("creador", ""))).strip().lower()
            es_maca = creador_val == "maca"
            css_class = "card-maca" if es_maca else "card-fede"
            tag_class = "tag-maca" if es_maca else "tag-fede"
            avatar = "👩 Maca" if es_maca else "👨 Fede"
            
            titulo_val = r.get("Titulo", r.get("titulo", ""))
            desc_val = r.get("Descripcion", r.get("descripcion", ""))
            cat_val = r.get("Categoria", r.get("categoria", ""))
            fecha_val = r.get("Fecha", r.get("fecha", ""))

            st.markdown(
                f"""
                <div class='{css_class}'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span class='{tag_class}'>{avatar}</span>
                        <span style='color: #64748b; font-size: 0.85rem; font-weight: 600;'>📅 {fecha_val} &nbsp;|&nbsp; {cat_val}</span>
                    </div>
                    <h3 style='color: #1e293b; margin-top: 15px; margin-bottom: 5px; font-family: "Playfair Display", serif;'>{titulo_val}</h3>
                    <p style='color: #475569; font-size: 1rem; line-height: 1.6;'>{desc_val}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("Aún no hay recuerdos registrados. ¡Abran el panel de arriba para registrar el primero!")

# =============================================================================
# SECCIÓN 2: LOS 10 MANDAMIENTOS DE M&F
# =============================================================================
elif menu == "📜 Los 10 Mandamientos":
    st.subheader("📜 Nuestras Promesas")
    st.caption("Las reglas inquebrantables que guían y protegen nuestra relación a la distancia.")

    df_mandamientos = obtener_datos("Mandamientos")

    if not df_mandamientos.empty:
        col_m1, col_m2 = st.columns(2)
        
        for idx, r in df_mandamientos.iterrows():
            target_col = col_m1 if idx % 2 == 0 else col_m2
            
            num_val = r.get("Numero", r.get("numero", r.get("Número", idx+1)))
            titulo_val = r.get("Titulo", r.get("titulo", ""))
            desc_val = r.get("Descripcion", r.get("descripcion", ""))
            
            with target_col:
                st.markdown(
                    f"""
                    <div class='mandamiento-card'>
                        <div style='color: #e11d48; font-weight: 800; font-size: 1.2rem; margin-bottom: 5px;'>Mandamiento #{num_val}</div>
                        <h4 style='margin-top: 0px; margin-bottom: 10px; color: #1e293b;'>{titulo_val}</h4>
                        <p style='color: #64748b; font-size: 0.95rem; line-height: 1.4; margin: 0;'>{desc_val}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# =============================================================================
# SECCIÓN 3: ENVIAR MENSAJE DE WHATSAPP
# =============================================================================
elif menu == "📲 Celebrar en WhatsApp":
    st.subheader("💬 Enviar Mensaje Romántico")
    st.write("Genera rápidamente un mensaje hermoso para celebrar los días y meses juntos.")

    destinatario = st.radio("¿A quién le vas a enviar el mensaje?", ["A Macarena 👩🇨🇱", "A Federico 👨🇵🇾"], horizontal=True)

    msj_default = f"¡Feliz Cumple Mes #{meses_mostrar} mi amor! ❤️\n\nHoy celebramos {dias_mostrar} días construyendo nuestra historia. Gracias por elegirme todos los días a pesar de la distancia.\n\nTe amo muchísimo, de Chile a Paraguay y de regreso. ✈️💖"

    mensaje_personalizado = st.text_area("Edita tu mensaje aquí:", value=msj_default, height=150)

    msj_encoded = urllib.parse.quote(mensaje_personalizado)
    url_wa = f"https://api.whatsapp.com/send?text={msj_encoded}"

    st.markdown(
        f"""
        <a href="{url_wa}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #25D366; color: white; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; font-size: 1.2rem; margin-top: 10px; box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3);">
                🟢 Abrir en WhatsApp y Enviar
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )
