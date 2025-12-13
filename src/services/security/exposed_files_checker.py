"""
Exposed Files and Directories Checker

Verifica se arquivos e diretórios sensíveis estão expostos.
"""

from typing import Dict, Any, List
from urllib.parse import urlparse
import requests


class ExposedFilesChecker:
    """Checker para arquivos e diretórios expostos"""

    # Endpoints sensíveis para verificar
    SENSITIVE_PATHS = [
        "/.git/HEAD",
        "/.git/config",
        "/.env",
        "/.env.local",
        "/.env.production",
        "/admin",
        "/admin/",
        "/wp-admin",
        "/wp-admin/",
        "/phpmyadmin",
        "/phpmyadmin/",
        "/backup.zip",
        "/backup.sql",
        "/database.sql",
        "/db.sql",
        "/.well-known/security.txt",
        "/robots.txt",
        "/sitemap.xml",
        "/api/",
        "/swagger",
        "/graphql"
    ]

    def check(self, url: str) -> Dict[str, Any]:
        """
        Verificação de arquivos e diretórios expostos

        Verifica endpoints sensíveis:
        - /.git/ (código-fonte exposto)
        - /.env (credenciais)
        - /admin, /wp-admin
        - /backup.zip, /database.sql

        Args:
            url: URL do website a verificar

        Returns:
            Dict com arquivos expostos categorizados
        """
        # Normalizar URL base
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        exposed = []
        safe = []

        for path in self.SENSITIVE_PATHS:
            try:
                test_url = base_url + path
                response = requests.head(test_url, timeout=5, allow_redirects=False)

                # Considerar exposto se retornar 200 ou 403 (existe mas bloqueado)
                if response.status_code == 200:
                    if path.startswith("/.git") or path == "/.env" or ".sql" in path or ".zip" in path:
                        exposed.append(f"🚨 CRÍTICO: {path} (HTTP {response.status_code})")
                    elif path in ["/admin", "/admin/", "/wp-admin", "/wp-admin/", "/phpmyadmin", "/phpmyadmin/"]:
                        exposed.append(f"⚠️  {path} acessível (HTTP {response.status_code})")
                    else:
                        safe.append(f"ℹ️  {path} público (esperado)")
                elif response.status_code == 403:
                    exposed.append(f"⚠️  {path} existe mas bloqueado (HTTP 403)")

            except:
                # Erro de conexão = provavelmente não existe (bom sinal)
                pass

        return {
            "exposed_files": {
                "critical_exposed": [e for e in exposed if "CRÍTICO" in e],
                "warnings": [e for e in exposed if "CRÍTICO" not in e],
                "public_files": safe,
                "total_exposed": len(exposed)
            }
        }
