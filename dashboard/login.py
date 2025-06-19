import streamlit as st # type: ignore
import os

def login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.logged_in:
        placeholder = st.empty()

        with placeholder.form("login"):
            current_dir = os.path.dirname(__file__)
            image_path = os.path.join(current_dir, "images/LCG_logo.png")
            st.image(image_path, use_container_width=True, width=200)
            st.markdown("<h1 style='text-align: center;'>¡Bienvenido!</h1>", unsafe_allow_html=True)
            st.markdown("### Iniciar sesión")
            username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            submit = st.form_submit_button("Iniciar sesión")

        if submit:
            if (username == "admin" and password == "admin") or (username == "user" and password == "user") or (username == "LCG" and password == "BC_dashboard"):
                st.session_state.logged_in = True
                st.session_state.username = username
                placeholder.empty()
                st.success(f"Inicio de sesión exitoso para {username.upper()}")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        return False
    return True
