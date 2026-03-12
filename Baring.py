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


# 2. --- DATOS ---
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
        "Gin Tonic Importado": 9000, "Coctelería Autor (Dobby/Hedwig/etc)": 11500,
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
        "Papas Clásicas": 9500, "Papas Especiales (Cheddar/Bravas/Visio)": 9900,
        "Papas Stout (Carne desmechada)": 10500, "Bastones de Mozzarella": 9900,
        "Rabas Clásicas": 17500, "Crispy Chicken Fingers": 11900,
        "Tabla La Visio (Para 2)": 28990, "Tabla La Visio (Para 4)": 39990
    },
    "Vinos & Espumantes 🍷": {
        "Lobo Piel de Cordero": 13500, "Eugenio Bustos Dulce": 15000,
        "Dieter Meier Puro": 18700, "Luigi Bosca": 23100,
        "Chandon Extra Brut": 28000, "Botella Chandon + 3 Speed": 37000
    },
    "Sin Alcohol & Postres 🥤": {
        "Gaseosa / Agua / Saborizada": 3800, "Vaso Limonada": 3800,
        "Jarra Limonada": 13000, "Red Bull / Speed": 5000, "Postre": 6500
    }
}

@st.cache_data(ttl=30) # Reducido a 30s para que la lista sea más dinámica
def cargar_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=5)
        json_data = r.json()
        if len(json_data) > 1:
            return pd.DataFrame(json_data[1:], columns=json_data[0])
    except: pass
    return pd.DataFrame(columns=["Invitado", "Producto", "Cant", "Subtotal"])

data_actual = cargar_datos()
  # --- LÓGICA DE SORTEO (ESTADO ANIMACIÓN) ---
if "countdown" not in st.session_state:
    st.session_state.countdown = -1

# Si el sorteo está corriendo, mostramos la cuenta regresiva
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
        # Cada fila es un ticket: el que más pidió tiene más chances
        bolsa = data_actual["Invitado"].tolist()
        ganador = random.choice(bolsa)
        
        st.markdown(f"""
            <div style="border: 4px solid #FFB300; background: rgba(0,0,0,0.9); padding: 30px; border-radius: 20px; text-align: center;">
                <h2 style='color: white;'>🏆 ¡EL GANADOR ES! 🏆</h2>
                <div style="color: #FFB300; font-size: 50px; font-weight: bold;">{ganador}</div>
                <p style='color: white; font-size: 20px;'>¡Vení a la barra por tu premio!</p>
            </div>
        """, unsafe_allow_html=True)
        st.snow()
        if st.button("Volver a la App"):
            st.session_state.countdown = -1
            st.rerun()
    st.stop() # Detiene el resto de la app para que solo se vea el ganador  

# 3. --- LÓGICA DE PEDIDO ---
nombre = st.text_input("👤 Tu nombre:", placeholder="Escribí aquí...")

st.write("### 📂 1. Categoría")
cat = st.selectbox("📂 1. Seleccioná Categoría", [None] + list(CARTA.keys()))

if cat:
    st.write(f"### 🍕 2. {cat}")
    prod = st.pills("Prod", list(CARTA[cat].keys()), label_visibility="collapsed")
    
    if prod:
        precio = CARTA[cat][prod]
        st.markdown(f'<div class="price-tag">${precio:,}</div>', unsafe_allow_html=True)
        cant = st.number_input("🔢 Cantidad:", 1, 10, 1)
        
        # Optimizamos el botón para evitar doble envío
        if st.button("🚀 ¡ANOTAR PEDIDO!", use_container_width=True):
            if not nombre:
                st.warning("⚠️ Ey! Poné tu nombre arriba.")
            else:
                with st.spinner("Anotando..."):
                    payload = {"Invitado": nombre, "Producto": prod, "Cant": int(cant), "Subtotal": int(precio * cant)}
                    try:
                        requests.post(URL_SCRIPT, data=json.dumps(payload), timeout=8)
                        st.balloons() # Efecto visual de éxito
                        st.success(f"¡Listo {nombre}! Ya te lo anoté.")
                        st.cache_data.clear()
                        time.sleep(1.5)
                        st.rerun()
                    except:
                        st.error("Sumaste una chance!")



# 4. --- RESUMEN, RANKING Y MOVIMIENTOS ---

if not data_actual.empty:
    st.divider()
    df_fix = data_actual.copy()
    
    try:
        # Aseguramos nombres de columnas
        if df_fix.shape[1] >= 4:
            df_fix.columns = ["Invitado", "Producto", "Cant", "Subtotal"]
        
        # 1. RANKING DE CHANCES (Arriba de todo)
        st.subheader("🏆 Ranking de Tickets para el Sorteo")
        st.markdown("_¡Cada pedido es una chance más de ganar!_")
        
        ranking = df_fix.groupby("Invitado").size().reset_index(name='Tickets 🎫')
        ranking = ranking.sort_values(by='Tickets 🎫', ascending=False)
        st.dataframe(ranking, hide_index=True, use_container_width=True)

        # 2. ÚLTIMOS MOVIMIENTOS (En el medio)
        st.subheader("📋 Últimos Pedidos en la Barra")
        historial = df_fix[["Invitado", "Producto", "Cant"]].iloc[::-1].head(5)
        st.table(historial)

        # 3. TOTAL ACUMULADO (Abajo de todo y discreto)
        with st.expander("💰 Ver mi total acumulado"):
            df_fix["Subtotal"] = pd.to_numeric(df_fix["Subtotal"], errors='coerce').fillna(0)
            resumen = df_fix.groupby("Invitado")["Subtotal"].sum().reset_index()
            resumen.columns = ["Invitado", "Total ($)"]
            resumen["Total ($)"] = resumen["Total ($)"].map("${:,.0f}".format)
            st.table(resumen)
        
    except Exception as e:
        st.info("Actualizando datos...")

# --- PANEL DE ADMIN DISCRETO (Al final de todo) ---
st.divider()

# Usamos columnas para que el botón de OK esté al lado del texto
col_key, col_btn = st.columns([3, 1])

with col_key:
    admin_key = st.text_input("🔑 Acceso Admin", type="password", placeholder="Clave...", label_visibility="collapsed")

# Si escribiste la clave, habilitamos el botón de sorteo
if admin_key.lower() == "ulises":
    st.success("✅ Modo Admin Activo")
    if st.button("🔥 ¡INICIAR SORTEO AHORA! 🔥", use_container_width=True):
        st.session_state.countdown = 10
        st.rerun()
else:
    if admin_key: # Si escribió algo pero no es la clave
        st.error("Clave incorrecta")


















