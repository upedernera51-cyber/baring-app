import streamlit as st
import pandas as pd
import requests
import json
import time
import random

# 1. --- CONFIGURACIÓN Y ESTÉTICA ---

st.set_page_config(page_title="Baring App", page_icon="🍺", layout="centered")



# Importamos una fuente elegante para tu firma

st.markdown("""

    <style>
            /* Convierte las opciones del radio en boxes horizontales */
div[data-testid="stRadio"] > div {
    flex-direction: row !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
}

/* Estilo del box (el label del radio) */
div[data-testid="stRadio"] label {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    padding: 5px 10px !important;
    color: #CCC !important;
    font-size: 12px !important;
}

/* Estilo cuando está seleccionado */
div[data-testid="stRadio"] label[data-selected="true"] {
    border-color: #FFB300 !important;
    color: #FFB300 !important;
    background-color: rgba(255, 179, 0, 0.1) !important;
}

/* Oculta el círculo original del radio */
div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
    margin-left: -20px !important; /* Mueve el texto sobre el círculo */
}

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



    /* Optimización de botones para móvil */

    .stButton>button {

        background-color: #FFB300 !important;

        color: black !important;

        font-weight: bold !important;

        font-size: 22px !important;

        border-radius: 12px !important;

        height: 3em !important;

        width: 100% !important;

    }

   

    /* Estilo de tablas */

    .stTable { background: rgba(255,255,255,0.05); border-radius: 8px; }

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
            if df.shape[1] >= 4:
                df.columns = ["Invitado", "Producto", "Cant", "Subtotal"]
            return df
    except:
        pass
    return pd.DataFrame(columns=["Invitado", "Producto", "Cant", "Subtotal"])

data_actual = cargar_datos()

# 3. --- LÓGICA DE SORTEO ---
if "countdown" not in st.session_state:
    st.session_state.countdown = -1

# Pantalla de Cuenta Regresiva
if st.session_state.countdown >= 0:
    placeholder = st.empty()
    for i in range(st.session_state.countdown, -1, -1):
        with placeholder.container():
            st.markdown(f"<h1 style='font-size: 100px; text-align:center;'>{i if i > 0 else '🔥'}</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center; color:white;'>¡Mucha suerte a todos!</h3>", unsafe_allow_html=True)
            time.sleep(1)
    st.session_state.countdown = -2 
    st.rerun()

# Pantalla del Ganador
if st.session_state.countdown == -2:
    if not data_actual.empty:
        bolsa = data_actual["Invitado"].dropna().tolist()
        if bolsa:
            ganador = random.choice(bolsa)
            st.markdown(f"""
                <div style="border: 4px solid #FFB300; background: rgba(0,0,0,0.9); padding: 30px; border-radius: 20px; text-align: center;">
                    <h2 style='color: white;'>🏆 ¡EL GANADOR ES! 🏆</h2>
                    <div style="color: #FFB300; font-size: 50px; font-weight: bold;">{ganador}</div>
                </div>
            """, unsafe_allow_html=True)
            st.snow()
            if st.button("Volver a la App"):
                st.session_state.countdown = -1
                st.rerun()
    st.stop()

# --- CSS PARA FORZAR BOTONES PEQUEÑOS Y GRILLA ---
st.markdown("""
    <style>
    /* 1. Botones de Producto: Transparentes, bordes finos y pequeños */
    div[data-testid="stColumn"] button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #CCC !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        height: 35px !important;
        font-size: 10px !important;
        padding: 0px !important;
        margin-bottom: -15px !important;
        text-transform: uppercase;
    }

    /* 2. Cuando el botón está seleccionado (hover o activo) */
    div[data-testid="stColumn"] button:focus, div[data-testid="stColumn"] button:active {
        border-color: #FFB300 !important;
        color: #FFB300 !important;
        background-color: rgba(255, 179, 0, 0.1) !important;
    }

    /* 3. Botón de CONFIRMAR: Grande, Naranja y visible */
    .stButton > button[kind="primary"] {
        background-color: #FFB300 !important;
        color: black !important;
        font-size: 18px !important;
        height: 55px !important;
        border-radius: 10px !important;
        margin-top: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. --- FORMULARIO DE PEDIDO ---

# Definimos 'nombre' para que no de error

with st.form("form_pedido", clear_on_submit=True):

 nombre = st.text_input("👤 Tu nombre:", placeholder="¿Quién sos?")



st.write("### 📂 1. Seleccioná Categoría")

# Usamos el selectbox que querías

cat = st.selectbox("Categorías", [None] + list(CARTA.keys()), label_visibility="collapsed")



if cat:

    st.write(f"### 🍕 2. Seleccioná {cat}")

# Cambiá tu línea por esta:
prod = st.radio("Productos", list(CARTA[cat].keys()), label_visibility="collapsed", horizontal=True)
   

if prod:

        precio_actual = CARTA[cat][prod]

        st.markdown(f'<div class="price-tag">${precio_actual:,}</div>', unsafe_allow_html=True)

       

        cant = st.number_input("🔢 Cantidad:", 1, 10, 1)

       

        if st.form_submit_button("🚀 ¡ANOTAR PEDIDO!"):

            if nombre:

                # Aquí definimos el 'payload' (el paquete de datos)

                payload = {

                    "Invitado": nombre,

                    "Producto": prod,

                    "Cant": int(cant),

                    "Subtotal": int(precio_actual * cant)

                }

               

                with st.spinner("Enviando a la barra..."):

                    try:

                        # OJO: Es 'requests' (con S al final)

                        requests.post(URL_SCRIPT, data=json.dumps(payload), timeout=8)

                       

                        # Limpiamos el caché para que el Ranking se actualice al toque

                        st.cache_data.clear()

                       

                        st.success(f"✅ ¡Anotado para {nombre}!")

                        time.sleep(1)

                        st.rerun()

                    except:

                        st.error("Error de conexión. Reintentá en un momento.")

            else:

                st.warning("⚠️ Por favor, poné tu nombre arriba antes de pedir.")

# 5. --- DASHBOARD Y ADMIN ---
if not data_actual.empty:
    st.divider()
    df_fix = data_actual.copy()
    
    # Ranking
    st.subheader("🏆 Ranking de Tickets (Sorteo)")
    ranking = df_fix.groupby("Invitado").size().reset_index(name='Tickets 🎫')
    st.dataframe(ranking.sort_values(by='Tickets 🎫', ascending=False), hide_index=True, use_container_width=True)

    # Últimos pedidos
    st.subheader("📋 Últimos Pedidos")
    st.table(df_fix[["Invitado", "Producto", "Cant"]].iloc[::-1].head(5))

    # Total oculto
    with st.expander("💰 Ver mi total acumulado"):
        df_fix["Subtotal"] = pd.to_numeric(df_fix["Subtotal"], errors='coerce').fillna(0)
        resumen = df_fix.groupby("Invitado")["Subtotal"].sum().reset_index()
        resumen.columns = ["Invitado", "Total ($)"]
        resumen["Total ($)"] = resumen["Total ($)"].map("${:,.0f}".format)
        st.table(resumen)

# Panel Admin
st.divider()
col_k, col_b = st.columns([3, 1])
with col_k:
    admin_key = st.text_input("🔑 Admin", type="password", placeholder="Clave...", label_visibility="collapsed")

if admin_key.lower() == "ulises":
    if st.button("🔥 ¡INICIAR SORTEO! 🔥", use_container_width=True):
        st.session_state.countdown = 5
        st.rerun()
