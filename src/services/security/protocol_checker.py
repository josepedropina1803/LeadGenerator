"""
Protocol Security Checker

Verifica o uso de HTTP vs HTTPS e redirects.
"""

from typing import Dict, Any
import requests


class ProtocolChecker:
    """Checker para protocolo HTTP/HTTPS"""

    def check(self, url: str) -> Dict[str, Any]:
        """
        Verificação Geral de Segurança

        Verifica:
        1. Uso de protocolo de encriptação (HTTP vs HTTPS)
        2. Redirects automáticos HTTP → HTTPS

        Args:
            url: URL do website a verificar

        Returns:
            Dict com issues de protocolo
        """
        try:
            # Fazer request SEM seguir redirects primeiro
            response = requests.head(url, timeout=10, allow_redirects=False)

            issues = []
            original_is_http = url.startswith("http://")

            # Verificar se houve redirect
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_location = response.headers.get('Location', '')

                if original_is_http and redirect_location.startswith("https://"):
                    issues.append("⚠️  Aceita HTTP mas redireciona para HTTPS (melhor: só aceitar HTTPS)")
                elif original_is_http:
                    issues.append("❌ Usa HTTP sem redirecionamento para HTTPS")
                else:
                    issues.append(f"⚠️  Redireciona com status {response.status_code}")
            else:
                # Sem redirect
                if original_is_http:
                    issues.append("❌ Usa HTTP em vez de HTTPS")
                else:
                    issues.append("✅ Usa HTTPS")

            return {"issues": issues}

        except requests.exceptions.Timeout:
            return {"issues": ["❌ Website não responde (timeout)"]}
        except requests.exceptions.ConnectionError:
            return {"issues": ["❌ Não conseguiu conectar ao website"]}
        except Exception as e:
            return {"issues": [f"❌ Erro ao verificar: {str(e)}"]}
