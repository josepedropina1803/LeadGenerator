"""
Cookie Security Checker

Verifica a segurança dos cookies HTTP.
"""

from typing import Dict, Any, List
import requests


class CookieChecker:
    """Checker para segurança de cookies"""

    def check(self, url: str) -> Dict[str, Any]:
        """
        Verificação de segurança de cookies

        Verifica:
        - Secure flag (só transmite via HTTPS)
        - HttpOnly flag (proteção XSS)
        - SameSite attribute (proteção CSRF)

        Args:
            url: URL do website a verificar

        Returns:
            Dict com análise de segurança dos cookies
        """
        try:
            response = requests.get(url, timeout=10)
            cookies = response.cookies

            if len(cookies) == 0:
                return {
                    "cookie_security": {
                        "status": "ℹ️  Nenhum cookie definido",
                        "cookies_analyzed": 0
                    }
                }

            issues = []
            cookie_details = []

            for cookie in cookies:
                cookie_info = {
                    "name": cookie.name,
                    "secure": cookie.secure,
                    "httponly": cookie.has_nonstandard_attr('HttpOnly'),
                    "samesite": cookie.get_nonstandard_attr('SameSite', 'None')
                }

                cookie_issues = []

                # Verificar Secure flag
                if not cookie.secure and url.startswith("https://"):
                    cookie_issues.append("❌ Sem flag 'Secure' (pode ser transmitido via HTTP)")

                # Verificar HttpOnly
                if not cookie.has_nonstandard_attr('HttpOnly'):
                    cookie_issues.append("❌ Sem flag 'HttpOnly' (vulnerável a XSS)")

                # Verificar SameSite
                samesite = cookie.get_nonstandard_attr('SameSite')
                if not samesite or samesite == 'None':
                    cookie_issues.append("⚠️  Sem atributo 'SameSite' (vulnerável a CSRF)")

                if cookie_issues:
                    issues.extend([f"Cookie '{cookie.name}': {issue}" for issue in cookie_issues])

                cookie_info['issues'] = cookie_issues
                cookie_details.append(cookie_info)

            return {
                "cookie_security": {
                    "status": "⚠️  Problemas detectados" if issues else "✅ Cookies seguros",
                    "cookies_analyzed": len(cookies),
                    "issues": issues,
                    "cookie_details": cookie_details
                }
            }

        except Exception as e:
            return {
                "cookie_security": {
                    "status": "❌ Erro ao analisar cookies",
                    "error": str(e)
                }
            }
