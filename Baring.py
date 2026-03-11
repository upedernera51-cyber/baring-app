import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. --- CARTA FINAL ---
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

st.set_page_config(page_title="Baring App by Ulises", page_icon="🍺")

# Intentar conexión
conn = st.connection("gsheets", type=GSheetsConnection)

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .price-tag { font-size: 22px; color: #1e88e5; font-weight: bold; text-align: center; border: 2px solid #1e88e5; border-radius: 10px; padding: 10px; margin: 10px 0; background-color: #f0f7ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍺 Baring App by Ulises")

# Función segura para leer
def cargar_datos():
    try:
        return conn.read(worksheet="Hoja1", ttl=0)
    except:
        return pd.DataFrame(columns=["Invitado", "Producto", "Cant", "Subtotal"])

data_actual = cargar_datos()

# 3. --- FORMULARIO ---
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
            nueva_fila = pd.DataFrame([{
                "Invitado": nombre, "Producto": prod, "Cant": int(cant), "Subtotal": int(precio_actual * cant)
            }])
            
            # UNIÓN DE DATOS
            df_actualizado = pd.concat([data_actual, nueva_fila], ignore_index=True)
            
            # EL CAMBIO CLAVE: Intentar actualizar con manejo de error
            try:
                conn.update(worksheet="Hoja1", data=df_actualizado)
                st.success(f"✅ ¡Anotado en la cuenta de {nombre}!")
                st.rerun()
            except Exception as e:
                st.error("Error de permisos en Google Sheets. Revisá que esté en modo 'Editor' para todos.")
        else:
            st.error("⚠️ Por favor, poné tu nombre.")

# 4. --- RESUMEN ---
if not data_actual.empty:
    st.divider()
    resumen = data_actual.groupby("Invitado")["Subtotal"].sum().reset_index()
    resumen.columns = ["Invitado", "Total a Pagar ($)"]
    st.write("### 💵 Resumen de la cuenta")
    st.table(resumen)
    
    with st.expander("Ver detalle"):
        st.dataframe(data_actual, use_container_width=True, hide_index=True)


