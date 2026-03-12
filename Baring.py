import streamlit as st

import pandas as pd

import requests

import json

import time

import random



# 1. --- CONFIGURACIÓN Y ESTÉTICA ---

st.set_page_config(page_title="Baring App", page_icon="🍺", layout="centered")



st.markdown("""

    <style>

    @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');

    

    .stApp {

        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)),

                    url("https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=1000&auto=format&fit=crop") !important;

        background-size: cover !important;

        background-position: center !important;

        background-attachment: fixed !important;

    }



    h1 { color: #FFB300 !important; text-align: center; text-shadow: 2px 2px 4px #000; margin-bottom: 0px !important; }

    

    .signature {

        font-family: 'Great Vibes', cursive;

        font-size: 24px !important;

        color: #FFB300 !important;

        text-align: center;

        margin-top: -15px !important;

        margin-bottom: 25px !important;

        opacity: 0.9;

    }



    /* --- GRILLA DE PRODUCTOS --- */

    div[data-testid="stRadio"] > div {

        flex-direction: row !important;

        flex-wrap: wrap !important;

        gap: 10px !important;

    }



    div[data-testid="stRadio"] label div[data-testid="stWidgetSelectionMarker"] {

        display: none !important;

    }



    div[data-testid="stRadio"] label {

        background-color: rgba(255, 255, 255, 0.05) !important;

        border: 1px solid rgba(255, 255, 255, 0.2) !important;

        border-radius: 8px !important;

        padding: 10px 15px !important;

        color: white !important; /* LETRAS BLANCAS */

        font-size: 14px !important;

        cursor: pointer;

    }



    div[data-testid="stRadio"] label[data-selected="true"] {

        border-color: #FFB300 !important;

        background-color: rgba(255, 179, 0, 0.2) !important;

    }



    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {

        margin: 0px !important;

        color: white !important;

    }

    

    .stButton > button {

        background-color: #FFB300 !important;

        color: black !important;

        font-weight: bold !important;

        font-size: 22px !important;

        height: 3em !important;

        border-radius: 12px !important;

        width: 100% !important;

    }



    .price-tag {

        font-size: 42px !important;

        color: #FFB300 !important;

        font-weight: bold;

        text-align: center;

        padding: 10px;

        border: 2px solid #FFB300;

        border-radius: 15px;

        background: rgba(0,0,0,0.6);

        margin: 15px 0;

    }

    </style>

    """, unsafe_allow_html=True)



st.title("🍻 Baring App 🍻")

st.markdown('<p class="signature">by Ulises</p>', unsafe_allow_html=True)



# 2. --- DATOS Y CONEXIÓN ---

URL_SCRIPT = st.secrets["api_url"]



CARTA = {

    "Birras Artesanales 🍺": {

        "Golden": 5900, "Honey": 5900, "Calvu Scottish": 7500, "IPA": 6500,

        "Irish Red": 7000, "Caramel": 7000, "Frutos Rojos": 7000, "Amber Lager": 7000,

        "scottish": 7800, "Barley": 7800, "Lemon Kush": 8000, "Stout": 7800,

        "Session IPA": 7500, "APA": 7500, "EPA": 7500, "Artesanal Visionaire": 7500

    },

    "Coctelería & Tragos 🍸": {

        "Fernet Branca": 6500, "Gin Tonic Malandra": 7000, "Aperol Spritz": 7500,

        "Mojito / Mojito Malibú": 7500, "Jager Bomb / Jager Julep": 11500,

        "Negroni": 8800, "Old Fashioned": 11500, "Cynar Julep": 7000,

        "Gin Tonic Importado": 9000, "Coctelería Autor": 11500,

        "Vermouth / Gancia": 6000, "Caipirinha / Caipiroska": 7000

    },

    "Pizzas 🍕": {

        "Pizza Mozzarella": 16000, "Pizza Napolitana / Fugazza": 17000,

        "Pizza Calabresa / 4 Quesos": 18000, "Pizza Especial / Caprese": 18000,

        "Pizza Visio (Cheddar/Papas/Panceta)": 18900, "Pizza Stout (Carne Desmechada)": 19900,

        "Pizza Mozzarella Sin TACC": 19900, "Adicional Muzza Vegana": 3500

    },

    "Burgers & Lomos 🍔": {

        "Burger Clásica / Cheese (Doble)": 13500, 

        "Burger Antipasti / Cuarto / Caserita (Doble)": 13990,

        "Burger Walt Disney / Stout / Rockera": 15000,

        "Burger Dobby Quinoa (Veggie)": 13000,

        "Lomo Cordobés (M)": 15990, "Lomo Cordobés (XL)": 19990,

        "Lomo Visio (XL)": 20900, "Chegusan de Mila (XL)": 19990

    },

    "Para Picar 🍟": {

        "Papas Clásicas": 9500, "Papas Especiales": 9900,

        "Papas Stout (Carne desmechada)": 10500, "Bastones de Mozzarella": 9900,

        "Rabas Clásicas": 17500, "Crispy Chicken Fingers": 11900,

        "Tabla La Visio (Para 2)": 28990, "Tabla La Visio (Para 4)": 39990

    },

    "Sin Alcohol & Postres 🥤": {

        "Gaseosa / Agua / Saborizada": 3800, "Vaso Limonada": 3800,

        "Jarra Limonada": 13000, "Red Bull / Speed": 5000, "Postre": 6500

    }

}



@st.cache_data(ttl=5)

