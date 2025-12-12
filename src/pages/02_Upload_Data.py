# src/ui/upload_data.py
"""
Módulo UI: Upload e validação de dados
"""
import streamlit as st
import pandas as pd

from ui.pagesEnum import Pages
from ui.upload_data import render_upload_data




st.title("📤 Data Upload")
    
    # Renderizar upload de dados (agora com cache automático)
df = render_upload_data()
    
if df is not None:
    st.success("✅ Dataset loaded and cached!")
    st.balloons()
    if st.button("🧙‍♂️ Start Website Analysis"):
        st.switch_page(Pages.WEBSITE_ANALYZER.value)