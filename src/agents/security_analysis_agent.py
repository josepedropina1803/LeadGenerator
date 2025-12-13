"""
Security Analysis Agent

Agente que usa LLM para interpretar resultados de análise de segurança
e gerar relatórios em linguagem natural.
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .base_agent import BaseAgent
import os
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()


class SecurityAnalysisAgent(BaseAgent):
    """
    Agente que analisa resultados de segurança usando LLM.

    Gera:
    - Resumo executivo
    - Análise detalhada
    - Recomendações priorizadas
    - Explicações em linguagem clara
    """

    def __init__(self):
        super().__init__("SecurityAnalysisAgent")

        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,  # Baixa temperatura para análise técnica
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.analysis_prompt = PromptTemplate(
            template="""Você é um especialista em segurança de websites. Analise os seguintes resultados de uma verificação de segurança e forneça uma interpretação detalhada.

URL Analisado: {url}
Risk Score: {risk_score}/100
Risk Level: {risk_level}

DADOS DA ANÁLISE:
{security_data}

Por favor, forneça:

1. RESUMO EXECUTIVO (2-3 frases)
   - Avaliação geral da segurança do site
   - Principais problemas encontrados

2. ANÁLISE DETALHADA
   Por categoria, explique o que foi encontrado e o impacto:
   - Protocolo e SSL/TLS
   - Headers de Segurança
   - Vulnerabilidades
   - Arquivos Expostos
   - Cookies
   - CMS Detectado

3. PRINCIPAIS RISCOS (ordenados por gravidade)
   Liste os 3-5 riscos mais críticos com:
   - Descrição do risco
   - Impacto potencial
   - Probabilidade de exploração

4. RECOMENDAÇÕES PRIORIZADAS
   Liste 5-7 ações recomendadas em ordem de prioridade:
   - O que fazer
   - Por que é importante
   - Dificuldade de implementação (Fácil/Média/Difícil)

5. PONTOS POSITIVOS
   O que o site está fazendo corretamente em termos de segurança

Seja técnico mas claro. Use emojis quando apropriado (🚨, ⚠️, ✅, 🔒, etc).
Responda em Português de Portugal.""",
            input_variables=["url", "risk_score", "risk_level", "security_data"]
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa resultados de segurança usando LLM.

        Args:
            input_data: Dict contendo os resultados do security workflow

        Returns:
            Dict com análise interpretada pelo LLM
        """
        try:
            self.log_action("Iniciando análise com LLM", {})

            # Extrair dados
            url = input_data.get("url", "")
            risk_score = input_data.get("risk_score", 0)
            risk_level = input_data.get("risk_level", "UNKNOWN")

            # Formatar dados para o LLM
            security_data = self._format_security_data(input_data)

            # Criar chain
            chain = self.analysis_prompt | self.llm

            # Executar análise
            response = chain.invoke({
                "url": url,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "security_data": security_data
            })

            analysis_text = response.content

            self.log_action("Análise LLM concluída", {"chars": len(analysis_text)})

            return {
                "llm_analysis": {
                    "status": "✅ Análise Completa",
                    "analysis": analysis_text,
                    "url": url,
                    "risk_score": risk_score,
                    "risk_level": risk_level
                }
            }

        except Exception as e:
            self.logger.error(f"Erro na análise LLM: {str(e)}")
            return {
                "llm_analysis": {
                    "status": "❌ Erro na análise",
                    "error": str(e)
                }
            }

    def _format_security_data(self, data: Dict[str, Any]) -> str:
        """
        Formata dados de segurança para o prompt do LLM.

        Args:
            data: Dados brutos do security workflow

        Returns:
            String formatada para o LLM
        """
        formatted = []

        # Protocolo e SSL
        if "security_issues" in data:
            formatted.append("## PROTOCOLO")
            for issue in data["security_issues"]:
                formatted.append(f"- {issue}")

        # SSL Avançado
        if "ssl_advanced" in data:
            ssl = data["ssl_advanced"]
            formatted.append("\n## SSL/TLS")
            formatted.append(f"- Status: {ssl.get('status')}")
            if ssl.get('dias_restantes'):
                formatted.append(f"- Dias até expiração: {ssl.get('dias_restantes')}")
            if ssl.get('protocolo'):
                formatted.append(f"- Protocolo: {ssl.get('protocolo')}")
            if ssl.get('emissor'):
                formatted.append(f"- Emissor: {ssl.get('emissor')}")
            if ssl.get('issues'):
                for issue in ssl.get('issues', []):
                    formatted.append(f"  - {issue}")
            if ssl.get('info'):
                for info in ssl.get('info', []):
                    formatted.append(f"  - {info}")

        # Headers
        if "headers_check" in data:
            formatted.append("\n## HEADERS DE SEGURANÇA")
            for header, status in data["headers_check"].items():
                formatted.append(f"- {header}: {status}")

        # Vulnerabilidades
        if "vulnerabilities" in data:
            formatted.append("\n## VULNERABILIDADES")
            for vuln in data["vulnerabilities"]:
                formatted.append(f"- {vuln}")

        # Arquivos Expostos
        if "exposed_files" in data:
            exp = data["exposed_files"]
            formatted.append("\n## ARQUIVOS EXPOSTOS")
            formatted.append(f"- Total de arquivos expostos: {exp.get('total_exposed', 0)}")

            if exp.get('critical_exposed'):
                formatted.append("- CRÍTICOS:")
                for item in exp['critical_exposed']:
                    formatted.append(f"  - {item}")

            if exp.get('warnings'):
                formatted.append(f"- Avisos: {len(exp['warnings'])} itens")

        # Cookies
        if "cookie_security" in data:
            cookies = data["cookie_security"]
            formatted.append("\n## COOKIES")
            formatted.append(f"- Status: {cookies.get('status')}")
            formatted.append(f"- Cookies analisados: {cookies.get('cookies_analyzed', 0)}")
            if cookies.get('issues'):
                for issue in cookies.get('issues', [])[:3]:  # Primeiros 3
                    formatted.append(f"  - {issue}")

        # CMS
        if "cms_detection" in data:
            cms = data["cms_detection"]
            formatted.append("\n## CMS DETECTADO")
            formatted.append(f"- Status: {cms.get('status')}")
            if cms.get('cms'):
                formatted.append(f"- CMS: {cms.get('cms')}")
                if cms.get('version'):
                    formatted.append(f"- Versão: {cms.get('version')}")

        return "\n".join(formatted)
