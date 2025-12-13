"""
CMS (Content Management System) Detector

Detecta qual CMS está sendo utilizado pelo website.
"""

from typing import Dict, Any, Optional, List
import requests
import re


class CMSDetector:
    """Detector de CMS"""

    def detect(self, url: str) -> Dict[str, Any]:
        """
        Detecção de CMS (Content Management System)

        Detecta:
        - WordPress
        - Joomla
        - Drupal
        - Shopify
        - Wix
        - Magento

        Args:
            url: URL do website a verificar

        Returns:
            Dict com CMS detectado e informações adicionais
        """
        try:
            response = requests.get(url, timeout=10)
            html_content = response.text.lower()
            headers = response.headers

            cms_detected = None
            version = None
            indicators = []

            # WordPress
            if 'wp-content' in html_content or 'wp-includes' in html_content:
                cms_detected = "WordPress"
                indicators.append("wp-content/ ou wp-includes/ detectado")

                # Tentar detectar versão
                version_match = re.search(r'wp-includes.*?ver=([0-9.]+)', html_content)
                if version_match:
                    version = version_match.group(1)

            # Joomla
            elif 'joomla' in html_content or '/components/com_' in html_content:
                cms_detected = "Joomla"
                indicators.append("Componentes Joomla detectados")

            # Drupal
            elif 'drupal' in html_content or 'sites/default/files' in html_content:
                cms_detected = "Drupal"
                indicators.append("Estrutura Drupal detectada")

            # Shopify
            elif 'shopify' in html_content or 'cdn.shopify.com' in html_content:
                cms_detected = "Shopify"
                indicators.append("CDN Shopify detectado")

            # Wix
            elif 'wix.com' in html_content or 'x-wix' in str(headers).lower():
                cms_detected = "Wix"
                indicators.append("Plataforma Wix detectada")

            # Magento
            elif 'magento' in html_content or 'mage/cookies.js' in html_content:
                cms_detected = "Magento"
                indicators.append("Magento detectado")

            if cms_detected:
                warnings = self._get_cms_warnings(cms_detected, version)

                return {
                    "cms_detection": {
                        "status": f"✅ CMS Detectado: {cms_detected}",
                        "cms": cms_detected,
                        "version": version,
                        "indicators": indicators,
                        "warnings": warnings
                    }
                }
            else:
                return {
                    "cms_detection": {
                        "status": "ℹ️  Nenhum CMS conhecido detectado",
                        "cms": None
                    }
                }

        except Exception as e:
            return {
                "cms_detection": {
                    "status": "❌ Erro ao detectar CMS",
                    "error": str(e)
                }
            }

    def _get_cms_warnings(self, cms: str, version: Optional[str]) -> List[str]:
        """
        Retorna avisos específicos para cada CMS

        Args:
            cms: Nome do CMS detectado
            version: Versão do CMS (se detectada)

        Returns:
            Lista de avisos
        """
        warnings = []

        if cms == "WordPress":
            warnings.append("⚠️  WordPress: Verificar se plugins estão atualizados")
            warnings.append("⚠️  WordPress: Esconder versão (security through obscurity)")
            if version:
                warnings.append(f"ℹ️  Versão detectada: {version}")

        return warnings
