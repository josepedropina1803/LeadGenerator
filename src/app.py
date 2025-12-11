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

# Imports dos módulos UI
from ui.sidebar import render_sidebar
from ui.upload_data import render_upload_data
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

# Upload e validação de dados
df = render_upload_data()

if df is not None:
    # Dados carregados - mostrar seletor de empresa
    empresa = render_company_selector(df)
    
    if empresa is not None:
        # Empresa selecionada - mostrar tabs
        tab_dados, tab_analise = st.tabs([
            "📊 Dados da Empresa", 
            "📧 Relatório de Lead"
        ])
        
        with tab_dados:
            render_company_details(empresa, df)
        
        with tab_analise:
            render_website_analysis(empresa)

# Rodapé
st.markdown("---")
st.markdown("🤖 Sistema de Análise de Empresas com AI Agents | Desenvolvido com Streamlit")