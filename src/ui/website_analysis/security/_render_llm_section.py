from typing import Any, Dict
import streamlit as st

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
