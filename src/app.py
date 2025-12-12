# src/app.py
"""
LeadGenerator - Orquestrador Principal
Camada de visualização - apenas orquestra os componentes UI
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")




# Adiciona o diretório src ao path para permitir imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
    
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Imports dos módulos UI
from ui.pagesEnum import Pages
from ui.sidebar import render_sidebar

from ui.company_selector import render_company_selector
from ui.company_details import render_company_details
from ui.website_analysis import render_website_analysis

# Configuração da página
st.set_page_config(
    page_title="LeadGenerator - AI Agents",
    page_icon="🏢",
    layout="wide"
)

# Título principal
st.title("🏢 Lead Generator")
st.markdown("---")

# Renderizar sidebar
render_sidebar()


if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
        # Dados já carregados - mostrar dashboard
        st.success("✅ Dataset loaded!")
        df = st.session_state.uploaded_data
        st.info(f"Dataset with {len(df)} companies ready for analysis!")
        
        # Aqui você coloca o conteúdo do seu dashboard principal
        st.subheader("📊 General Analysis")
        # ... resto da lógica do dashboard
        if st.button("🏠 Website Analysis"):
                st.switch_page(Pages.WEBSITE_ANALYZER.value)
else:
        # Nenhum dado carregado - redirecionar para upload
        st.warning("⚠️ No dataset was loaded. Please upload from \"Upload Data\" first.")
        if st.button("📤 Upload Data", type="primary"):
            st.switch_page(Pages.UPLOAD_DATA.value)



# Rodapé
st.markdown("---")
st.markdown("🤖 Sistema de Análise de Empresas com AI Agents | Desenvolvido com Streamlit")