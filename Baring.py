import streamlit as st
import pandas as pd
import requests
import json
import time

# 1. --- CARTA ACTUALIZADA ---
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

# 2. --- CONFIGURACIÓN ---
st.set_page_config(page_title="Baring App by Ulises", page_icon="🍺")
URL_SCRIPT = st.secrets["api_url"]

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .price-tag { font-size: 22px; color: #1e88e5; font-weight: bold; text-align: center; border: 2px solid #1e88e5; border-radius: 10px; padding: 10px; margin: 10px 0; background-color: #f0f7ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍺 Baring App by Ulises")

# 3. --- CARGA DE DATOS CON CACHÉ ---
@st.cache_data(ttl=120)  # Mantiene los datos en memoria por 2 minutos para máxima velocidad
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

# 4. --- FORMULARIO ---
with st.container(border=True):
    nombre = st.text_input("Tu nombre:", placeholder="Ej: Juan").strip()
    col1, col2 = st.columns(2)
    with col1:
        cat = st.selectbox("Categoría:", list(CARTA.keys()))
    with col2:
        prod = st.selectbox("Producto:", list(CARTA[cat].keys()))
    
    precio_actual = CARTA[cat][prod]
    st.markdown(f'<div class="price-tag">Precio: ${precio_actual:,}</div>', unsafe_allow_html=True)
    
    cant = st.number_input("Cantidad:", min_value=1, max_value=20, value=1)
    
    if st.button("Anotar a mi cuenta ➕"):
        if nombre:
            payload = {
                "Invitado": nombre,
                "Producto": prod,
                "Cant": int(cant),
                "Subtotal": int(precio_actual * cant)
            }
            with st.spinner("Anotando..."):
                try:
                    # Enviamos los datos a Google
                    requests.post(URL_SCRIPT, data=json.dumps(payload), timeout=5)
                    # LIMPIAMOS EL CACHÉ: Esto obliga a la app a leer el Sheet nuevo ahora mismo
                    st.cache_data.clear()
                except:
                    # Si falla la respuesta, igual limpiamos caché por si el dato entró
                    st.cache_data.clear()
                
                st.success(f"¡Listo {nombre}, anotado!")
                time.sleep(1.2)
                st.rerun()
        else:
            st.error("⚠️ Por favor, poné tu nombre.")

# 5. --- RESUMEN DE CUENTAS ---
if not data_actual.empty and "Subtotal" in data_actual.columns:
    st.divider()
    # Aseguramos que Subtotal sea número para sumar correctamente
    data_actual["Subtotal"] = pd.to_numeric(data_actual["Subtotal"], errors='coerce').fillna(0)
    
    resumen = data_actual.groupby("Invitado")["Subtotal"].sum().reset_index()
    resumen.columns = ["Invitado", "Total ($)"]
    
    # Formateamos los números para que se vean lindos con el signo $
    resumen_visual = resumen.copy()
    resumen_visual["Total ($)"] = resumen_visual["Total ($)"].map("${:,.0f}".format)
    
    st.write("### 💵 Totales por persona")
    st.table(resumen_visual)
    
    with st.expander("Ver detalle de todos los consumos"):
        st.dataframe(data_actual, use_container_width=True, hide_index=True)






