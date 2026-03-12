import streamlit as st
import pandas as pd
import requests
import json
import time
import random

# 1. --- CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Baring App", page_icon="🍺", layout="centered")

# CSS para convertir Radios en Boxes y mejorar la interfaz
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

    /* --- GRILLA DE PRODUCTOS (Radio como Boxes) --- */
    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
    }

    div[data-testid="stRadio"] label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        color: #CCC !important;
        font-size: 13px !important;
        cursor: pointer;
    }

    div[data-testid="stRadio"] label[data-selected="true"] {
        border-color: #FFB300 !important;
        color: #FFB300 !important;
        background-color: rgba(255, 179, 0, 0.1) !important;
    }

    /* Ocultar el circulito del radio */
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
        margin-left: -15px !important;
    }
    
    /* Botón de envío (Naranja y Grande) */
    div.stForm div.stButton > button {
        background-color: #FFB300 !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 20px !important;
        height: 3em !important;
        border-radius: 12px !important;
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
            
            # ESTA LÍNEA MAGICA: Convierte todo a un formato estándar
            # No importa si dice 'INVITADO', 'invitado' o 'Invitado'
            df.columns = [c.strip().capitalize() for c in df.columns]
            
            # O mejor aún, forzalas por posición para que coincidan con tu código:
            # df.columns = ["Invitado", "Producto", "Cant", "Subtotal"]
            
            return df
    except:
        pass
    return pd.DataFrame(columns=["Invitado", "Producto", "Cant", "Subtotal"])
# 3. --- FORMULARIO DE PEDIDO ---
with st.form("form_pedido", clear_on_submit=True):
    nombre = st.text_input("👤 Tu nombre:", placeholder="¿Quién sos?")
    cat = st.selectbox("📂 Seleccioná Categoría", [None] + list(CARTA.keys()))
    
    prod = None
    if cat and cat in CARTA:
        st.write(f"### 🍕 Seleccioná {cat}")
        # Radio horizontal que parece botones
        prod = st.radio("Productos", list(CARTA[cat].keys()), horizontal=True, label_visibility="collapsed")
        
        precio_actual = CARTA[cat][prod]
        st.markdown(f'<div class="price-tag">${precio_actual:,}</div>', unsafe_allow_html=True)
        cant = st.number_input("🔢 Cantidad:", 1, 10, 1)
    
    # Botón de envío DENTRO del form
    enviar = st.form_submit_button("🚀 ¡ANOTAR PEDIDO!", use_container_width=True)

# Lógica de envío (Fuera del form para evitar errores de refresco)
if enviar:
    if nombre and prod:
        payload = {
            "Invitado": nombre,
            "Producto": prod,
            "Cant": int(cant),
            "Subtotal": int(CARTA[cat][prod] * cant)
        }
        with st.spinner("Enviando a la barra..."):
            try:
                requests.post(URL_SCRIPT, data=json.dumps(payload), timeout=8)
                st.cache_data.clear()
                st.success(f"✅ ¡Anotado para {nombre}!")
                time.sleep(1)
                st.rerun()
            except:
                st.error("Error de conexión.")
    else:
        st.warning("⚠️ Falta nombre o producto.")

# 4. --- DASHBOARD Y ADMIN ---
# 4. --- DASHBOARD Y ADMIN ---
data_actual = cargar_datos()

if not data_actual.empty:
    st.divider()
    
    # Verificamos que la columna 'Invitado' realmente exista antes de agrupar
    if "Invitado" in data_actual.columns:
        st.subheader("🏆 Ranking de Tickets (Sorteo)")
        
        # Agrupamos y contamos
        ranking = data_actual.groupby("Invitado").size().reset_index(name='Tickets 🎫')
        
        # Ordenamos de mayor a menor
        ranking = ranking.sort_values(by='Tickets 🎫', ascending=False)
        
        st.dataframe(ranking, hide_index=True, use_container_width=True)
    else:
        # Si la columna tiene otro nombre, esto te va a ayudar a saber cuál es
        st.warning(f"⚠️ No se encontró la columna 'Invitado'. Columnas detectadas: {list(data_actual.columns)}")

    # Sección de últimos pedidos (solo si existen las columnas)
    if all(col in data_actual.columns for col in ["Invitado", "Producto", "Cant"]):
        st.subheader("📋 Últimos Pedidos")
        st.table(data_actual[["Invitado", "Producto", "Cant"]].iloc[::-1].head(5))
# Panel Admin al final
st.divider()
admin_key = st.text_input("🔑 Admin", type="password", placeholder="Clave...", label_visibility="collapsed")
if admin_key.lower() == "ulises":
    if st.button("🔥 ¡INICIAR SORTEO! 🔥", use_container_width=True):
        st.session_state.countdown = 5
        st.rerun()
