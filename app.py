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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nosotros, Lo Nuestro — M&F",
    page_icon="❤️",
    layout="wide"
)

FECHA_INICIO = date(2026, 4, 21)  
SPREADSHEET_ID = "1o6dSXS4nSyC3M-20RaOQzpRsxEyVySnuu5KdzIZLyAo"

# Estilos CSS Románticos
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

    .card-maca {
        border-left: 6px solid #ec4899;
        background-color: #
