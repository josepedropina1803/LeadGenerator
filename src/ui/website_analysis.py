# src/ui/website_analysis.py
"""
Módulo UI: Análise de Website (Tab: Relatório de Lead)
"""
import streamlit as st
import pandas as pd
import time
from typing import Dict, Any

# Imports dos agentes
try:
    from agents.categorization_agent import CategorizationAgent
    from agents.website_agent import WebsiteAgent
    from agents.needs_agent import NeedsAgent
    from agents.classification_agent import ClassificationAgent
except ImportError:
    pass


def render_website_analysis(empresa: pd.Series):
    """
    Renderiza a análise completa do website na tab "Relatório de Lead"
    
    Args:
        empresa: Series com dados da empresa
    """
    st.header(f"📧 Relatório de Lead para {empresa['Nome']}")
    
    # Botão para gerar relatório
    if st.button("🚀 Obter Relatório de Lead", type="primary"):
        _execute_analysis(empresa)
    
    # Verificar se análise foi executada
    if st.session_state.get('analise_results'):
        _render_analysis_results(empresa)
    else:
        st.info(
            "Pressione o botão 'Obter Relatório de Lead' para iniciar "
            "a análise e visualizar os resultados."
        )


def _execute_analysis(empresa: pd.Series):
    """
    Executa a análise usando os agentes
    
    Args:
        empresa: Series com dados da empresa
    """
    with st.spinner("🤖 Agentes AI analisando..."):
        # Simular processamento
        time.sleep(2)
        
        # Executar agentes
        setor = _categorizar_empresa(empresa['Descrição Atividade'])
        avaliacao_website = _avaliar_website(empresa['Website'])
        
        # Armazenar resultados
        st.session_state.analise_results = {
            "setor": setor,
            "avaliacao_website": avaliacao_website,
        }


def _categorizar_empresa(descricao: str) -> str:
    """Categoriza a empresa usando o agente"""
    try:
        agent = CategorizationAgent()
        result = agent.process({"descricao": descricao})
        return result.get("setor", "Não identificado")
    except Exception as e:
        st.error(f"Erro na categorização: {e}")
        return "Erro na análise"


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
    
    # Setor identificado
    _render_sector_section(resultados)
    
    # Avaliação do website
    _render_website_evaluation(resultados)
    
    # Segurança do website
    _render_security_section()
    
    # Resumo executivo
    _render_executive_summary(empresa, resultados)
    
    # Botão de exportação
    if st.button("💾 Exportar Relatório"):
        st.success("✅ Relatório exportado com sucesso!")
        st.info("🔜 Funcionalidade de exportação em desenvolvimento...")


def _render_sector_section(resultados: Dict):
    """Renderiza seção do setor identificado"""
    st.subheader("🏢 Setor Identificado")
    st.info(resultados.get('setor', 'Não identificado'))


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


def _render_security_section():
    """Renderiza seção de segurança do website"""
    st.subheader("🔒 Segurança do Website")
    
    # Dados dummy de segurança
    security_data = _get_dummy_security_data()
    
    # Resumo principal
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if security_data['ssl']['valido']:
            st.metric("Status SSL", "✅ Válido", delta="Ativo")
        else:
            st.metric("Status SSL", "❌ Inválido", delta="Crítico", delta_color="inverse")
        
        st.write(f"**Emissor:** {security_data['ssl']['emissor']}")
        st.write(f"**Protocolo:** {security_data['ssl']['protocolo']}")
    
    with col2:
        dias = security_data['ssl']['dias_restantes']
        if dias > 30:
            st.metric("Validade", f"{dias} dias", delta="OK")
        elif dias > 0:
            st.metric("Validade", f"{dias} dias", delta="Expira em breve", delta_color="inverse")
        else:
            st.metric("Validade", "Expirado", delta="Crítico", delta_color="inverse")
        
        st.write(f"**Válido até:** {security_data['ssl']['valido_ate']}")
    
    with col3:
        nota = security_data['score']['nota']
        if nota.startswith('A'):
            delta_color = "normal"
        elif nota.startswith('B'):
            delta_color = "off"
        else:
            delta_color = "inverse"
        
        st.metric("Avaliação Geral", nota, 
                 delta=security_data['score']['nivel'],
                 delta_color=delta_color)
        st.write(f"**Pontuação:** {security_data['score']['pontuacao']}/100")
    
    st.markdown("---")
    
    # Análise detalhada
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### ✅ Pontos Positivos")
        st.markdown("""
        - ✅ Certificado SSL válido
        - ✅ HSTS habilitado
        - ✅ HTTP/2 suportado
        - ✅ Cookies configurados corretamente
        - ✅ Compressão ativada
        - ✅ X-Content-Type-Options presente
        """)
    
    with col_right:
        st.markdown("#### ⚠️ Problemas Identificados")
        
        if not security_data['redirect']['http_para_https']:
            st.error("🚨 **CRÍTICO:** Sem redirecionamento HTTP → HTTPS")
        
        if security_data['ssl']['dias_restantes'] <= 30:
            st.warning(f"⚠️ Certificado expira em {security_data['ssl']['dias_restantes']} dias")
        
        if security_data['ssl']['protocolo'] == 'TLSv1.2':
            st.warning("⚠️ Usar TLS 1.3 para melhor segurança")
        
        if not security_data['security_headers']['x_frame_options']:
            st.warning("⚠️ Header X-Frame-Options ausente")
        
        if not security_data['security_headers']['content_security_policy']:
            st.info("ℹ️ CSP não configurado (recomendado)")
    
    st.markdown("---")
    
    # Detalhes técnicos em expanders
    with st.expander("🔍 Detalhes Completos do Certificado SSL"):
        st.json(security_data['ssl'])
    
    with st.expander("🔄 Configuração de Redirecionamento"):
        st.json(security_data['redirect'])
    
    with st.expander("🛡️ Headers de Segurança HTTP"):
        st.json(security_data['security_headers'])
    
    with st.expander("🍪 Configuração de Cookies"):
        st.json(security_data['cookies'])
    
    with st.expander("⚙️ Configurações do Servidor"):
        st.json(security_data['servidor'])


def _render_executive_summary(empresa: pd.Series, resultados: Dict):
    """Renderiza resumo executivo"""
    st.markdown("---")
    st.subheader("📋 Resumo Executivo")
    
    st.markdown(f"""
    **Empresa analisada:** {empresa['Nome']}
    
    **Setor principal (AI):** {resultados.get('setor', 'Não identificado')}
    
    **Principais oportunidades identificadas:**
    - Melhoria na presença digital
    - Implementação de automação
    - Fortalecimento da análise de dados
    
    **Recomendação:** Priorizar investimentos em tecnologia e automação 
    para otimizar processos.
    """)


def _get_dummy_security_data() -> Dict:
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