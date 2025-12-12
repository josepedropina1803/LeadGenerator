# src/ui/upload_data.py
"""
Módulo UI: Upload e validação de dados
"""
import streamlit as st
import pandas as pd

from ui.pagesEnum import Pages


def render_upload_data():
    
    
    
    # Verificar se já temos dados em cache
    if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
        st.success("✅ Dataset loaded!")
        df = st.session_state.uploaded_data
        with st.expander("👁️ Data preview (cached)"):
            st.dataframe(df.head())
            st.caption(f"Total of {len(df)} companies inside the dataset")
        
        # Opção para recarregar
        if st.button("🔄 Load new Dataset"):
            st.session_state.uploaded_data = None
            st.experimental_rerun()
            
        return df
    
    uploaded_file = st.file_uploader(
        "Choose .CSV or .XLSX", 
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
            st.success("✅ Dataset loaded with success!")
            
            # Salvar em cache (session state)
            st.session_state.uploaded_data = df
            
            # Preview dos dados
            with st.expander("👁️ Data Preview"):
                st.dataframe(df.head())
                st.caption(f"Total of {len(df)} companies inside the dataset")
            
            return df
        else:
            st.error(
                f"❌ Necessary columns not found. "
                f"Necessary: {colunas_necessarias}"
            )
            return None
            
    except Exception as e:
        st.error(f"❌ Error loading dataset: {str(e)}")
        return None


def _render_sample_data():
    """
    Renderiza informações sobre dados de exemplo
    """
    st.info("👆 Upload a dataset or watch an example below:")
    
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
    st.markdown("### 📝 Necessary Format")
    st.markdown("""
    The datset must contain the following columns:
    - **Nome**: Nome da empresa
    - **Website**: URL do website  
    - **Descrição Atividade**: Descrição detalhada da empresa
    
    **Accepted formats:** CSV, Excel (.xlsx)
    """)


st.title("📤 Data Upload")
    
    # Renderizar upload de dados (agora com cache automático)
df = render_upload_data()
    
if df is not None:
    st.success("✅ Dataset loaded and cached!")
    st.balloons()
    if st.button("🧙‍♂️ Start Website Analysis"):
        st.switch_page(Pages.WEBSITE_ANALYZER.value)