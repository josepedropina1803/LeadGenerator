from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from typing import Dict, Any

import requests
from .base_agent import BaseAgent


class SecurityAgent(BaseAgent):
    """
    
    Agente que verifica a segurança de websites apenas através do url
    
    1. check_ssl 

    2. check_headers

    3. check_vulnerabilities


    
    """

    def __init__(self):
        super().__init__("SecurityAgent")

        

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:

        

        """ 

        1. Vai ler o input_data de 2 formas: 
            - url
            - tipo de security check que vai ser feito
        
        2. dependendo do tipo vai chamar a função correspondente.

        """

        try:
            url = input_data["url"]
            check_type = input_data["check_type"]

            if check_type == "ssl":
                return self._check_ssl(url)
            elif check_type == "headers":
                return self._check_headers(url)
            elif check_type == "vulnerabilities":
                return self._check_vulnerabilities(url)
            else:
                return self._check_general(url)
        except Exception as e:
            self.logger.error(f"Erro na verificação de segurança: {str(e)}")
            return {"error": str(e)}
        
    def _check_ssl(self, url: str) -> Dict[str, Any]:
        self.log_action("Verificação de SSL", {"url": url})
        """
        
        Verificação SSL/TLS
        
        """
        try:
            response = requests.get(url, timeout=10)

            ssl_info = {
                "status": "✅ SSL Válido",
                "protocol": "TLS/HTTPS",
            }

            if hasattr(response, 'cert'):
                ssl_info["cert_info"] = response.cert

            self.log_action("Verificação de SSL concluída", {"status": "válido"})

            return {"ssl": ssl_info}    
        except requests.exceptions.SSLError as e:
            self.log_action("Erro de SSL detetado", {"error", str(e)})
            return {"ssl": {"status": "❌ Erro de SSL", "details": str(e)}}
        except Exception as e:
            return {"ssl": {"status": "❌ Erro ao verificar SSL", "details": str(e)}}
    
    def _check_headers(self, url:str) -> Dict[str,Any]:
        """

        Verificação de headers de segurança

        1. Verifica se na resposta dada pelo servidor vem com os requests supostos

        
        """
        self.log_action("Verificação de headers", {"url": url})

        try:
            response = requests.head(url, timeout=10)
            headers = response.headers

            required_headers = {
                "Content-Security-Policy": "Protege contra XSS",
                "X-Frame-Options": "Protege contra Clickjacking",
                "X-Content-Type-Options": "Protege contra MIME sniffing",
                "Strict-Transport-Security": "Força HTTPS",
            }

            headers_check = {}
            missing = {}

            for header, description in required_headers.items():
                if header in headers:
                    headers_check[header] = f"✅ Presente: {headers[header]}"
                else:
                    headers_check[header] = "❌ Ausente"
            
            self.log_action("Verificação de headers concluída", {
                "present": len(headers_check) - len(missing),
                "missing": len(missing)
            })
            return {"headers": headers_check}
        
        except Exception as e:
            return {"headers": {str(e)}}
        
    def _check_vulnerabilities(self, url:str) -> Dict[str, Any]:
        """
        
        Verificação de vulnerabilidades comuns

        1.Cookies sem HttpOnly
        2.Sem HSTS
        3.Sem CSP
        4.Server header exposto
        5.X-Powered-By exposto

        """
        self.log_action("Verificação de vulnerabilidades", {"url": url})
        
        vulnerabilities = []
        
        try:
            response = requests.get(url, timeout=10)
            headers = response.headers
            cookies = response.cookies
            
            
            for cookie in cookies:
                if 'HttpOnly' not in str(cookie):
                    vulnerabilities.append("⚠️  Cookie sem flag HttpOnly")
            
            
            if "Strict-Transport-Security" not in headers:
                vulnerabilities.append("⚠️  Sem HSTS header (man-in-the-middle risk)")
            
            
            if "Content-Security-Policy" not in headers:
                vulnerabilities.append("⚠️  Sem Content-Security-Policy (XSS risk)")
            
            
            if "Server" in headers:
                vulnerabilities.append(f"⚠️  Server header exposto: {headers['Server']}")
            
           
            if "X-Powered-By" in headers:
                vulnerabilities.append(f"⚠️  X-Powered-By exposto: {headers['X-Powered-By']}")
            
            self.log_action("Verificação de vulnerabilidades concluída", {
                "count": len(vulnerabilities)
            })
            
            return {"vulnerabilities": vulnerabilities}
        except Exception as e:
            return {"vulnerabilities": [f"Erro ao verificar: {str(e)}"]}

    def _check_general(self, url: str) -> Dict[str, Any]:
        self.log_action("Verificação Geral de Segurança", {"url": url})
        """
            Verificação Geral de Segurança

            1. ver se usa o protocolo de encriptação , certificado SSL 
            2. Analisar os tempos de resposta e métricas de requests ao servidor

        """
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)

            issues = []

            if url.startswith("http://"):
                issues.append("❌ Usa HTTP em vez de HTTPS")
            else:
                issues.append("✅ Usa HTTPS")

            if response.status_code >= 300 and response.status_code < 400:
                issues.append(f"⚠️  Redireciona com status {response.status_code}")
            
            self.log_action("Verificação Geral Concluída", {"issues_count": len(issues)})

            return {"issues": issues}

        except requests.exceptions.Timeout:
            return {"issues": ["❌ Website não responde (timeout)"]}
        except requests.exceptions.ConnectionError:
            return {"issues": ["❌ Não conseguiu conectar ao website"]}
        except Exception as e:
            return {"issues": [f"❌ Erro ao verificar: {str(e)}"]}



