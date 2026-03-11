import streamlit as st
import pandas as pd
import requests
import json
import time

# 1. --- CONFIGURACIÓN Y ESTÉTICA DEFINITIVA ---
st.set_page_config(page_title="Baring App", page_icon="🍺", layout="centered")

st.markdown("""
    <style>
    /* FONDO Y TEXTOS */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=1000&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: scroll !important; 
    }
    .stMarkdown p, .stTextInput label, .stSelectbox label, .stNumberInput label, label p, .stAlert p {
        color: white !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px black !important;
    }
    h1, h2, h3, .stSubheader {
        color: #FFB300 !important;
        text-align: center !important;
        text-shadow: 2px 2px 4px #000000 !important;
    }

    /* ELIMINAR TECLADO EN SELECTBOX */
    /* Este bloque detecta el input dentro del selector y le quita el foco de escritura */
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        inputmode: none !important;
        pointer-events: none !important;
    }

    /* ESTILO DE CATEGORÍAS (RADIO) */
    .stRadio div[role="radiogroup"] {
        gap: 8px;
    }
    .stRadio div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 179, 0, 0.3);
        border-radius: 10px;
        padding: 8px 12px;
        width: 100%;
        color: white !important;
    }

    /* BOTÓN Y PRECIO */
    .price-tag {
        font-size: 35px !important;
        color: #FFB300 !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 10px !important;
        margin-bottom: 20px !important;
        border: 2px solid #FFB300 !important;
        border-radius: 15px !important;
        background: rgba(0,0,0,0.6) !important;
    }
    .stButton>button {
        background-color: #FFB300 !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 22px !important;
        border-radius: 15px !important;
        height: 3.5em !important;
        border: none !important;
    }
    
    /* TABLAS */
    .stTable { background-color: rgba(255, 255, 255, 0.1) !important; border-radius: 10px !important; }
    th { color: #FFB300 !important; background-color: rgba(0,0,0,0.5) !important; }
    td { color: white !important; background-color: rgba(0,0,0,0.3) !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍻 BARING NIGHT 🍻")

# 2. --- CARTA COMPLETA ---
URL_SCRIPT = st.secrets["api_url"]

CARTA = {
    "Cervezas 🍺": {
        "Pinta Artesanal Visionaire": 5500, "Pinta Artesanal Premium": 6800,
        "Irish Red (Visio)": 7000, "Caramel (Visio)": 7000, "Frutos Rojos (Calvu)": 7000,
        "Amber Lager (Fermentum)": 7000, "Session IPA (Fermentum)": 7500,
        "APA (Visio / Fermentum)": 7500, "EPA (Calvu)": 7500, "Scottish (Calvu)": 7800,
        "Stout (Walmunz)": 7800, "Barley (Walmunz)": 7800, "Lemon Kush (Calvu)": 8000,
        "Heineken Monjita": 6500, "Heineken Balde x6": 35000, "Imperial Lata": 5500
    },
    "Tragos 🍸": {
        "Fernet Branca": 6500, "Aperol Spritz": 7500, "Gin Tonic Malandra (Vaso)": 5500,
        "Gin Tonic Malandra (Copón)": 7000, "Gin Tonic Importado": 9000,
        "Boulevardier": 7200, "Old Fashioned": 11500, "Penicilin": 7800,
        "Tom Collins": 7600, "Cuba Libre": 7000, "Red Label": 8000,
        "Destornillador": 7000, "Jager Bomb / Julep": 11500, "Cynar Julep": 7000,
        "Vermouth": 6000, "Gancia Batido/Directo": 6500, "Caipirinha / Caipiroska": 7000,
        "Caipi Malibú": 9000, "Negroni": 8800, "Coctelería de Autor": 11500
    },
    "Bebidas sin Alcohol 🥤": {
        "Gaseosa chica": 3800, "Agua sin/con gas": 3800, "Agua Saborizada": 3800,
        "Vaso de Limonada": 3800, "Jarra de Limonada": 13000, "Red Bull": 6000, "Speed": 4600
    },
    "Comida 🍕🍔🍟": {
        "Pizza Mozzarella": 16000, "Pizza Napolitana / Fugazza": 17000,
        "Pizza Calabresa / 4 Quesos": 18000, "Pizza Especial / Caprese": 18000,
        "Pizza Visio (Cheddar/Panceta)": 18900, "Pizza Stout / Rúcula y Crudo": 19900,
        "Burger Clásica / Cheese (Doble)": 13500, "Burger Antipasti / Cuarto (Doble)": 13990,
        "Burger Walt Disney / Stout / Rockera": 15000, "Burger Dobby Quinoa (Veggie)": 13000,
        "Papas Clásicas": 9500, "Papas (Cheddar / Bravas / 4 Quesos)": 9900, "Papas Stout": 10500
    }
}

@st.cache_data(ttl=60)
def cargar_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=5)
        json_data = r.json()
        if len(json_data) > 1:
            return pd.DataFrame(json_data[1:], columns=json_data[0])
    except:
        pass
    return pd.DataFrame(columns=["Invitado", "Producto", "Cant", "Subtotal"])

data_actual = cargar_datos()

# 3. --- FORMULARIO (VERSIÓN ANTI-TECLADO TOTAL) ---
with st.container():
    nombre = st.text_input("👤 Tu nombre:", placeholder="¿Quién sos?")
    
    st.markdown("### 📂 Categoría")
    cat = st.pills("Seleccioná categoría:", list(CARTA.keys()), label_visibility="collapsed")
    
    if cat:
        st.markdown(f"### 🍕 Productos de {cat}")
        # Usamos pills para los productos también. 
        # Esto genera botones que se pueden tocar sin disparar el teclado.
        prod = st.pills("Seleccioná producto:", list(CARTA[cat].keys()), label_visibility="collapsed")
        
        if prod:
            precio_actual = CARTA[cat][prod]
            st.markdown(f'<div class="price-tag">${precio_actual:,}</div>', unsafe_allow_html=True)
            
            cant = st.number_input("🔢 Cantidad:", 1, 10, 1)
            
            if st.button("¡ANOTAR PEDIDO! 🚀"):
                if nombre:
                    payload = {"Invitado": nombre, "Producto": prod, "Cant": int(cant), "Subtotal": int(precio_actual * cant)}
                    with st.spinner("Enviando..."):
                        try:
                            requests.post(URL_SCRIPT, data=json.dumps(payload), timeout=5)
                            st.cache_data.clear()
                        except:
                            st.cache_data.clear()
                        st.success(f"✅ ¡Anotado, {nombre}!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.warning("⚠️ Poné tu nombre para la cuenta.")
    else:
        st.info("👆 Seleccioná una categoría para ver los productos.")

# 4. --- TABLAS ---
if not data_actual.empty:
    st.divider()
    df_fix = data_actual.copy()
    try:
        if df_fix.shape[1] >= 4:
            df_fix.columns = ["Invitado", "Producto", "Cant", "Subtotal"]
        st.subheader("💰 Resumen")
        df_fix["Subtotal"] = pd.to_numeric(df_fix["Subtotal"], errors='coerce').fillna(0)
        resumen = df_fix.groupby("Invitado")["Subtotal"].sum().reset_index()
        resumen.columns = ["Invitado", "Total ($)"]
        resumen["Total ($)"] = resumen["Total ($)"].map("${:,.0f}".format)
        st.table(resumen)

        st.subheader("📋 Últimos Pedidos")
        historial = df_fix[["Invitado", "Producto", "Cant"]].iloc[::-1].head(10)
        st.table(historial)
    except:
        st.table(data_actual.iloc[::-1].head(10))

















