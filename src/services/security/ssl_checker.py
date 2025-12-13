"""
SSL/TLS Security Checker

Verifica certificados SSL e configurações TLS de websites.
"""

from typing import Dict, Any
import requests
from services.check_ssl_certificate import CheckSSL


class SSLChecker:
    """Checker para verificações SSL/TLS"""

    def check(self, url: str) -> Dict[str, Any]:
        """
        Verificação SSL/TLS Básica

        Args:
            url: URL do website a verificar

        Returns:
            Dict com status SSL básico
        """
        try:
            # Verificar se o URL original é HTTP ou HTTPS
            original_is_http = url.startswith("http://")

            # Seguir redirects para verificar o SSL do destino final
            response = requests.get(url, timeout=10, allow_redirects=True)

            # Se chegou aqui sem erro de SSL, o certificado é válido
            ssl_info = {
                "status": "✅ SSL Válido" if response.url.startswith("https://") else "❌ Sem SSL",
                "protocol": "TLS/HTTPS" if response.url.startswith("https://") else "HTTP",
            }

            # Adicionar informação sobre redirect se aplicável
            if original_is_http and response.url.startswith("https://"):
                ssl_info["note"] = "URL original HTTP redirecionou para HTTPS"

            if hasattr(response, 'cert'):
                ssl_info["cert_info"] = response.cert

            return {"ssl": ssl_info}
        except requests.exceptions.SSLError as e:
            return {"ssl": {"status": "❌ Erro de SSL", "details": str(e)}}
        except Exception as e:
            return {"ssl": {"status": "❌ Erro ao verificar SSL", "details": str(e)}}

    def check_advanced(self, url: str) -> Dict[str, Any]:
        """
        Verificação SSL/TLS Avançada

        Verifica:
        1. Expiração do certificado
        2. Versão TLS
        3. Emissor (CA)
        4. Dias restantes até expiração

        Args:
            url: URL do website a verificar

        Returns:
            Dict com análise SSL avançada
        """
        try:
            # Usar a classe CheckSSL existente
            ssl_result = CheckSSL.verifica_ssl(url)

            if not ssl_result.get('valido'):
                return {
                    "ssl_advanced": {
                        "status": "❌ Certificado Inválido",
                        "error": ssl_result.get('erro', 'Erro desconhecido'),
                        "details": ssl_result.get('detalhes', '')
                    }
                }

            # Processar informações do certificado
            dias_restantes = ssl_result.get('dias_restantes')
            emissor = ssl_result.get('emissor', {})
            protocolo = ssl_result.get('protocolo_ssl', 'Desconhecido')

            issues = []
            warnings = []

            # Verificar expiração
            if dias_restantes is not None:
                if dias_restantes < 0:
                    issues.append(f"❌ Certificado EXPIRADO há {abs(dias_restantes)} dias")
                elif dias_restantes <= 7:
                    issues.append(f"🚨 CRÍTICO: Expira em {dias_restantes} dias")
                elif dias_restantes <= 30:
                    warnings.append(f"⚠️  Expira em breve: {dias_restantes} dias")
                else:
                    warnings.append(f"✅ Válido por {dias_restantes} dias")

            # Verificar versão TLS
            if protocolo:
                if 'TLSv1.3' in protocolo:
                    warnings.append("✅ TLS 1.3 (mais seguro)")
                elif 'TLSv1.2' in protocolo:
                    warnings.append("✅ TLS 1.2 (seguro)")
                elif 'TLSv1.1' in protocolo or 'TLSv1.0' in protocolo:
                    issues.append(f"❌ {protocolo} - versão obsoleta e insegura")
                elif 'SSLv' in protocolo:
                    issues.append(f"❌ {protocolo} - EXTREMAMENTE INSEGURO")

            # Informações do emissor
            ca_name = emissor.get('organizationName', 'Desconhecido')

            return {
                "ssl_advanced": {
                    "status": "✅ Análise Completa" if not issues else "⚠️  Problemas Detectados",
                    "dias_restantes": dias_restantes,
                    "valido_ate": ssl_result.get('valido_ate'),
                    "protocolo": protocolo,
                    "emissor": ca_name,
                    "issues": issues,
                    "info": warnings
                }
            }

        except Exception as e:
            return {
                "ssl_advanced": {
                    "status": "❌ Erro na análise",
                    "error": str(e)
                }
            }
