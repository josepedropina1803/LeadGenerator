# src/ui/company_details.py
"""
Módulo UI: Detalhes da empresa (Tab: Dados da Empresa)
"""
import streamlit as st
import pandas as pd


def render_company_details(empresa: pd.Series, df: pd.DataFrame):
    """
    Renderiza os detalhes da empresa na tab "Dados da Empresa"
    
    Args:
        empresa: Series com dados da empresa
        df: DataFrame completo (para obter índice)
    """
    st.subheader(f"Dados da Empresa: {empresa['Nome']}")
    
    # Informações principais em colunas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Website:**", empresa['Website'])
    
    with col2:
        setor_original = empresa.get('Setor', 'Não definido')
        st.write("**Setor (Original):**", setor_original)
    
    with col3:
        # Obter ID da empresa
        index_original = df[df['Nome'] == empresa['Nome']].index[0]
        st.write("**ID:**", index_original + 1)
    
    # Descrição completa
    st.markdown("---")
    st.markdown("### 📄 Descrição da Atividade")
    st.write(empresa['Descrição Atividade'])
    
    # Informações adicionais (se existirem)
    campos_adicionais = [
        'Email', 'Telefone', 'Endereço', 
        'Funcionários', 'Fundação', 'Receita'
    ]
    
    campos_disponiveis = [
        campo for campo in campos_adicionais 
        if campo in empresa.index and pd.notna(empresa.get(campo))
    ]
    
    if campos_disponiveis:
        st.markdown("---")
        st.markdown("### ℹ️ Informações Adicionais")
        
        col1, col2 = st.columns(2)
        
        for idx, campo in enumerate(campos_disponiveis):
            with col1 if idx % 2 == 0 else col2:
                st.write(f"**{campo}:**", empresa[campo])