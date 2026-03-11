import streamlit as st
import pandas as pd
import requests
import json
import time

# 1. --- CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Baring App", page_icon="🍺", layout="centered")

# URL de imagen de fondo/encabezado (Podés cambiar este link por el de tu logo o foto)
IMG_URL = "https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=1000&auto=format&fit=crop"

st.markdown(f"""
    <style>
    /* Fondo general */
    .stApp {{
        background-color: #121212;
        color: #FFFFFF;
    }}
    /* Títulos y Subtítulos */
    h1, h2, h3 {{
        color: #FFB300 !important;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
    }}
    /* El contenedor del formulario */
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    .st-expander, .stContainer {{
        border: 1px solid #FFB300 !important;
        background-color: #1E1E1E !important;
        border-radius: 15px;
    }}
    /* Botón estilo "Pinta" */
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #FFB300 !important; /* Ámbar Cerveza */
        color: #000000 !important;
        font-weight: bold;
        font-size: 20px;
        border: none;
        box-shadow: 0px 4px 15px rgba(255, 179, 0, 0.3);
    }}
    .stButton>button:hover {{
        background-color: #FFA000 !important;
        transform: scale(1.02);
    }}
    /* Etiqueta de precio */
    .price-tag {{
        font-size: 28px;
        color: #FFB300;
        font-weight: bold;
        text-align: center;
        margin: 15px 0;
        text-shadow: 2px 2px 4px #000000;
    }}
    /* Tablas estilo pizarra */
    .stTable {{
        background-color: #1E1E1E;
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Banner de bienvenida
st.image(IMG_URL, use_container_width=True)
st.title("🍻 BARING NIGHT 🍻")

# 2. --- DATOS Y CARTA ---
URL_SCRIPT = st.secrets["api_url"]

CARTA = {
    "Cervezas 🍺": {
        "Pinta Visionaire": 5500, "Pinta Premium": 6800, "Irish Red": 7000, "Caramel": 7000, 
        "Frutos Rojos": 7000, "Amber Lager": 7000, "Session IPA": 7500, "APA": 7500, 
        "EPA": 7500, "Scottish": 7800, "Stout": 7800, "Barley": 7800, "Lemon Kush": 8000,
        "Heineken Monjita": 6500, "Heineken Balde x6": 35000, "Imperial Lata": 5500
    },
    "Tragos 🍸": {
        "Fernet Branca": 6500, "Aperol Spritz": 7500, "Gin Tonic Malandra": 7000, 
        "Gin Importado": 9000, "Old Fashioned": 11500, "Negroni": 8800, "Jager Bomb": 11500
    },
    "Bebidas Sin Alcohol 🥤": {
        "Gaseosa / Agua": 3800, "Limonada Vaso": 3800, "Limonada Jarra": 13000, "Red Bull": 6000
    },
    "Comida 🍕🍔🍟": {
        "Pizza Muzzarella": 16000, "Pizza Especial": 18000, "Burger Clásica": 13500, 
        "Burger Walt Disney": 15000, "Papas Cheddar": 9900, "Papas Stout": 10500
    }
}

@st.cache_data(ttl=120)
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

# 3. --- FORMULARIO ---
with st.container():
    nombre = st.text_input("📝 ¿Quién pide?", placeholder="Tu nombre...").strip()
    cat = st.selectbox("Categoría:", list(CARTA.keys()))
    prod = st.selectbox("Producto:", list(CARTA[cat].keys()))
    
    precio_actual = CARTA[cat][prod]
    st.markdown(f'<div class="price-tag">${precio_actual:,}</div>', unsafe_allow_html=True)
    
    cant = st.number_input("Cantidad:", 1, 10, 1)
    
    if st.button("¡PEDIR AHORA! 🚀"):
        if nombre:
            payload = {"Invitado": nombre, "Producto": prod, "Cant": int(cant), "Subtotal": int(precio_actual * cant)}
            with st.spinner("Anotando..."):
                try:
                    requests.post(URL_SCRIPT, data=json.dumps(payload), timeout=5)
                    st.cache_data.clear()
                except:
                    st.cache_data.clear()
                st.success(f"✅ ¡Excelente, {nombre}!")
                time.sleep(1)
                st.rerun()
        else:
            st.warning("⚠️ Necesito tu nombre para la cuenta.")

# 4. --- RESUMEN ---
if not data_actual.empty:
    st.divider()
    df_fix = data_actual.copy()
    if df_fix.shape[1] >= 4:
        df_fix.columns = ["Invitado", "Producto", "Cant", "Subtotal"]

    st.subheader("💰 Resumen de Cuentas")
    df_fix["Subtotal"] = pd.to_numeric(df_fix["Subtotal"], errors='coerce').fillna(0)
    resumen = df_fix.groupby("Invitado")["Subtotal"].sum().reset_index()
    resumen.columns = ["Invitado", "Total ($)"]
    resumen["Total ($)"] = resumen["Total ($)"].map("${:,.0f}".format)
    st.table(resumen)

    st.subheader("📋 Últimos Pedidos")
    historial = df_fix[["Invitado", "Producto", "Cant"]].iloc[::-1].head(10)
    st.table(historial)








