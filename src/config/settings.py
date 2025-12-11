# Responsabilidade: Configurações da aplicação
# - Variáveis de ambiente (API keys, URLs)
# - Configurações de modelos (temperatura, tokens)
# - Validação de configurações
# - Valores padrão
# Exemplo:
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    model_temperature: float = 0.7
    max_retries: int = 3
