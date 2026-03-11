import streamlit as st
import pandas as pd

# 1. --- CARTA COMPLETA (Sincronizada con tus fotos y PDF) ---
CARTA = {
    "Cervezas 🍺": {
        "Pinta Artesanal Visionaire": 5500,
        "Pinta Artesanal Premium": 6800,
        "Heineken Monjita": 6500,
        "Heineken Balde x6": 35000,
        "Imperial Lata": 5500,
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
        "Coctelería de Autor": 11500
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
    "Comida 🍕🍔🍟": {
        "Burger Clásica / Cheese (Doble)": 13500,
        "Burger Antipasti / Cuarto (Doble)": 13990,
        "Burger Walt Disney / Stout / Rockera": 15000,
        "Burger Dobby Quinoa (Veggie)": 13000,
        "Papas Clásicas": 9500,
        "Papas (Cheddar / Bravas / 4 Quesos)": 9900,
        "Papas Stout (Carne desmechada)": 10500,
        "Pizza Mozzarella": 16000,
        "Pizza Napolitana / Fugazza": 17000,
        "Pizza Especial / Caprese": 18000,
        "Pizza Visio (Cheddar/Panceta)": 18900,
        "Pizza Stout / Rúcula y Crudo": 19900
    }
}

# 2. --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Baring - La Terminal", page_icon="🍺")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .price-tag { font-size: 24px; color: #1e88e5; font-weight: bold; text-align: center; border: 2px solid #1e88e5; border-radius: 10px; padding: 10px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍺 Baring @ La Terminal")
st.write("¡Feliz Cumple! Anotá tus pedidos para que la cuenta cierre perfecta.")

if 'consumos' not in st.session_state:
    st.session_state.consumos = []

# 3. --- FORMULARIO CON VISOR DE PRECIO ---
with st.container(border=True):
    nombre = st.text_input("Tu nombre:", placeholder="Ej: Juan").strip()
    
    col1, col2 = st.columns(2)
    with col1:
        cat = st.selectbox("Categoría:", list(CARTA.keys()))
    with col2:
        prod = st.selectbox("Producto:", list(CARTA[cat].keys()))
    
    # --- LA MAGIA: EL VISOR DE PRECIO ---
    precio_actual = CARTA[cat][prod]
    st.markdown(f'<div class="price-tag">Precio Unitario: ${precio_actual:,}</div>', unsafe_allow_html=True)
    
    cant = st.number_input("Cantidad:", min_value=1, max_value=20, value=1)
    
    if st.button("Anotar a mi cuenta ➕"):
        if nombre:
            st.session_state.consumos.append({
                "Invitado": nombre, "Producto": prod, "Cant": cant, "Subtotal": precio_actual * cant
            })
            st.toast(f"✅ {cant}x {prod} anotado.")
        else:
            st.error("⚠️ Poné tu nombre.")

# 4. --- TABLAS DE RESULTADOS ---
if st.session_state.consumos:
    st.divider()
    df = pd.DataFrame(st.session_state.consumos)
    
    # Resumen por invitado
    resumen = df.groupby("Invitado")["Subtotal"].sum().reset_index()
    resumen.columns = ["Invitado", "Total a Pagar ($)"]
    
    st.write("### 💵 Resumen para pagar")
    st.table(resumen)
    
    with st.expander("Ver detalle de pedidos"):
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.write(f"**Total acumulado en el bar: ${df['Subtotal'].sum():,}**")

    if st.button("❌ Limpiar todo (Solo cumpleañero)"):
        st.session_state.consumos = []
        st.rerun()



