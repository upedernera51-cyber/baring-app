import streamlit as st
import pandas as pd
import requests
import json
import time

# 1. --- CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="Baring App", page_icon="🍺", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url("https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=1000&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: scroll !important; 
    }
    .stMarkdown p, label p {
        color: white !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    h1, h2, h3 {
        color: #FFB300 !important;
        text-align: center !important;
        text-shadow: 2px 2px 4px #000000 !important;
    }
    /* Estilo para los botones de selección (Pills) */
    div[data-testid="stWidgetLabel"] p { color: #FFB300 !important; font-size: 20px !important; }
    
    .price-tag {
        font-size: 38px !important;
        color: #FFB300 !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 15px !important;
        margin: 20px 0 !important;
        border: 3px solid #FFB300 !important;
        border-radius: 20px !important;
        background: rgba(0,0,0,0.7) !important;
    }
    .stButton>button {
        background-color: #FFB300 !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 24px !important;
        border-radius: 15px !important;
        height: 3.5em !important;
        width: 100% !important;
    }
    .stTable { background-color: rgba(255, 255, 255, 0.1) !important; border-radius: 10px !important; }
    th { color: #FFB300 !important; }
    td { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍻 LA TERMINAL RUIN BAR 🍻")

# 2. --- CARTA ACTUALIZADA (CON NUEVAS BIRRAS) ---
URL_SCRIPT = st.secrets["api_url"]

CARTA = {
    "Cervezas Artesanales 🍺": {
        "Pinta Visionaire (Irish/Caramel/APA)": 7000,
        "Pinta Calvu (F. Rojos/EPA/Scottish/L. Kush)": 7500,
        "Pinta Fermentum (Amber/Session IPA/APA)": 7500,
        "Pinta Walmunz (Stout/Barley)": 7800,
        "Pinta Visionaire Común": 5500,
        "Pinta Premium": 6800,
        "Heineken Monjita": 6500,
        "Heineken Balde x6": 35000,
        "Imperial Lata": 5500
    },
    "Tragos & Coctelería 🍸": {
        "Fernet Branca": 6500, "Mojito": 7500, "Gin Tonic Malandra": 7000,
        "Gin Tonic Importado": 9000, "Aperol Spritz": 7500, "Jager Bomb": 11500,
        "Negroni": 8800, "Coctelería de Autor (Varios)": 11500, "Cynar Julep": 7000
    },
    "Comida & Papas 🍕🍟": {
        "Papas Clásicas": 9500, "Papas Especiales (Cheddar/Visio/etc)": 9900,
        "Papas Stout (Carne desmechada)": 10500, "Pizza Mozzarella": 16000,
        "Pizza Especial / Calabresa": 18000, "Pizza Stout / Rúcula y Crudo": 19900,
        "Burger Clásica (Doble)": 13000, "Burger Walt Disney / Stout": 15000,
        "Lomo Cordobés (XL)": 19990
    },
    "Bebidas & Otros 🥤": {
        "Gaseosa / Agua / Saborizada": 3800, "Vaso Limonada": 3800,
        "Jarra Limonada": 13000, "Red Bull": 6000, "Speed": 4600, "Postre": 6500
    }
}

@st.cache_data(ttl=60)
def cargar_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=5)
        json_data = r.json()
        if len(json_data) > 1:
            return pd.DataFrame(json_data[1:], columns=json_data[0])
    except: pass
    return pd.DataFrame(columns=["Invitado", "Producto", "Cant", "Subtotal"])

data_actual = cargar_datos()

# 3. --- FORMULARIO (MODO PILLS - NO TECLADO) ---
nombre = st.text_input("👤 Tu nombre:", placeholder="Escribí aquí...")

st.write("### 📂 1. Elegí Categoría")
cat = st.pills("Categorías", list(CARTA.keys()), label_visibility="collapsed")

if cat:
    st.write(f"### 🍕 2. Elegí {cat}")
    prod = st.pills("Productos", list(CARTA[cat].keys()), label_visibility="collapsed")
    
    if prod:
        precio_actual = CARTA[cat][prod]
        st.markdown(f'<div class="price-tag">${precio_actual:,}</div>', unsafe_allow_html=True)
        
        cant = st.number_input("🔢 Cantidad:", 1, 10, 1)
        
        if st.button("🚀 ¡ANOTAR PEDIDO!"):
            if nombre:
                payload = {"Invitado": nombre, "Producto": prod, "Cant": int(cant), "Subtotal": int(precio_actual * cant)}
                with st.spinner("Enviando..."):
                    try:
                        requests.post(URL_SCRIPT, data=json.dumps(payload), timeout=5)
                        st.cache_data.clear()
                        st.success(f"✅ ¡Anotado para {nombre}!")
                        time.sleep(1)
                        st.rerun()
                    except: st.error("Error de conexión.")
            else:
                st.warning("⚠️ Falta el nombre.")

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
    except: st.table(data_actual.iloc[::-1].head(5))


















