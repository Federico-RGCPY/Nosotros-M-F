# -----------------------------------------------------------------------------
# 2. CONEXIÓN A GOOGLE SHEETS
# -----------------------------------------------------------------------------
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def conectar_sheet():
    if "gcp_json" in st.secrets:
        try:
            json_raw = st.secrets["gcp_json"].strip("'\"")
            creds_dict = json.loads(json_raw, strict=False)
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            gc = gspread.authorize(credentials)
            return gc.open_by_key(SPREADSHEET_ID)
        except Exception as e:
            st.error(f"⚠️ Error al conectar con Google Sheets: Verifique que la cuenta de servicio tenga acceso al archivo. ({e})")
            return None
    return None

def obtener_datos(pestana_nombre):
    sh = conectar_sheet()
    if sh:
        try:
            ws = sh.worksheet(pestana_nombre)
            vals = ws.get_all_values()
            if not vals or len(vals) <= 1:
                return pd.DataFrame()
            
            headers = [str(h).strip() for h in vals[0]]
            data = vals[1:]
            
            max_cols = len(headers)
            data_clean = [r + [""] * (max_cols - len(r)) for r in data]
            
            df = pd.DataFrame(data_clean, columns=headers)
            df = df.dropna(how="all")
            return df
        except Exception as e:
            st.warning(f"No se pudieron leer los datos de '{pestana_nombre}': {e}")
            return pd.DataFrame()
    return pd.DataFrame()
