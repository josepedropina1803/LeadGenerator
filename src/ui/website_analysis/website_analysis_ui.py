# src/ui/website_analysis.py
"""
Módulo UI: Análise de Website (Tab: Relatório de Lead)
"""
from .security._render_details import _render_cms_detection, _render_cookie_details, _render_exposed_files, _render_headers_details, _render_ssl_details, _render_vulnerabilities
from .security._render_llm_section import _render_llm_analysis
from .security._render_metrics import _render_quick_metrics
from .security._render_security_header import _render_risk_score_header
import streamlit as st
import pandas as pd
import time
from typing import Dict, Any, Union
import json
import os
import re
import unicodedata
from orchestration.security_workflow import run_security_check
from services.check_valid_url import is_valid_url

try:
    from fpdf import FPDF
    _CAN_EXPORT_PDF = True
except Exception:
    _CAN_EXPORT_PDF = False

try:
    from agents.categorization_agent import CategorizationAgent
    from agents.website_agent import WebsiteAgent
    from agents.needs_agent import NeedsAgent
    from agents.classification_agent import ClassificationAgent
except ImportError:
    pass


def render_website_analysis(empresa_ou_url: Union[pd.Series, str]):

    if isinstance(empresa_ou_url, str):
        url = empresa_ou_url
        empresa = pd.Series({'Website':url, 'Nome':url})
    elif isinstance(empresa_ou_url, pd.Series):
        url = empresa_ou_url['Website']
        empresa = empresa_ou_url
    else:
        st.error("Entry type invalid to analyze website.")
    
    tab_analise, tab_seguranca = st.tabs([
        "📧 Report Specialist",
        "🔒 Security Analyst"
    ])

    with tab_seguranca:
        render_security_section(url)

    with tab_analise:
        st.title("📧 Generalized Report")
        st.markdown(f"**URL:** `{url}`")
        st.markdown("---")
        
        if(st.button("📧 Iniciar Verificação Completa", type="primary", use_container_width=True)):
            _execute_analysis(url)
            _avaliar_website(url)
            _render_analysis_results(empresa)

