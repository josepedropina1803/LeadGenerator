# src/ui/website_analysis.py
"""
Módulo UI: Análise de Website (Tab: Relatório de Lead)
"""
import streamlit as st
import pandas as pd
import time
from typing import Dict, Any
import io
import json
import io
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


def render_website_analysis(empresa: pd.Series):
    """..."""
    url = empresa['Website']
    tab_analise, tab_seguranca = st.tabs([
        "📧 Relatório de Lead",
        "🔒 Análise de Segurança"
    ])

    with tab_seguranca:
        render_security_section(url)

    with tab_analise:
        clica = st.button("Clica")
        if(clica):
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

    st.title("🔒 Análise de Segurança do Website")
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


def _render_risk_score_header(report: Dict[str, Any]):
    """Renderiza header com risk score"""
    risk_score = report.get("risk_score", 0)
    risk_level = report.get("risk_level", "UNKNOWN")

    # Definir cores e ícones por nível
    risk_config = {
        "CRITICAL": {"color": "#FF0000", "icon": "🚨", "emoji": "🔴"},
        "HIGH": {"color": "#FF6B00", "icon": "⚠️", "emoji": "🟠"},
        "MEDIUM": {"color": "#FFD700", "icon": "⚠️", "emoji": "🟡"},
        "LOW": {"color": "#90EE90", "icon": "ℹ️", "emoji": "🟢"},
        "VERY LOW": {"color": "#00FF00", "icon": "✅", "emoji": "🟢"}
    }

    config = risk_config.get(risk_level, {"color": "#808080", "icon": "❓", "emoji": "⚪"})

    # Header com cores
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"### {config['icon']} Nível de Risco: **{risk_level}**")

    with col2:
        st.metric("Risk Score", f"{risk_score}/100")

    with col3:
        # Emoji visual
        st.markdown(f"<h1 style='text-align: center;'>{config['emoji']}</h1>", unsafe_allow_html=True)

    # Progress bar colorida
    st.markdown(f"""
        <div style="background-color: #f0f0f0; border-radius: 10px; height: 30px; position: relative;">
            <div style="background-color: {config['color']}; width: {risk_score}%; height: 100%; border-radius: 10px;
                        display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                {risk_score}%
            </div>
        </div>
    """, unsafe_allow_html=True)


