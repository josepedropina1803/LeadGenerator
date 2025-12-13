from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from agents.security_agent import SecurityAgent
from agents.security_analysis_agent import SecurityAnalysisAgent


# Estado compartilhado entre nodes
class SecurityState(TypedDict):
    url: str
    security_issues: dict
    ssl_status: dict
    ssl_advanced: dict
    headers_check: dict
    vulnerabilities: list
    exposed_files: dict
    cookie_security: dict
    cms_detection: dict
    llm_analysis: dict
    final_report: dict

# Inicializar agentes
security_agent = SecurityAgent()
analysis_agent = SecurityAnalysisAgent()

# Node: Verificar inseguranças gerais
def verify_security(state: SecurityState) -> dict:
    """Node principal - verifica inseguranças"""
    result = security_agent.process({
        "url": state["url"],
        "check_type": "general"
    })
    
    return {"security_issues": result.get("issues", {})}

# Node: Verificar SSL/TLS
def check_ssl(state: SecurityState) -> dict:
    """Node específico - SSL"""
    result = security_agent.process({
        "url": state["url"],
        "check_type": "ssl"
    })
    
    return {"ssl_status": result.get("ssl", {})}

# Node: Verificar headers HTTP
def check_headers(state: SecurityState) -> dict:
    """Node específico - Headers"""
    result = security_agent.process({
        "url": state["url"],
        "check_type": "headers"
    })
    
    return {"headers_check": result.get("headers", {})}

# Node: Verificar vulnerabilidades
def check_vulnerabilities(state: SecurityState) -> dict:
    """Node específico - Vulnerabilidades"""
    result = security_agent.process({
        "url": state["url"],
        "check_type": "vulnerabilities"
    })

    return {"vulnerabilities": result.get("vulnerabilities", [])}

# Node: Verificar SSL avançado
def check_ssl_advanced(state: SecurityState) -> dict:
    """Node específico - SSL Avançado"""
    result = security_agent.process({
        "url": state["url"],
        "check_type": "ssl_advanced"
    })

    return {"ssl_advanced": result.get("ssl_advanced", {})}

# Node: Verificar arquivos expostos
def check_exposed_files(state: SecurityState) -> dict:
    """Node específico - Arquivos Expostos"""
    result = security_agent.process({
        "url": state["url"],
        "check_type": "exposed_files"
    })

    return {"exposed_files": result.get("exposed_files", {})}

# Node: Verificar cookie security
def check_cookie_security(state: SecurityState) -> dict:
    """Node específico - Cookie Security"""
    result = security_agent.process({
        "url": state["url"],
        "check_type": "cookie_security"
    })

    return {"cookie_security": result.get("cookie_security", {})}

# Node: Detectar CMS
def check_cms_detection(state: SecurityState) -> dict:
    """Node específico - CMS Detection"""
    result = security_agent.process({
        "url": state["url"],
        "check_type": "cms_detection"
    })

    return {"cms_detection": result.get("cms_detection", {})}

# Node: Agregar resultados e gerar análise LLM
def aggregate_results(state: SecurityState) -> dict:
    """Node final - consolida tudo e gera análise LLM"""

    # Calcular risk score e level
    risk_score = calculate_risk_score(state)
    risk_level = calculate_risk_level(state)

    # Preparar dados para análise LLM
    analysis_data = {
        "url": state["url"],
        "security_issues": state.get("security_issues", {}),
        "ssl_advanced": state.get("ssl_advanced", {}),
        "headers_check": state.get("headers_check", {}),
        "vulnerabilities": state.get("vulnerabilities", []),
        "exposed_files": state.get("exposed_files", {}),
        "cookie_security": state.get("cookie_security", {}),
        "cms_detection": state.get("cms_detection", {}),
        "risk_score": risk_score,
        "risk_level": risk_level
    }

    # Gerar análise LLM
    llm_result = analysis_agent.process(analysis_data)

    return {
        "final_report": {
            "url": state["url"],
            "security_issues": state["security_issues"],
            "ssl_status": state["ssl_status"],
            "ssl_advanced": state["ssl_advanced"],
            "headers_check": state["headers_check"],
            "vulnerabilities": state["vulnerabilities"],
            "exposed_files": state["exposed_files"],
            "cookie_security": state["cookie_security"],
            "cms_detection": state["cms_detection"],
            "llm_analysis": llm_result.get("llm_analysis", {}),
            "risk_level": risk_level,
            "risk_score": risk_score
        }
    }