def _create_pdf_bytes(report: Dict[str, Any]) -> bytes:
    """Cria um PDF em memória com um resumo do relatório e retorna os bytes.
    Usa fpdf se disponível; caso contrário retorna JSON bytes (fallback)."""
    # Fallback para JSON quando PDF não estiver disponível
    if not _CAN_EXPORT_PDF:
        return json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8")

    # Montar texto legível a partir do dicionário do report
    lines = []
    lines.append("Análise de Segurança")
    lines.append("====================")
    lines.append(f"Risk Level: {report.get('risk_level', 'N/A')}")
    lines.append(f"Risk Score: {report.get('risk_score', 'N/A')}")
    lines.append("")

    llm = report.get("llm_analysis", {})
    if llm and llm.get("analysis"):
        lines.append("Análise LLM:")
        lines.append(llm.get("analysis", ""))
        lines.append("")

    quick_metrics = []
    ssl_adv = report.get("ssl_advanced", {})
    if ssl_adv:
        dias = ssl_adv.get("dias_restantes", None)
        quick_metrics.append(f"SSL dias restantes: {dias}")

    headers_check = report.get("headers_check", {})
    if headers_check:
        ok_count = sum(1 for v in headers_check.values() if "✅" in str(v))
        quick_metrics.append(f"Headers seguros: {ok_count}/{len(headers_check)}")

    vulns = report.get("vulnerabilities", [])
    quick_metrics.append(f"Vulnerabilidades: {len(vulns)}")

    exposed = report.get("exposed_files", {})
    critical = len(exposed.get("critical_exposed", []))
    quick_metrics.append(f"Arquivos críticos expostos: {critical}")

    if quick_metrics:
        lines.append("Métricas Rápidas:")
        for m in quick_metrics:
            lines.append(f"- {m}")
        lines.append("")

    if vulns:
        lines.append("Vulnerabilidades (lista):")
        for v in vulns[:30]:
            lines.append(f"- {v}")
        lines.append("")

    if exposed:
        critical_list = exposed.get("critical_exposed", [])
        warnings = exposed.get("warnings", [])
        lines.append(f"Arquivos críticos ({len(critical_list)}):")
        for it in critical_list[:30]:
            lines.append(f"- {it}")
        lines.append("")
        if warnings:
            lines.append(f"Avisos ({len(warnings)}):")
            for w in warnings[:30]:
                lines.append(f"- {w}")
            lines.append("")

    cms = report.get("cms_detection", {})
    if cms:
        lines.append("CMS Detectado:")
        lines.append(f"- Status: {cms.get('status', 'N/A')}")
        if cms.get('cms'):
            lines.append(f"- CMS: {cms.get('cms')}")
        if cms.get('version'):
            lines.append(f"- Versão: {cms.get('version')}")
        if cms.get('warnings'):
            for w in cms.get('warnings', []):
                lines.append(f"- {w}")
        lines.append("")

    # Adicionar uma secção com JSON (resumida)
    lines.append("Dados brutos (JSON resumido):")
    json_chunk = json.dumps(report, indent=2, ensure_ascii=False)
    if len(json_chunk) > 4000:
        lines.append(json_chunk[:4000] + "\n...TRUNCADO...")
    else:
        lines.append(json_chunk)

    # Aux: tentar usar fonte TTF (DejaVu) para unicode; se não, sanitizar texto
    def _sanitize_for_pdf(s: str) -> str:
        if s is None:
            return ""
        if not isinstance(s, str):
            s = str(s)
        # Se já é codificável em latin-1, return original
        try:
            s.encode('latin-1')
            return s
        except Exception:
            # Normalizar (remove diacríticos), depois remover chars não-ascii
            s_norm = unicodedata.normalize('NFKD', s)
            s_ascii = s_norm.encode('ascii', 'ignore').decode('ascii', 'ignore')
            # Remover resto de não-ASCII (ex: emojis)
            s_ascii = re.sub(r'[^\x00-\x7F]+', '', s_ascii)
            return s_ascii

    # Gerar PDF com fpdf
    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()

    # Tentar registrar DejaVu Sans (unicode)
    font_registered = False
    font_candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/local/share/fonts/DejaVuSans.ttf',
        '/Library/Fonts/DejaVu Sans.ttf',
        '/Library/Fonts/DejaVuSans.ttf',
        os.path.join(os.getcwd(), 'DejaVuSans.ttf'),
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                pdf.add_font('DejaVu', '', path, uni=True)
                pdf.set_font('DejaVu', size=11)
                font_registered = True
                break
            except Exception:
                font_registered = False

    if not font_registered:
        # fallback para Helvetica + sanitização do texto para evitar caracteres problemáticos
        pdf.set_font("Helvetica", size=11)

    for paragraph in lines:
        paragraph_s = _sanitize_for_pdf(paragraph) if not font_registered else paragraph
        pdf.multi_cell(0, 6, paragraph_s)
        pdf.ln(2)

    output = pdf.output(dest="S")
    if isinstance(output, str):
        # Saída as bytes; latin-1 aqui é seguro porque sanitizamos quando necessário.
        try:
            output = output.encode("latin-1")
        except Exception:
            output = output.encode("utf-8", errors="ignore")
    return output

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
    """
    Renderiza análise de segurança completa com visualização melhorada
    """

    st.title("🔒 Security First!")
    st.markdown(f"**URL:** `{url}`")
    st.markdown("---")

    if st.button("🚀 Iniciar Verificação Completa", type="primary", use_container_width=True):

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("🔍 Iniciando verificação de segurança...")
        progress_bar.progress(10)

        try:
            # Executar workflow
            status_text.text("🔐 Verificando SSL/TLS...")
            progress_bar.progress(30)

            report = run_security_check(url)

            status_text.text("✅ Análise concluída!")
            progress_bar.progress(100)
            time.sleep(0.5)

            # Limpar progress
            progress_bar.empty()
            status_text.empty()

            # Renderizar resultados
            _render_security_results(report)

        except Exception as e:
            st.error(f"❌ Erro na verificação: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def _render_security_results(report: Dict[str, Any]):
    """Renderiza resultados da análise de segurança"""

    # ========== HEADER: RISK SCORE ==========
    _render_risk_score_header(report)

    st.markdown("---")

    # ========== ANÁLISE LLM (DESTAQUE) ==========
    _render_llm_analysis(report)

    st.markdown("---")

    # ========== MÉTRICAS RÁPIDAS ==========
    _render_quick_metrics(report)

    st.markdown("---")

    # ========== DETALHES POR CATEGORIA ==========
    st.header("📊 Análise Detalhada")

    col1, col2 = st.columns(2)

    with col1:
        _render_ssl_details(report)
        _render_headers_details(report)
        _render_cookie_details(report)

    with col2:
        _render_vulnerabilities(report)
        _render_exposed_files(report)
        _render_cms_detection(report)

    # ========== DADOS RAW (EXPANDIDO) ==========
    with st.expander("🔍 Ver Dados Técnicos Completos (JSON)"):
        st.json(report)

    # ========== EXPORTAÇÃO ==========
    st.markdown("---")
    st.subheader("💾 Exportar Relatório")
    if _CAN_EXPORT_PDF:
        # Gera os bytes do PDF e oferece download
        pdf_bytes = _create_pdf_bytes(report)
        st.download_button(
            label="Exportar como PDF",
            data=pdf_bytes,
            file_name="security_report.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Exportar para PDF requer a biblioteca 'fpdf'. Para habilitar, execute: pip install fpdf")
        st.download_button(
            label="Exportar JSON (fallback)",
            data=json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8"),
            file_name="security_report.json",
            mime="application/json"
        )