def _render_llm_analysis(report: Dict[str, Any]):
    """Renderiza análise LLM de forma destacada"""
    llm_analysis = report.get("llm_analysis", {})

    if not llm_analysis or llm_analysis.get("status") != "✅ Análise Completa":
        st.warning("⚠️ Análise LLM não disponível")
        return

    st.header("🤖 Análise Inteligente (GPT-3.5)")

    analysis_text = llm_analysis.get("analysis", "")

    if analysis_text:
        # Container destacado
        st.markdown("""
            <style>
            .llm-analysis {
                background-color: #f8f9fa;
                border-left: 5px solid #4CAF50;
                padding: 20px;
                border-radius: 5px;
                margin: 10px 0;
            }
            </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="llm-analysis">', unsafe_allow_html=True)
            st.markdown(analysis_text)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhuma análise gerada")


def _render_quick_metrics(report: Dict[str, Any]):
    """Renderiza métricas rápidas"""
    st.subheader("📈 Métricas Rápidas")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        ssl_advanced = report.get("ssl_advanced", {})
        dias = ssl_advanced.get("dias_restantes", "N/A")
        st.metric(
            "🔐 Certificado SSL",
            f"{dias} dias" if isinstance(dias, int) else dias,
            delta="Válido" if isinstance(dias, int) and dias > 30 else "Expirando"
        )

    with col2:
        headers = report.get("headers_check", {})
        headers_ok = sum(1 for v in headers.values() if "✅" in str(v))
        st.metric(
            "📋 Headers Seguros",
            f"{headers_ok}/4",
            delta="OK" if headers_ok >= 3 else "Atenção"
        )

    with col3:
        vulns = len(report.get("vulnerabilities", []))
        st.metric(
            "⚠️ Vulnerabilidades",
            vulns,
            delta="Crítico" if vulns > 5 else ("Atenção" if vulns > 0 else "OK"),
            delta_color="inverse"
        )

    with col4:
        exposed = report.get("exposed_files", {})
        critical = len(exposed.get("critical_exposed", []))
        st.metric(
            "🚨 Arquivos Críticos",
            critical,
            delta="CRÍTICO" if critical > 0 else "Seguro",
            delta_color="inverse"
        )


def _render_ssl_details(report: Dict[str, Any]):
    """Renderiza detalhes SSL"""
    with st.expander("🔐 **SSL/TLS Avançado**", expanded=True):
        ssl_adv = report.get("ssl_advanced", {})

        if ssl_adv:
            st.markdown(f"**Status:** {ssl_adv.get('status', 'N/A')}")

            if ssl_adv.get('dias_restantes'):
                dias = ssl_adv['dias_restantes']
                cor = "🟢" if dias > 30 else ("🟡" if dias > 7 else "🔴")
                st.markdown(f"{cor} **Expira em:** {dias} dias")

            if ssl_adv.get('protocolo'):
                st.markdown(f"**Protocolo:** {ssl_adv['protocolo']}")

            if ssl_adv.get('emissor'):
                st.markdown(f"**Emissor:** {ssl_adv['emissor']}")

            if ssl_adv.get('issues'):
                st.error("**Problemas:**")
                for issue in ssl_adv['issues']:
                    st.markdown(f"- {issue}")

            if ssl_adv.get('info'):
                for info in ssl_adv['info']:
                    st.success(info)
        else:
            st.info("Sem dados SSL avançados")


def _render_headers_details(report: Dict[str, Any]):
    """Renderiza detalhes de headers"""
    with st.expander("📋 **Headers de Segurança**"):
        headers = report.get("headers_check", {})

        if headers:
            for header, status in headers.items():
                if "✅" in status:
                    st.success(f"**{header}**: {status}")
                else:
                    st.error(f"**{header}**: {status}")
        else:
            st.info("Sem dados de headers")


def _render_cookie_details(report: Dict[str, Any]):
    """Renderiza detalhes de cookies"""
    with st.expander("🍪 **Segurança de Cookies**"):
        cookies = report.get("cookie_security", {})

        if cookies:
            st.markdown(f"**Status:** {cookies.get('status', 'N/A')}")
            st.markdown(f"**Cookies Analisados:** {cookies.get('cookies_analyzed', 0)}")

            if cookies.get('issues'):
                st.warning("**Problemas Detectados:**")
                for issue in cookies['issues'][:5]:  # Mostrar só os 5 primeiros
                    st.markdown(f"- {issue}")
            else:
                st.success("✅ Nenhum problema detectado")
        else:
            st.info("Sem dados de cookies")


def _render_vulnerabilities(report: Dict[str, Any]):
    """Renderiza vulnerabilidades"""
    with st.expander("⚠️ **Vulnerabilidades Detectadas**", expanded=True):
        vulns = report.get("vulnerabilities", [])

        if vulns:
            for vuln in vulns:
                st.warning(vuln)
        else:
            st.success("✅ Nenhuma vulnerabilidade detectada!")


def _render_exposed_files(report: Dict[str, Any]):
    """Renderiza arquivos expostos"""
    with st.expander("📁 **Arquivos e Diretórios Expostos**"):
        exposed = report.get("exposed_files", {})

        if exposed:
            critical = exposed.get("critical_exposed", [])
            warnings = exposed.get("warnings", [])
            total = exposed.get("total_exposed", 0)

            st.markdown(f"**Total de arquivos verificados:** {total}")

            if critical:
                st.error(f"**🚨 CRÍTICOS ({len(critical)}):**")
                for item in critical:
                    st.markdown(f"- {item}")
            else:
                st.success("✅ Nenhum arquivo crítico exposto")

            if warnings:
                with st.expander(f"⚠️ Avisos ({len(warnings)})"):
                    for warn in warnings[:10]:  # Mostrar só os 10 primeiros
                        st.markdown(f"- {warn}")
        else:
            st.info("Sem dados de arquivos expostos")


def _render_cms_detection(report: Dict[str, Any]):
    """Renderiza detecção de CMS"""
    with st.expander("🎨 **CMS Detectado**"):
        cms = report.get("cms_detection", {})

        if cms:
            st.markdown(f"**Status:** {cms.get('status', 'N/A')}")

            if cms.get('cms'):
                st.info(f"**CMS:** {cms['cms']}")

                if cms.get('version'):
                    st.markdown(f"**Versão:** {cms['version']}")

                if cms.get('warnings'):
                    st.warning("**Avisos:**")
                    for warn in cms['warnings']:
                        st.markdown(f"- {warn}")
            else:
                st.success("✅ Nenhum CMS conhecido detectado (pode ser site custom)")
        else:
            st.info("Sem dados de CMS")
