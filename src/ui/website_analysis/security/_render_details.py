
from typing import Any, Dict
import streamlit as st

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


def _render_vulnerabilities(report: Dict[str, Any]):
    """Renderiza vulnerabilidades"""
    with st.expander("⚠️ **Vulnerabilidades Detectadas**", expanded=True):
        vulns = report.get("vulnerabilities", [])

        if vulns:
            for vuln in vulns:
                st.warning(vuln)
        else:
            st.success("✅ Nenhuma vulnerabilidade detectada!")


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
