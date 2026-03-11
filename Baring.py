import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Calculadora de Cumple", page_icon="🍻")

st.title("🍻 ¿Cuánto llevo tomando?")
st.subheader("Festejo de Cumpleaños")

# --- CONFIGURACIÓN DEL BAR (Edita esto) ---
PRODUCTOS = {
    "Cerveza Pinta": 3500,
    "Cerveza Media": 2200,
    "Gin Tonic": 4500,
    "Fernet": 4800,
    "Gaseosa/Agua": 1800,
    "Burger/Pizza": 7500
}

# --- BASE DE DATOS TEMPORAL ---
if 'consumos' not in st.session_state:
    st.session_state.consumos = []

# --- INTERFAZ PARA EL INVITADO ---
with st.form("registro_consumo"):
    nombre = st.text_input("Tu nombre:", placeholder="Ej: Juan Perez").strip()
    opcion = st.selectbox("¿Qué pediste?", list(PRODUCTOS.keys()))
    submit = st.form_submit_button("Añadir a mi cuenta ➕")

    if submit:
        if nombre:
            st.session_state.consumos.append({
                "Nombre": nombre,
                "Item": opcion,
                "Precio": PRODUCTOS[opcion]
            })
            st.success(f"¡Anotado! {opcion} para {nombre}.")
        else:
            st.error("Por favor, poné tu nombre para saber de quién es la cuenta.")

# --- VISUALIZACIÓN ---
st.divider()
if st.session_state.consumos:
    df = pd.DataFrame(st.session_state.consumos)
    
    # Resumen por persona
    st.write("### 📊 Resumen de Gastos")
    resumen = df.groupby("Nombre")["Precio"].sum().reset_index()
    resumen.columns = ["Invitado", "Total a Pagar ($)"]
    st.table(resumen)

    # Botón para ver el detalle general (solo para vos)
    with st.expander("Ver detalle de todos los pedidos"):
        st.dataframe(df)
else:
    st.info("Todavía no hay consumos registrados. ¡Que empiece la fiesta!")