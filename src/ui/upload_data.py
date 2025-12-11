# src/ui/upload_data.py
"""
Módulo UI: Upload e validação de dados
"""
import streamlit as st
import pandas as pd


def render_upload_data():
    """
    Renderiza a seção de upload de dados e retorna o DataFrame
    
    Returns:
        pd.DataFrame ou None: DataFrame carregado ou None se não houver upload
    """
    st.header("📂 Upload de Dataset")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo CSV ou Excel", 
        type=["csv", "xlsx"]
    )
    
    if uploaded_file is None:
        _render_sample_data()
        return None
    
    try:
        # Ler o arquivo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validar colunas necessárias
        colunas_necessarias = ['Nome', 'Website', 'Descrição Atividade']
        if all(col in df.columns for col in colunas_necessarias):
            st.success("✅ Dataset carregado com sucesso!")
            
            # Preview dos dados
            with st.expander("👁️ Preview dos dados"):
                st.dataframe(df.head())
                st.caption(f"Total de {len(df)} empresas no dataset")
            
            return df
        else:
            st.error(
                f"❌ Colunas necessárias não encontradas. "
                f"Necessário: {colunas_necessarias}"
            )
            return None
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
        return None


def _render_sample_data():
    """
    Renderiza informações sobre dados de exemplo
    """
    st.info("👆 Faça upload de um dataset ou veja o exemplo abaixo:")
    
    # Dataset de exemplo
    sample_data = {
        'Nome': ['Tech Solutions', 'MediCare', 'EcoRetail'],
        'Website': [
            'https://techsolutions.com', 
            'https://medicare.com', 
            'https://ecoretail.com'
        ],
        'Descrição Atividade': [
            'Empresa especializada em desenvolvimento de software para startups.',
            'Fornecedor de equipamentos médicos e telemedicina.',
            'Plataforma de e-commerce sustentável com produtos ecológicos.'
        ]
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df)
    
    # Informações sobre o formato
    st.markdown("### 📝 Formato Necessário")
    st.markdown("""
    O dataset deve conter as seguintes colunas:
    - **Nome**: Nome da empresa
    - **Website**: URL do website  
    - **Descrição Atividade**: Descrição detalhada da empresa
    
    **Formatos aceitos:** CSV, Excel (.xlsx)
    """)