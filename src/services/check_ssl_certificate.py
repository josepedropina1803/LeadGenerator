


import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse

class CheckSSL:
    
    @staticmethod
    def verifica_ssl(url, timeout=5):
        """
        Verifica o certificado SSL de um site através da URL.
        
        Args:
            url (str): URL do site (pode incluir http://, https:// ou apenas o domínio)
            timeout (int): Timeout em segundos para a conexão
            
        Returns:
            dict: Dicionário com informações do certificado SSL ou erro
        """
        try:
            # Parse da URL para extrair o hostname
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed_url = urlparse(url)
            hostname = parsed_url.netloc or parsed_url.path
            
            # Remove porta se existir
            if ':' in hostname:
                hostname = hostname.split(':')[0]
            
            # Criar contexto SSL
            context = ssl.create_default_context()
            
            # Conectar ao servidor
            with socket.create_connection((hostname, 443), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Obter informações do certificado
                    cert = ssock.getpeercert()
                    
                    # Processar informações
                    result = {
                        'valido': True,
                        'hostname': hostname,
                        'emissor': dict(x[0] for x in cert['issuer']),
                        'assunto': dict(x[0] for x in cert['subject']),
                        'versao': cert['version'],
                        'serial_number': cert['serialNumber'],
                        'valido_de': cert['notBefore'],
                        'valido_ate': cert['notAfter'],
                        'dias_restantes': CheckSSL._calcular_dias_restantes(cert['notAfter']),
                        'san': cert.get('subjectAltName', []),
                        'protocolo_ssl': ssock.version()
                    }
                    
                    return result
                    
        except ssl.SSLCertVerificationError as e:
            return {
                'valido': False,
                'erro': 'Certificado SSL inválido',
                'detalhes': str(e)
            }
        except socket.gaierror:
            return {
                'valido': False,
                'erro': 'Não foi possível resolver o hostname',
                'hostname': hostname
            }
        except socket.timeout:
            return {
                'valido': False,
                'erro': 'Timeout na conexão',
                'hostname': hostname
            }
        except Exception as e:
            return {
                'valido': False,
                'erro': 'Erro ao verificar SSL',
                'detalhes': str(e)
            }
    
    @staticmethod
    def _calcular_dias_restantes(data_expiracao):
        """Calcula quantos dias faltam até o certificado expirar"""
        try:
            # Formato: 'Jan 1 12:00:00 2025 GMT'
            data_exp = datetime.strptime(data_expiracao, '%b %d %H:%M:%S %Y %Z')
            dias = (data_exp - datetime.now()).days
            return dias
        except:
            return None
    
    @staticmethod
    def verificar_expiracao(url, dias_aviso=30):
        """
        Verifica se o certificado está próximo de expirar
        
        Args:
            url (str): URL do site
            dias_aviso (int): Número de dias para considerar como aviso
            
        Returns:
            dict: Status de expiração
        """
        info = CheckSSL.verifica_ssl(url)
        
        if not info['valido']:
            return info
        
        dias_restantes = info['dias_restantes']
        
        if dias_restantes is None:
            return {'aviso': 'Não foi possível calcular dias restantes'}
        elif dias_restantes < 0:
            return {'aviso': 'EXPIRADO', 'dias': dias_restantes}
        elif dias_restantes <= dias_aviso:
            return {'aviso': f'EXPIRA EM BREVE ({dias_restantes} dias)', 'dias': dias_restantes}
        else:
            return {'aviso': 'OK', 'dias': dias_restantes}