import streamlit as st
import pandas as pd

# 1. --- CONFIGURACIÓN DE LA CARTA (Editá esto fácil) ---
# Podés agregar o quitar lo que quieras siguiendo el formato "Nombre": Precio
CARTA = {
    "Cerveza Pinta": 4200,
    "Cerveza Media": 2800,
    "Gin Tonic": 5500,
    "Fernet con Coca": 5800,
    "Gaseosa / Agua": 2200,
    "Papas Fritas": 4500,
    "Burger Completa": 8500,
    "Pizza Muzzarella": 7000
}

# 2. --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Baring - La Cuenta Clara", page_icon="🍺")

# Estilo personalizado para que se vea más "bar"
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #f0a500; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍺 Baring")
st.subheader("Festejo de Cumpleaños")
st.info("Anotá lo que vayas pidiendo para que al final no haya líos con la cuenta.")

# 3. --- BASE DE DATOS EN SESIÓN ---
if 'consumos' not in st.session_state:
    st.session_state.consumos = []

# 4. --- FORMULARIO DE INVITADO ---
with st.form("registro", clear_on_submit=True):
    nombre = st.text_input("Tu nombre (siempre el mismo):", placeholder="Ej: Lucas").strip()
    item = st.selectbox("¿Qué pediste?", list(CARTA.keys()))
    submit = st.form_submit_button("¡Anotar a mi cuenta!")

    if submit:
        if nombre:
            st.session_state.consumos.append({
                "Invitado": nombre,
                "Producto": item,
                "Precio": CARTA[item]
            })
            st.success(f"✅ Anotado: {item} para {nombre}")
        else:
            st.warning("⚠️ Poné tu nombre para que sepamos quién sos.")

# 5. --- RESUMEN FINAL ---
st.divider()
if st.session_state.consumos:
    df = pd.DataFrame(st.session_state.consumos)
    
    # Resumen por persona
    resumen = df.groupby("Invitado")["Precio"].sum().reset_index()
    resumen.columns = ["Invitado", "Total a Pagar ($)"]
    
    st.write("### 💵 Resumen de Cuentas")
    st.dataframe(resumen, use_container_width=True, hide_index=True)
    
    # Detalle total por si hay dudas
    with st.expander("Ver detalle de pedidos (toda la noche)"):
        st.table(df)
        
    if st.button("❌ Borrar todo (Solo para el cumpleañero)"):
        st.session_state.consumos = []
        st.rerun()
else:
    st.write("Aún no hay pedidos. ¡Salud! 🥂")
