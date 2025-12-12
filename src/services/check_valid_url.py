


from urllib.parse import urlparse

import requests


def is_valid_url(url):
    """
    Verifica se o URL é válido e acessível
    """
    try:
        # Primeiro verificar o formato básico
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False
        
        # Verificar se é HTTP ou HTTPS
        if result.scheme not in ['http', 'https']:
            return False
            
        # Testar se o URL é acessível (com timeout curto)
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code < 400  # Considerar sucesso se < 400
        
    except requests.exceptions.RequestException:
        # Se der erro de conexão, tentar GET como fallback
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            return response.status_code < 400
        except:
            return False
    except:
        return False