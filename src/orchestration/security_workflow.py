from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from agents.security_agent import SecurityAgent


# Estado compartilhado entre nodes
class SecurityState(TypedDict):
    url: str
    security_issues: dict
    ssl_status: dict
    headers_check: dict
    vulnerabilities: list
    final_report: dict

# Inicializar agente
security_agent = SecurityAgent()

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

# Node: Agregar resultados
def aggregate_results(state: SecurityState) -> dict:
    """Node final - consolida tudo"""
    return {
        "final_report": {
            "url": state["url"],
            "security_issues": state["security_issues"],
            "ssl_status": state["ssl_status"],
            "headers_check": state["headers_check"],
            "vulnerabilities": state["vulnerabilities"],
            "risk_level": calculate_risk_level(state)
        }
    }

def calculate_risk_level(state: SecurityState) -> str:
    """Calcula nível de risco"""
    vuln_count = len(state["vulnerabilities"])
    if vuln_count > 5:
        return "CRITICAL"
    elif vuln_count > 2:
        return "HIGH"
    elif vuln_count > 0:
        return "MEDIUM"
    return "LOW"

# Construir o workflow
workflow = StateGraph(SecurityState)

# Adicionar nodes
workflow.add_node("verify_security", verify_security)
workflow.add_node("check_ssl", check_ssl)
workflow.add_node("check_headers", check_headers)
workflow.add_node("check_vulnerabilities", check_vulnerabilities)
workflow.add_node("aggregate_results", aggregate_results)

# Adicionar edges
workflow.add_edge(START, "verify_security")
workflow.add_edge("verify_security", "check_ssl")
workflow.add_edge("verify_security", "check_headers")
workflow.add_edge("verify_security", "check_vulnerabilities")
workflow.add_edge("check_ssl", "aggregate_results")
workflow.add_edge("check_headers", "aggregate_results")
workflow.add_edge("check_vulnerabilities", "aggregate_results")
workflow.add_edge("aggregate_results", END)

# Compilar
security_graph = workflow.compile()

# Usar no Streamlit
def run_security_check(url: str) -> dict:
    """Executa o workflow"""
    state = {"url": url, "security_issues": {}, "ssl_status": {}, 
             "headers_check": {}, "vulnerabilities": [], "final_report": {}}
    
    result = security_graph.invoke(state)
    return result["final_report"]