def cargar_datos():

    try:

        r = requests.get(f"{URL_SCRIPT}?nocache={time.time()}", timeout=5)

        json_data = r.json()

        if len(json_data) > 1:

            df = pd.DataFrame(json_data[1:], columns=json_data[0])

            df.columns = [c.strip().capitalize() for c in df.columns]

            # Convertimos Subtotal a numérico por si las dudas

            df["Subtotal"] = pd.to_numeric(df["Subtotal"], errors='coerce').fillna(0)

            return df

    except:

        pass

    return pd.DataFrame(columns=["Invitado", "Producto", "Cant", "Subtotal"])



# 3. --- LÓGICA DE SORTEO ---

if "countdown" not in st.session_state:

    st.session_state.countdown = -1



if st.session_state.countdown >= 0:

    placeholder = st.empty()

    for i in range(st.session_state.countdown, -1, -1):

        with placeholder.container():

            st.markdown(f"<h1 style='font-size: 100px; text-align:center;'>{i if i > 0 else '🔥'}</h1>", unsafe_allow_html=True)

            time.sleep(1)

    st.session_state.countdown = -2 

    st.rerun()



if st.session_state.countdown == -2:

    data_sorteo = cargar_datos()

    if not data_sorteo.empty:

        bolsa = data_sorteo["Invitado"].dropna().tolist()

        if bolsa:

            ganador = random.choice(bolsa)

            st.markdown(f'<div style="border:4px solid #FFB300; background:rgba(0,0,0,0.9); padding:30px; border-radius:20px; text-align:center;"><h2 style="color:white;">🏆 ¡EL GANADOR ES! 🏆</h2><div style="color:#FFB300; font-size:50px; font-weight:bold;">{ganador}</div></div>', unsafe_allow_html=True)

            st.snow()

            if st.button("Volver a la App"):

                st.session_state.countdown = -1

                st.rerun()

    st.stop()




st.divider()



# 5. --- FORMULARIO DE PEDIDO ---

nombre = st.text_input("👤 Tu nombre:", placeholder="¿Quién sos?")

cat = st.selectbox("📂 Seleccioná Categoría", [None] + list(CARTA.keys()))



if cat and cat in CARTA:

    st.write(f"### 🍕 ¿Qué vas a pedir de {cat}?")

    prod = st.radio("Productos", list(CARTA[cat].keys()), horizontal=True, label_visibility="collapsed")

    

    if prod:

        precio_actual = CARTA[cat][prod]

        st.markdown(f'<div class="price-tag">${precio_actual:,}</div>', unsafe_allow_html=True)

        cant = st.number_input("🔢 Cantidad:", 1, 10, 1)

        

        if st.button("🚀 ¡ANOTAR PEDIDO!"):

            if nombre:

                payload = {

                    "Invitado": nombre,

                    "Producto": prod,

                    "Cant": int(cant),

                    "Subtotal": int(precio_actual * cant)

                }

                with st.spinner("Enviando..."):

                    try:

                        requests.post(URL_SCRIPT, data=json.dumps(payload), timeout=8)

                        st.cache_data.clear()

                        st.success(f"✅ ¡Anotado para {nombre}!")

                        time.sleep(1)

                        st.rerun()

                    except:

                        st.error("Sumaste una chance!.")

            else:

                st.warning("⚠️ Escribí tu nombre primero.")

data_actual = cargar_datos()
# 6. --- DASHBOARD PÚBLICO ---

if not data_actual.empty:

    st.divider()

    if "Invitado" in data_actual.columns:

        st.subheader("🏆 Ranking de Tickets")

        ranking = data_actual.groupby("Invitado").size().reset_index(name='Tickets 🎫')

        st.dataframe(ranking.sort_values(by='Tickets 🎫', ascending=False), hide_index=True, use_container_width=True)

# --- CONSULTA INDIVIDUAL DE GASTO (VERSION CORREGIDA) ---
if not data_actual.empty:
    st.divider()
    with st.expander("🧐 Consultar cuánto lleva gastado cada uno"):
        # Aseguramos que la columna Invitado exista
        col_invitado = "Invitado" if "Invitado" in data_actual.columns else data_actual.columns[0]
        
        # Calculamos los totales
        gastos_totales = data_actual.groupby(col_invitado)["Subtotal"].sum().reset_index()
        
        opciones = ["Seleccioná un nombre..."] + gastos_totales[col_invitado].unique().tolist()
        seleccion = st.selectbox("Ver cuenta de:", opciones, label_visibility="collapsed")
        
        if seleccion != "Seleccioná un nombre...":
            total_persona = gastos_totales[gastos_totales[col_invitado] == seleccion]["Subtotal"].iloc[0]
            st.markdown(f"💰 **{seleccion}** lleva gastado un total de: **${total_persona:,}**")
            
            # FILTRADO SEGURO: Solo mostramos las columnas que REALMENTE existen en tu dataframe
            columnas_existentes = [c for c in ["Producto", "Cant", "Subtotal"] if c in data_actual.columns]
            detalle = data_actual[data_actual[col_invitado] == seleccion][columnas_existentes]
            
            st.dataframe(detalle, hide_index=True, use_container_width=True)
            
# Panel Admin

st.divider()

admin_key = st.text_input("🔑 Admin", type="password", placeholder="Clave...", label_visibility="collapsed")

if admin_key.lower() == "ulises":

    if st.button("🔥 ¡INICIAR SORTEO! 🔥"):

        st.session_state.countdown = 5

        st.rerun()



