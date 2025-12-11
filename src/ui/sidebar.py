# src/ui/sidebar.py
"""
Módulo UI: Sidebar com configurações
"""
import streamlit as st
import os
from dotenv import dotenv_values


def render_sidebar():
    """
    Renderiza a sidebar com configurações da aplicação
    """
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Verificar se há API key no .env
        env_values = dotenv_values()
        api_key = os.getenv("OPENAI_API_KEY", "")
        
        if api_key:
            st.success("🔒 API Key configurada")
        else:
            st.error("❌ API Key não encontrada no .env")
        
        # Slider de temperatura
        model_temp = st.slider("Temperatura do Modelo", 0.0, 1.0, 0.3)
        
        # Informações adicionais
        st.markdown("---")
        with st.expander("ℹ️ Sobre o Sistema"):
            st.markdown("""
            **LeadGenerator v2.0**
            
            Sistema de análise automatizada de empresas.
            
            **Funcionalidades:**
            - 🤖 Análise com AI Agents
            - 🔍 Avaliação de websites
            - 🔒 Análise de segurança
            - 📊 Relatórios detalhados
            """)