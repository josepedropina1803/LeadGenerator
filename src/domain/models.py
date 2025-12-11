# Responsabilidade: Modelos de dados Pydantic
# - Definição de estruturas de dados
# - Validação automática
# - Serialização/deserialização
# - Tipagem estática
from enum import Enum


class CategoriasValidas(Enum):
    TECNOLOGIA = "Tecnologia"
    SAUDE = "Saúde" 
    VAREJO = "Varejo"
    EDUCACAO = "Educação"
    FINANCEIRO = "Financeiro"
    INDUSTRIA = "Indústria"
    SERVICOS = "Serviços"
    AGRONEGOCIO = "Agronegócio"
    CONSTRUCAO = "Construção"
    TRANSPORTE = "Transporte"
    ENERGIA = "Energia"
    TELECOMUNICACOES = "Telecomunicações"
    MIDIA = "Mídia"
    TURISMO = "Turismo"
    AUTOMOTIVO = "Automotivo"
    ALIMENTICIO = "Alimentício"
    MODA = "Moda"
    IMOBILIARIO = "Imobiliário"
    LOGISTICA = "Logística"
    SEGUROS = "Seguros"
    OUTROS = "Outros"