def calculate_risk_level(state: SecurityState) -> str:
    """Calcula nível de risco baseado em múltiplos fatores"""
    risk_score = calculate_risk_score(state)

    if risk_score >= 80:
        return "CRITICAL"
    elif risk_score >= 60:
        return "HIGH"
    elif risk_score >= 30:
        return "MEDIUM"
    elif risk_score > 0:
        return "LOW"
    return "VERY LOW"

def calculate_risk_score(state: SecurityState) -> int:
    """Calcula score de risco (0-100)"""
    score = 0

    # Vulnerabilidades gerais (até 30 pontos)
    vuln_count = len(state.get("vulnerabilities", []))
    score += min(vuln_count * 5, 30)

    # Arquivos expostos críticos (até 40 pontos)
    exposed_files = state.get("exposed_files", {})
    critical_exposed = exposed_files.get("critical_exposed", [])
    score += min(len(critical_exposed) * 20, 40)

    # SSL issues (até 20 pontos)
    ssl_advanced = state.get("ssl_advanced", {})
    ssl_issues = ssl_advanced.get("issues", [])
    score += min(len(ssl_issues) * 10, 20)

    # Cookie security (até 10 pontos)
    cookie_security = state.get("cookie_security", {})
    cookie_issues = cookie_security.get("issues", [])
    if len(cookie_issues) > 0:
        score += min(len(cookie_issues) * 2, 10)

    return min(score, 100)

# Construir o workflow
workflow = StateGraph(SecurityState)

# Adicionar nodes
workflow.add_node("verify_security", verify_security)
workflow.add_node("check_ssl", check_ssl)
workflow.add_node("check_ssl_advanced", check_ssl_advanced)
workflow.add_node("check_headers", check_headers)
workflow.add_node("check_vulnerabilities", check_vulnerabilities)
workflow.add_node("check_exposed_files", check_exposed_files)
workflow.add_node("check_cookie_security", check_cookie_security)
workflow.add_node("check_cms_detection", check_cms_detection)
workflow.add_node("aggregate_results", aggregate_results)

# Adicionar edges - todos os checks rodam em paralelo após verify_security
workflow.add_edge(START, "verify_security")
workflow.add_edge("verify_security", "check_ssl")
workflow.add_edge("verify_security", "check_ssl_advanced")
workflow.add_edge("verify_security", "check_headers")
workflow.add_edge("verify_security", "check_vulnerabilities")
workflow.add_edge("verify_security", "check_exposed_files")
workflow.add_edge("verify_security", "check_cookie_security")
workflow.add_edge("verify_security", "check_cms_detection")

# Todos os checks convergem para aggregate_results (que gera análise LLM)
workflow.add_edge("check_ssl", "aggregate_results")
workflow.add_edge("check_ssl_advanced", "aggregate_results")
workflow.add_edge("check_headers", "aggregate_results")
workflow.add_edge("check_vulnerabilities", "aggregate_results")
workflow.add_edge("check_exposed_files", "aggregate_results")
workflow.add_edge("check_cookie_security", "aggregate_results")
workflow.add_edge("check_cms_detection", "aggregate_results")
workflow.add_edge("aggregate_results", END)

# Compilar
security_graph = workflow.compile()

# Usar no Streamlit
def run_security_check(url: str) -> dict:
    """Executa o workflow completo de segurança com análise LLM"""
    state = {
        "url": url,
        "security_issues": {},
        "ssl_status": {},
        "ssl_advanced": {},
        "headers_check": {},
        "vulnerabilities": [],
        "exposed_files": {},
        "cookie_security": {},
        "cms_detection": {},
        "llm_analysis": {},
        "final_report": {}
    }

    result = security_graph.invoke(state)
    return result["final_report"]