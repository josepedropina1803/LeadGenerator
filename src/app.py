# src/app.py
"""
LeadGenerator - Orquestrador Principal
Camada de visualização - apenas orquestra os componentes UI
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


# Adiciona o diretório src ao path para permitir imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
    
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Imports dos módulos UI
from ui.pagesEnum import Pages
from ui.sidebar import render_sidebar

from ui.company_selector import render_company_selector
from ui.company_details import render_company_details
from ui.website_analysis.website_analysis_ui import render_website_analysis

# Configuração da página
st.set_page_config(
    page_title="LeadGenerator - AI Agents",
    page_icon="🏢",
    layout="wide"
)

# Título principal
st.title("🏢 Lead Generator")
st.markdown("---")

# Renderizar sidebar
render_sidebar()

st.markdown("""
## 🎯 **Bem-vindo ao LeadGenerator!**

Olá! É um prazer tê-lo a bordo. Deixe-me apresentar-lhe o **LeadGenerator** – o seu copiloto inteligente para análise e qualificação de leads empresariais.

### ✨ **O que fazemos por si?**

Imagine ter uma equipa de especialistas em segurança cibernética, análise de negócios e investigação digital – tudo isso automatizado e disponível 24/7. É exatamente isso que oferecemos!

### 🛫 **A sua jornada connosco tem três destinos:**

**📊 Módulo 1: Upload de Dados**
Comece por carregar o seu dataset de empresas (formato CSV ou Excel). Pense nisto como o check-in dos seus potenciais clientes. Uma vez a bordo, teremos todos os dados organizados e prontos para análise profunda.

**🧙‍♂️ Módulo 2: Análise de Websites**
Aqui é onde a magia acontece! Os nossos agentes de IA fazem uma inspeção completa do website de cada empresa:

- **🔒 Análise de Segurança Completa** – Verificamos certificados SSL, headers de segurança, vulnerabilidades, arquivos expostos, cookies, e muito mais. É como um raio-X digital que revela se o website está blindado ou vulnerável.

- **📧 Relatório de Lead Qualificado** – A nossa IA avalia o website em múltiplos critérios (design, funcionalidade, conteúdo, SEO, experiência do utilizador) e gera um relatório detalhado com pontuações de 0 a 5. Perfeito para perceber se aquela empresa está madura para o seu produto/serviço!

**🧬 Módulo 3: Análise de Redes Sociais** *(em desenvolvimento)*
Em breve, também analisaremos a presença digital nas redes sociais, completando o perfil 360º de cada lead.

### 🎁 **O que leva da viagem:**

✅ Relatórios detalhados de segurança em PDF
✅ Scores de risco e recomendações prioritizadas
✅ Análises geradas por IA em linguagem clara
✅ Visão completa sobre a maturidade digital de cada lead
✅ Insights acionáveis para a sua equipa comercial

### 🧭 **Como navegar:**

Use a **barra lateral** para alternar entre módulos. Carregue os seus dados, selecione uma empresa, e deixe os nossos agentes de IA trabalharem para si. É simples, rápido e poderoso.

**Pronto para decolar?** Comece pelo **Upload de Dados** e descubra o potencial escondido nos seus leads! 🚀

---

*Tenha uma excelente análise, e lembre-se: estamos aqui para transformar dados em decisões inteligentes.*
""")



# Rodapé
st.markdown("---")
st.markdown("🤖 Sistema de Análise de Empresas com AI Agents | Desenvolvido com Streamlit")