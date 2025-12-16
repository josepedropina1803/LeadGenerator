from typing import Any, Dict
import streamlit as st

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
