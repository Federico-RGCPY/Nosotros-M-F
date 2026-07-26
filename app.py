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
# 2. CONEXIÓN DIRECTA A GOOGLE SHEETS
# -----------------------------------------------------------------------------
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def obtener_cliente_gspread():
    if "gcp_json" in st.secrets:
        json_raw = st.secrets["gcp_json"].strip("'\"")
        creds_dict = json.loads(json_raw, strict=False)
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(credentials)
    return None

def obtener_datos(pestana_nombre):
    gc = obtener_cliente_gspread()
    if gc:
        try:
            sh = gc.open("Nosotros_Lo_Nuestro")
            ws = sh.worksheet(pestana_nombre)
            
            rows = ws.get_all_values()
            
            if not rows or len(rows) <= 1:
                return pd.DataFrame()
            
            headers = [str(h).strip() for h in rows[0]]
            data = rows[1:]
            
            df = pd.DataFrame(data, columns=headers)
            df = df.dropna(how='all')
            
            if "Titulo" in df.columns:
                df = df[df["Titulo"].astype(str).str.strip() != ""]
                
            return df
        except Exception as e:
            st.error(f"Error leyendo {pestana_nombre}: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def guardar_hito(nuevo_hito):
    gc = obtener_cliente_gspread()
    if gc:
        try:
            sh = gc.open("Nosotros_Lo_Nuestro")
            ws = sh.worksheet("Hitos")
            ws.append_row(nuevo_hito)
            return True
        except Exception as e:
            st.error(f"Error guardando hito: {e}")
    return False

# -----------------------------------------------------------------------------
# 3. ENCABEZADO Y CONTADOR
# -----------------------------------------------------------------------------
st.markdown("<div class='title-header'>NOSOTROS, LO NUESTRO</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>CHILE 🇨🇱 ✈️ 🇵🇾 PARAGUAY</div>", unsafe_allow_html=True)

col_izq, col_der = st.columns([1, 1.5])

with col_izq:
    # Tarjeta M&F
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
    # Cálculo de Días Juntos y Meses
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

# Alerta de Cumplemes si hoy es día 21
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

            submitted = st.form_submit_button("💖 Guardar en Nuestro Corazón (y en la base de datos)")

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
                    if guardar_hito(nuevo_registro):
                        st.success("✨ ¡Recuerdo guardado para siempre!")
                        st.rerun()

    st.subheader("⏳ Nuestra Historia")

    df_hitos = obtener_datos("Hitos")

    if not df_hitos.empty:
        df_hitos["Fecha_DT"] = pd.to_datetime(df_hitos["Fecha"], errors='coerce')
        df_hitos = df_hitos.sort_values(by="Fecha_DT", ascending=False)

        for _, r in df_hitos.iterrows():
            es_maca = str(r.get("Creador", "")).strip().lower() == "maca"
            css_class = "card-maca" if es_maca else "card-fede"
            tag_class = "tag-maca" if es_maca else "tag-fede"
            avatar = "👩 Maca" if es_maca else "👨 Fede"
            
            if pd.notnull(r.get("Fecha_DT")):
                fecha_str = r["Fecha_DT"].strftime("%d/%m/%Y")
            else:
                fecha_str = str(r.get("Fecha", ""))

            st.markdown(
                f"""
                <div class='{css_class}'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span class='{tag_class}'>{avatar}</span>
                        <span style='color: #64748b; font-size: 0.85rem; font-weight: 600;'>📅 {fecha_str} &nbsp;|&nbsp; {r.get('Categoria', '')}</span>
                    </div>
                    <h3 style='color: #1e293b; margin-top: 15px; margin-bottom: 5px; font-family: "Playfair Display", serif;'>{r.get('Titulo', '')}</h3>
                    <p style='color: #475569; font-size: 1rem; line-height: 1.6;'>{r.get('Descripcion', '')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("Aún no hay recuerdos registrados. ¡Abran el panel de arriba y sean los primeros en agregar uno!")

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
            with target_col:
                st.markdown(
                    f"""
                    <div class='mandamiento-card'>
                        <div style='color: #e11d48; font-weight: 800; font-size: 1.2rem; margin-bottom: 5px;'>Mandamiento #{r.get('Numero', idx+1)}</div>
                        <h4 style='margin-top: 0px; margin-bottom: 10px; color: #1e293b;'>{r.get('Titulo', '')}</h4>
                        <p style='color: #64748b; font-size: 0.95rem; line-height: 1.4; margin: 0;'>{r.get('Descripcion', '')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No se pudieron cargar los mandamientos. Revisa la pestaña 'Mandamientos' en Google Sheets.")

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
