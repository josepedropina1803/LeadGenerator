"""
HTTP Security Headers Checker

Verifica a presença de headers de segurança importantes.
"""

from typing import Dict, Any
import requests


class HeadersChecker:
    """Checker para headers de segurança HTTP"""

    def check(self, url: str) -> Dict[str, Any]:
        """
        Verificação de headers de segurança

        Verifica se a resposta do servidor contém headers de segurança importantes:
        - Content-Security-Policy (proteção XSS)
        - X-Frame-Options (proteção clickjacking)
        - X-Content-Type-Options (proteção MIME sniffing)
        - Strict-Transport-Security (força HTTPS)

        Args:
            url: URL do website a verificar

        Returns:
            Dict com status dos headers
        """
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

            for header, description in required_headers.items():
                if header in headers:
                    headers_check[header] = f"✅ Presente: {headers[header]}"
                else:
                    headers_check[header] = "❌ Ausente"

            return {"headers": headers_check}

        except Exception as e:
            return {"headers": {str(e)}}
