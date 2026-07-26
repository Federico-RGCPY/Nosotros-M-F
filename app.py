import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="RGC Dashboard VIP", layout="wide")

# URL de tu Google Sheet (Respaldo en vivo en la nube)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1L2kKpbx3u-bGehPZqce0Y7MVTKRK0fW9xEqkv5IZ2PQ/edit?usp=sharing"

# Diccionario para traducción de meses
MESES_ES = {
    "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
    "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
    "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

# Estilos Institucionales RGC
st.markdown("""
    <style>
    .header-mes { background-color: #800020; color: white; padding: 12px; border-radius: 8px; margin-top: 25px; font-weight: bold; text-transform: uppercase; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1 { color: #800020 !important; font-weight: 800; }
    .stButton>button { background-color: #800020; color: white; border-radius: 5px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN Y DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        df = conn.read(spreadsheet=URL_SHEET, ttl=0).dropna(how="all")
        df['Cierre Estimado'] = pd.to_datetime(df['Cierre Estimado'], errors='coerce')
        col_mov = 'Último Movimiento' if 'Último Movimiento' in df.columns else 'Últimiento Movimiento'
        df['Último Movimiento'] = pd.to_datetime(df[col_mov], errors='coerce')
        df['Monto Est.'] = pd.to_numeric(df['Monto Est.'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=['ID', 'Fecha Creación', 'Último Movimiento', 'Ejecutivo Comercial', 'Cliente', 'Tipo de Solución', 'Monto Est.', 'Status', 'Cierre Estimado'])

def guardar_datos(df_save):
    df_p = df_save.copy()
    df_p['Cierre Estimado'] = df_p['Cierre Estimado'].dt.strftime('%Y-%m-%d')
    df_p['Último Movimiento'] = df_p['Último Movimiento'].dt.strftime('%Y-%m-%d')
    conn.update(spreadsheet=URL_SHEET, data=df_p.astype(str))

# --- LÓGICA PRINCIPAL ---
df = cargar_datos()
opciones_status = ["Negociando", "Bajo", "Medio", "Ganado", "Perdido", "Postergado"]

st.title("📋 Pipeline Estratégico RGC")

# 3. SIDEBAR (FILTROS Y REGISTRO)
with st.sidebar:
    st.header("🔍 Filtros de Vista")
    lista_ejecutivos = ["Todos"] + sorted(df['Ejecutivo Comercial'].unique().tolist()) if not df.empty else ["Todos"]
    filtro_ejecutivo = st.selectbox("Filtrar por Ejecutivo", lista_ejecutivos)
    
    st.divider()
    st.header("📝 Registro de Oportunidad")
    with st.form("reg_form", clear_on_submit=True):
        v = st.text_input("Ejecutivo")
        c = st.text_input("Cliente")
        e = st.text_input("Equipo / Solución")
        m = st.number_input("Monto Estimado", min_value=0.0, step=1000.0)
        d = st.date_input("Fecha Estimada de Cierre")
        
        if st.form_submit_button("Registrar Oportunidad"):
            if v and c:
                nueva = pd.DataFrame([{
                    "ID": str(int(datetime.now().timestamp())), 
                    "Fecha Creación": date.today().strftime('%Y-%m-%d'), 
                    "Último Movimiento": pd.to_datetime(date.today()), 
                    "Ejecutivo Comercial": v, 
                    "Cliente": c, 
                    "Tipo de Solución": e, 
                    "Monto Est.": m, 
                    "Status": "Negociando", 
                    "Cierre Estimado": pd.to_datetime(d)
                }])
                df = pd.concat([df, nueva], ignore_index=True)
                guardar_datos(df)
                st.success("Guardado correctamente.")
                st.rerun()

    if not df.empty:
        st.divider()
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, engine='xlsxwriter')
        st.download_button(label="📥 Descargar Excel de Respaldo", data=towrite.getvalue(), file_name=f"Pipeline_RGC_{date.today()}.xlsx")

# Aplicar filtrado por Ejecutivo
if filtro_ejecutivo != "Todos":
    df_vistas = df[df['Ejecutivo Comercial'] == filtro_ejecutivo].copy()
else:
    df_vistas = df.copy()

# 4. KPIs
activos = df_vistas[df_vistas['Status'].isin(["Negociando", "Bajo", "Medio"])].copy()
monto_activo = activos['Monto Est.'].sum()

m1, m2, m3 = st.columns(3)
m1.metric("PIPELINE ACTIVO", f"{monto_activo:,.0f}".replace(",", "."))
m2.metric("OPORTUNIDADES", len(activos))
m3.metric("EQUIPOS", activos['Tipo de Solución'].nunique())

st.divider()
col_izq, col_der = st.columns([2, 1.3])

# 5. GESTIÓN DE CLIENTES (IZQUIERDA)
with col_izq:
    st.subheader("🚀 Seguimiento de Cartera")
    if not activos.empty:
        activos['Mes_ES'] = activos['Cierre Estimado'].dt.strftime('%B').map(MESES_ES) + " " + activos['Cierre Estimado'].dt.strftime('%Y')
        
        for mes in activos.sort_values('Cierre Estimado')['Mes_ES'].unique():
            st.markdown(f'<div class="header-mes">{mes}</div>', unsafe_allow_html=True)
            for i, row in activos[activos['Mes_ES'] == mes].iterrows():
                # Formateo de fecha DD/MM/AAAA y monto sin símbolos
                f_vis = row['Cierre Estimado'].strftime('%d/%m/%Y')
                monto_formateado = f"{row['Monto Est.']:,.0f}".replace(",", ".")
                
                with st.expander(f"📌 {row['Cliente']} | {row['Tipo de Solución']} ({monto_formateado} | Cierre: {f_vis})"):
                    with st.form(key=f"ed_{row['ID']}"):
                        ca, cb = st.columns(2)
                        nv = ca.text_input("Ejecutivo", value=row['Ejecutivo Comercial'])
                        nm = ca.number_input("Monto", value=float(row['Monto Est.']), step=1000.0)
                        nf = cb.date_input("Nueva Fecha Cierre", value=row['Cierre Estimado'].date())
                        ns = cb.selectbox("Estado", opciones_status, index=opciones_status.index(row['Status']))
                        
                        if st.form_submit_button("Aplicar Cambios"):
                            idx = df[df['ID'] == row['ID']].index[0]
                            df.at[idx, 'Ejecutivo Comercial'] = nv
                            df.at[idx, 'Monto Est.'] = nm
                            df.at[idx, 'Cierre Estimado'] = pd.to_datetime(nf)
                            df.at[idx, 'Status'] = ns
                            df.at[idx, 'Último Movimiento'] = pd.to_datetime(date.today())
                            guardar_datos(df)
                            st.rerun()
    else:
        st.info("No hay registros activos para mostrar.")

# 6. GRÁFICO DE DESEMPEÑO (DERECHA)
with col_der:
    st.subheader("📊 Desempeño Ejecutivo")
    if not activos.empty:
        df_g = activos.groupby('Ejecutivo Comercial')['Monto Est.'].sum().reset_index().sort_values('Monto Est.')
        
        fig = go.Figure(go.Bar(
            y=df_g['Ejecutivo Comercial'],
            x=df_g['Monto Est.'],
            orientation='h',
            text=df_g['Monto Est.'].apply(lambda x: f"{x:,.0f}".replace(",", ".")),
            textposition='outside',
            marker=dict(
                color=df_g['Monto Est.'],
                colorscale='YlOrRd', 
                line=dict(color='#333', width=2)
            )
        ))

        fig.update_layout(
            showlegend=False,
            height=450,
            xaxis_title="Monto Estimado",
            yaxis_title="",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=100, r=80),
            xaxis=dict(showgrid=True, gridcolor='lightgrey')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.markdown("**Resumen Numérico:**")
        for idx, r in df_g.sort_values(by='Monto Est.', ascending=False).iterrows():
            m_txt = f"{r['Monto Est.']:,.0f}".replace(",", ".")
            st.write(f"👤 {r['Ejecutivo Comercial']}: **{m_txt}**")
    else:
        st.write("Sin datos para graficar.")

# 7. HISTÓRICO
st.divider()
st.subheader("📂 Archivo Histórico")
hist = df_vistas[~df_vistas['Status'].isin(["Negociando", "Bajo", "Medio"])].copy()

if not hist.empty:
    for t in ["Postergado", "Ganado", "Perdido"]:
        fil = hist[hist['Status'] == t]
        if not fil.empty:
            with st.expander(f"Ver {t}s ({len(fil)})"):
                for i, r in fil.iterrows():
                    ra, rb = st.columns([3, 1])
                    f_hist_vis = r['Cierre Estimado'].strftime('%d/%m/%Y')
                    m_hist_txt = f"{r['Monto Est.']:,.0f}".replace(",", ".")
                    ra.write(f"**{r['Cliente']}** - {r['Tipo de Solución']} ({m_hist_txt} | Cierre: {f_hist_vis})")
                    
                    nh = rb.selectbox("Reactivar", opciones_status, index=opciones_status.index(r['Status']), key=f"h_{r['ID']}")
                    if nh != r['Status']:
                        df.loc[df['ID'] == r['ID'], 'Status'] = nh
                        df.loc[df['ID'] == r['ID'], 'Último Movimiento'] = pd.to_datetime(date.today())
                        guardar_datos(df)
                        st.rerun()
