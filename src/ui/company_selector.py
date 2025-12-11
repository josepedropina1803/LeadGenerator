# src/ui/company_selector.py
"""
Módulo UI: Seleção de empresa
"""
import streamlit as st
import pandas as pd


def render_company_selector(df: pd.DataFrame):
    """
    Renderiza o seletor de empresa e retorna os dados da empresa selecionada
    
    Args:
        df: DataFrame com as empresas
        
    Returns:
        pd.Series ou None: Dados da empresa selecionada ou None
    """
    st.header("🎯 Selecionar Empresa")
    
    # Inicializar estado
    if 'empresa_selecionada_nome' not in st.session_state:
        st.session_state.empresa_selecionada_nome = None
    if 'analise_results' not in st.session_state:
        st.session_state.analise_results = {}
    
    # Callback para limpar resultados ao mudar empresa
    def on_empresa_change():
        st.session_state.empresa_selecionada_nome = st.session_state.empresa_select
        st.session_state.analise_results = {}
    
    # Selectbox
    empresa_selecionada_nome = st.selectbox(
        "Escolha uma empresa para análise:",
        df['Nome'].tolist(),
        key="empresa_select",
        on_change=on_empresa_change
    )
    
    if not empresa_selecionada_nome:
        return None
    
    # Obter dados da empresa
    empresa_df = df[df['Nome'] == empresa_selecionada_nome]
    
    if empresa_df.empty:
        st.error("❌ Dados da empresa selecionada não encontrados.")
        return None
    
    return empresa_df.iloc[0]