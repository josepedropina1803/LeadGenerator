# src/ui/website_analysis.py
"""
Módulo UI: Análise de Website (Tab: Relatório de Lead)
"""
import streamlit as st
import pandas as pd
import time
from typing import Dict, Any

from orchestration.security_workflow import run_security_check
from services.check_valid_url import is_valid_url


try:
    from agents.categorization_agent import CategorizationAgent
    from agents.website_agent import WebsiteAgent
    from agents.needs_agent import NeedsAgent
    from agents.classification_agent import ClassificationAgent
except ImportError:
    pass


def render_website_analysis(empresa: pd.Series):
    """..."""
    url = empresa['Website']
    tab_analise, tab_seguranca = st.tabs([
        "📧 Relatório de Lead",
        "🔒 Segurança"
    ])
    
    with tab_seguranca:
        render_security_section(url)
    with tab_analise:
        clica = st.button("Clica")
        if(clica):  
            _execute_analysis(url)
            _avaliar_website(url)
            _render_analysis_results(empresa)
    


def _execute_analysis(url: str):
    """
    Executa a análise usando os agentes
    
    Args:
        url: URL do website a analisar
    """
    with st.spinner("🤖 AI Agents Analyzing..."):
        # Simular processamento
        time.sleep(2)
        # Executar agentes
        if(is_valid_url(url)):
            
            avaliacao_website = _avaliar_website(url)
            # Armazenar resultados
            st.session_state.analise_results = {
                "avaliacao_website": avaliacao_website,
            }
        else:
            st.error(f"URL not Valid! url: {url}")
        
        

def _avaliar_website(url: str) -> str:
    """Avalia o website usando o agente"""
    try:
        agent = WebsiteAgent()
        result = agent.process({"url": url})
        return result.get("avaliacao", "Não foi possível avaliar")
    except Exception as e:
        st.error(f"Erro na avaliação: {e}")
        return "Erro na análise"


def _render_analysis_results(empresa: pd.Series):
    """
    Renderiza os resultados da análise
    
    Args:
        empresa: Series com dados da empresa
    """
    resultados = st.session_state.analise_results
    
    st.header("📈 Resultados da Análise")
    
    
    
    # Avaliação do website
    _render_website_evaluation(resultados)

    
    
   
    
    # Botão de exportação
    if st.button("💾 Exportar Relatório"):
        st.success("✅ Relatório exportado com sucesso!")
        st.info("🔜 Funcionalidade de exportação em desenvolvimento...")


def _render_website_evaluation(resultados: Dict):
    """Renderiza avaliação geral do website"""
    st.subheader("🌐 Avaliação Geral do Website")
    
    # Informação sobre a escala
    st.info(
        "📊 **Escala de Avaliação:** Cada parâmetro é avaliado de **0 a 5**, onde:\n"
        "- **0** = Muito Fraco\n"
        "- **1-2** = Insuficiente  \n"
        "- **3** = Satisfatório  \n"
        "- **4** = Bom  \n"
        "- **5** = Excelente"
    )
    
    # Análise detalhada
    st.markdown("### 📋 Análise Detalhada")
    
    avaliacao_texto = resultados.get('avaliacao_website', 'Não foi possível avaliar')
    
    with st.container():
        st.markdown("---")
        
        # Processar e exibir cada linha da avaliação
        linhas = avaliacao_texto.split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if linha:
                # Destacar critérios (linhas que começam com número)
                if linha[0].isdigit() and '.' in linha[:3]:
                    st.markdown(f"#### {linha}")
                else:
                    st.markdown(linha)
                st.markdown("")  # Espaço entre parágrafos
        
        st.markdown("---")


def render_security_section(url: str):
    """Renderiza segurança com atualizações dinâmicas"""
    
    st.subheader("🔒 Segurança do Website")
    
    if st.button("🚀 Verificar Segurança", key="security_check"):
        # Containers para atualizar em tempo real
        status_container = st.container()
        metrics_container = st.container()
        details_container = st.container()
        
        with st.spinner("🔍 Verificando..."):
            # Executar workflow
            report = run_security_check(url)
        
        # Atualizar status
        with status_container:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                ssl_status = report["ssl_status"].get("status", "❌ Erro")
                st.metric("SSL/TLS", ssl_status)
            
            with col2:
                headers_present = sum(
                    1 for v in report["headers_check"].values() 
                    if "✅" in str(v)
                )
                st.metric("Headers Seguros", f"{headers_present}/4")
            
            with col3:
                vulns = len(report["vulnerabilities"])
                risk_color = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }
                risk_icon = risk_color.get(report["risk_level"], "⚪")
                st.metric("Nível de Risco", f"{risk_icon} {report['risk_level']}")
        
        st.markdown("---")
        
        # Detalhes
        with details_container:
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("#### ✅ OK")
                for issue in report["security_issues"]:
                    if "✅" in issue:
                        st.write(issue)
            
            with col_right:
                st.markdown("#### ⚠️ Problemas")
                if report["vulnerabilities"]:
                    for vuln in report["vulnerabilities"]:
                        st.warning(vuln)
                else:
                    st.success("Nenhuma vulnerabilidade detectada!")
            
            st.markdown("---")
            
            # Expanders com detalhes
            with st.expander("🔍 Detalhes Completos"):
                st.json(report)


    """
    Retorna dados dummy de segurança
    TODO: Substituir por dados reais
    """
    return {
        'ssl': {
            'valido': True,
            'emissor': 'Let\'s Encrypt',
            'valido_ate': '15 Jan 2025',
            'dias_restantes': 36,
            'protocolo': 'TLSv1.2',
            'algoritmo_assinatura': 'RSA-SHA256',
            'tamanho_chave': '2048 bits',
            'sans': ['exemplo.com', 'www.exemplo.com']
        },
        'redirect': {
            'http_para_https': False,
            'www_redirect': True
        },
        'security_headers': {
            'hsts': {
                'habilitado': True,
                'max_age': 31536000,
                'includeSubDomains': True,
                'preload': False
            },
            'x_content_type_options': 'nosniff',
            'x_frame_options': None,
            'content_security_policy': None,
            'referrer_policy': 'no-referrer-when-downgrade',
            'permissions_policy': None
        },
        'cookies': {
            'usa_cookies': True,
            'secure': True,
            'httponly': True,
            'samesite': 'Lax'
        },
        'servidor': {
            'http2': True,
            'http3': False,
            'compressao': 'gzip',
            'versao_exposta': 'Apache/2.4.41',
            'mixed_content': False
        },
        'score': {
            'nota': 'C+',
            'pontuacao': 65,
            'nivel': 'Melhorias necessárias'
        }
    }