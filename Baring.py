import streamlit as st
import pandas as pd

# 1. --- CARTA COMPLETA (Extraída de tus archivos) ---
CARTA = {
    "Cervezas 🍺": {
        "Pinta Artesanal Visionaire": 5500,
        "Pinta Artesanal Premium": 6800,
        "Heineken Monjita": 6500,
        "Heineken Balde x6": 35000,
        "Imperial Lata (Roja/IPA/APA/Lager)": 5500,
        "Golden (Visio/Calvu)": 5900,
        "Honey Visio": 5900,
        "IPA Visio": 6500,
        "Irish Red / Caramel / Frutos Rojos": 7000,
        "Amber Lager": 7000,
        "Session IPA / APA / EPA": 7500,
        "Scottish / Stout / Barley": 7800,
        "Lemon Kush": 8000
    },
    "Tragos 🍸": {
        "Fernet Branca": 6500,
        "Aperol Spritz": 7500,
        "Gin Tonic Malandra (Vaso)": 5500,
        "Gin Tonic Malandra (Copón)": 7000,
        "Gin Tonic Importado": 9000,
        "Mojito / Caipirinha / Caipiroska": 7500,
        "Jager Bomb / Julep": 11500,
        "Negroni": 8800,
        "Cynar Julep": 7000,
        "Gancia Batido": 6500,
        "Cuba Libre": 7000,
        "Coctelería de Autor (Cualquiera)": 11500,
        "Vinos (Promedio)": 18700
    },
    "Bebidas sin Alcohol 🥤": {
        "Gaseosa chica": 3800,
        "Agua sin/con gas": 3800,
        "Agua Saborizada": 3800,
        "Vaso de Limonada": 3800,
        "Jarra de Limonada": 13000,
        "Red Bull": 6000,
        "Speed": 4600
    },
"Comida 🍕": {
        # --- Hamburguesas (Precios Doble/Completa) ---
        "Burger Clásica (Doble)": 13000,
        "Burger La Cheese (Doble)": 13500,
        "Burger La Antipasti (Doble)": 13990,
        "Burger Cuarto de Visio (Doble)": 13990,
        "Burger Walt Disney": 15000,
        "Burger La Stout": 15000,
        "Burger La Kiki (Pollo)": 15000,
        "Burger La Rockera": 15000,
        "Burger La Visio": 15000,
        "Burger Dobby Quinoa (Vegetariana)": 13000,
        # --- Papas de todo tipo ---
        "Papas Clásicas": 9500,
        "Papas Bravas": 9900,
        "Papas Criollas": 9900,
        "Papas con Cheddar": 9900,
        "Papas Cuatro Quesos": 9900,
        "Papas Stout (Carne desmechada)": 10500,
        "Papas Visio (Panceta y Verdeo)": 9900,
        # --- Pizzas ---
        "Pizza Mozzarella": 16000,
        "Pizza Napolitana / Fugazza": 17000,
        "Pizza Especial (Jamón/Calabresa/Caprese)": 18000,
        "Pizza Visio (Cheddar/Panceta)": 18900,
        "Pizza Stout (Carne desmechada)": 19900,
        "Pizza Rúcula y Crudo": 19900
    }    }


# 2. --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Baring - La Terminal", page_icon="🍺")

# Estilo visual
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .stSelectbox label { font-weight: bold; color: #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍺 Baring @ La Terminal")
st.write("¡Feliz Cumple! Anotá acá lo que vas pidiendo para que al final la cuenta cierre perfecta.")

if 'consumos' not in st.session_state:
    st.session_state.consumos = []

# 3. --- FORMULARIO ---
with st.container(border=True):
    nombre = st.text_input("Tu nombre:", placeholder="Ej: Juan").strip()
    
    col1, col2 = st.columns(2)
    with col1:
        cat = st.selectbox("Categoría:", list(CARTA.keys()))
    with col2:
        prod = st.selectbox("Producto:", list(CARTA[cat].keys()))
    
    cant = st.number_input("Cantidad:", min_value=1, max_value=20, value=1)
    
    if st.button("Anotar a mi cuenta ➕"):
        if nombre:
            precio = CARTA[cat][prod]
            st.session_state.consumos.append({
                "Invitado": nombre,
                "Producto": prod,
                "Cant": cant,
                "Subtotal": precio * cant
            })
            st.toast(f"✅ {cant}x {prod} anotado para {nombre}")
        else:
            st.error("⚠️ Por favor, poné tu nombre.")

# 4. --- RESUMEN ---
if st.session_state.consumos:
    st.divider()
    df = pd.DataFrame(st.session_state.consumos)
    
    # Tabla resumen por persona
    resumen = df.groupby("Invitado")["Subtotal"].sum().reset_index()
    resumen.columns = ["Invitado", "Total a Pagar ($)"]
    
    st.write("### 💵 Resumen para pagar")
    st.table(resumen)
    
    # Detalle total
    with st.expander("Ver detalle de pedidos"):
        st.dataframe(df, use_container_width=True, hide_index=True)
        total_general = df["Subtotal"].sum()
        st.write(f"**Total acumulado en el bar: ${total_general:,}**")

    if st.button("❌ Limpiar todo (Solo cumpleañero)"):
        st.session_state.consumos = []
        st.rerun()


