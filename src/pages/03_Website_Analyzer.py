import streamlit as st
import pandas as pd
from services.check_valid_url import is_valid_url
from ui.company_details import render_company_details
from ui.pagesEnum import Pages
from ui.website_analysis import render_website_analysis 
st.title("🧙‍♂️ Website Analyzer")

# Verificar se já temos dados carregados
dataset_loaded = 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None

if dataset_loaded:
    # Dados já carregados - mostrar dashboard
    df = st.session_state.uploaded_data
    source = st.session_state.get('dataset_source', 'uploaded file')
    
    st.success(f"✅ Dataset loaded from {source}! Dataset with {len(df)} companies ready for analysis!")
    
    
    
    # Import e render aqui
    from ui.company_selector import render_company_selector

    empresa = render_company_selector(df)

    st.subheader("📊 General Company Data")

    
    render_company_details(empresa=empresa, df=df)
    render_website_analysis(empresa)

    

    

    
    
else:
    # Nenhum dado carregado - mostrar opções
    st.warning("⚠️ No dataset was loaded. Please choose one of the options below:")
    
    # Radio buttons para opções mutuamente exclusivas
    option = st.radio(
        "Choose data source:",
        ["📤 Upload Dataset File", "🔗 Load Dataset from URL"],
        index=0
    )
    
    if option == "📤 Upload Dataset File":
        st.subheader("Upload Dataset File")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Go to Upload Page", use_container_width=True):
                st.switch_page(Pages.UPLOAD_DATA.value)
        
        with col2:
            st.info("Navigate to the upload page to select and upload your CSV or Excel file.")
    
    else:  # "🔗 Load Dataset from URL"
        st.subheader("Load Dataset from URL")
        url = st.text_input("Dataset URL (CSV format)", 
                           placeholder="https://example.com/dataset.csv",
                           key="dataset_url_input")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Load from URL", use_container_width=True):
                if url:
                    if is_valid_url(url):
                        try:
                            with st.spinner("Loading data from URL..."):
                                # Tentar carregar o dataset
                                df = pd.read_csv(url)
                                
                                # Salvar na session state
                                st.session_state.uploaded_data = df
                                st.session_state.dataset_source = f"URL: {url}"
                                
                                st.success("✅ Dataset loaded successfully!")
                                st.experimental_rerun()
                                
                        except Exception as e:
                            st.error(f"❌ Error loading dataset: {str(e)}")
                    else:
                        st.error("❌ Invalid or inaccessible URL. Please check and try again.")
                else:
                    st.warning("Please enter a URL")
        
        with col2:
            st.info("Enter a direct URL to a CSV file. The URL must be publicly accessible.")
