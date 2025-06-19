import streamlit as st # type: ignore
from login import login
from dashboard import run_dashboard

#st.set_page_config(page_title="App", layout="wide")

# Inicio de sesión 
if login():
    run_dashboard()
