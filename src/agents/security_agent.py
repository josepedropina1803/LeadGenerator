"""
Security Agent

Agente responsável por orquestrar todas as verificações de segurança.
Delega trabalho para checkers especializados.
"""

from typing import Dict, Any
from .base_agent import BaseAgent
from services.security import (
    SSLChecker,
    HeadersChecker,
    VulnerabilityChecker,
    ExposedFilesChecker,
    CookieChecker,
    CMSDetector,
    ProtocolChecker
)


class SecurityAgent(BaseAgent):
    """
    Agente que verifica a segurança de websites através do URL.

    Este agente orquestra diferentes checkers especializados:
    1. ProtocolChecker - HTTP vs HTTPS, redirects
    2. SSLChecker - Certificados SSL/TLS
    3. HeadersChecker - Headers de segurança
    4. VulnerabilityChecker - Vulnerabilidades comuns
    5. ExposedFilesChecker - Arquivos/diretórios expostos
    6. CookieChecker - Segurança de cookies
    7. CMSDetector - Detecção de CMS
    """

    def __init__(self):
        super().__init__("SecurityAgent")

        # Inicializar todos os checkers
        self.ssl_checker = SSLChecker()
        self.headers_checker = HeadersChecker()
        self.vulnerability_checker = VulnerabilityChecker()
        self.exposed_files_checker = ExposedFilesChecker()
        self.cookie_checker = CookieChecker()
        self.cms_detector = CMSDetector()
        self.protocol_checker = ProtocolChecker()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma verificação de segurança.

        Args:
            input_data: Dict contendo:
                - url: URL do website
                - check_type: Tipo de verificação a realizar

        Returns:
            Dict com resultados da verificação
        """
        try:
            url = input_data["url"]
            check_type = input_data["check_type"]

            # Mapeamento de check_type para método do checker apropriado
            checkers = {
                "ssl": lambda u: self._run_checker("ssl", self.ssl_checker.check, u),
                "ssl_advanced": lambda u: self._run_checker("ssl_advanced", self.ssl_checker.check_advanced, u),
                "headers": lambda u: self._run_checker("headers", self.headers_checker.check, u),
                "vulnerabilities": lambda u: self._run_checker("vulnerabilities", self.vulnerability_checker.check, u),
                "exposed_files": lambda u: self._run_checker("exposed_files", self.exposed_files_checker.check, u),
                "cookie_security": lambda u: self._run_checker("cookie_security", self.cookie_checker.check, u),
                "cms_detection": lambda u: self._run_checker("cms_detection", self.cms_detector.detect, u),
                "general": lambda u: self._run_checker("general", self.protocol_checker.check, u)
            }

            # Executar o checker apropriado
            checker_fn = checkers.get(check_type, checkers["general"])
            return checker_fn(url)

        except Exception as e:
            self.logger.error(f"Erro na verificação de segurança: {str(e)}")
            return {"error": str(e)}

    def _run_checker(self, check_name: str, checker_fn, url: str) -> Dict[str, Any]:
        """
        Executa um checker com logging.

        Args:
            check_name: Nome da verificação
            checker_fn: Função do checker a executar
            url: URL a verificar

        Returns:
            Resultado da verificação
        """
        self.log_action(f"Iniciando verificação: {check_name}", {"url": url})

        try:
            result = checker_fn(url)
            self.log_action(f"Verificação {check_name} concluída", {"status": "sucesso"})
            return result
        except Exception as e:
            self.log_action(f"Erro em {check_name}", {"error": str(e)})
            return {"error": str(e)}
