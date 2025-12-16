from typing import Any, Dict
import streamlit as st

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