# src/agents/website_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from typing import Dict, Any
from .base_agent import BaseAgent

class WebsiteAgent(BaseAgent):
    def __init__(self, temperature: float = 0.3):
        super().__init__("WebsiteAgent")
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt = PromptTemplate.from_template(
            """Com base no website '{url}', faça uma avaliação detalhada considerando os seguintes critérios.
            
IMPORTANTE: Cada critério deve ser avaliado numa escala de 0 a 5, onde:
- 0 = Muito Fraco
- 1-2 = Insuficiente  
- 3 = Satisfatório
- 4 = Bom
- 5 = Excelente

Formate a resposta da seguinte maneira para CADA critério:

1. Design: [NOTA]/5
[Explicação detalhada sobre o design, incluindo pontos positivos e negativos]

2. Funcionalidade: [NOTA]/5
[Explicação detalhada sobre a funcionalidade, incluindo pontos positivos e negativos]

3. Acessibilidade: [NOTA]/5
[Explicação detalhada sobre a acessibilidade, incluindo pontos positivos e negativos]

4. Responsivo: [NOTA]/5
[Explicação detalhada sobre a responsividade, incluindo pontos positivos e negativos]

5. Segurança: [NOTA]/5
[Explicação detalhada sobre a segurança, incluindo pontos positivos e negativos]

6. Chatbot: [SIM/NÃO]
[Se houver chatbot, descreva sua implementação e qualidade]

Seja objetivo, crítico e honesto na avaliação. Não hesite em apontar problemas e áreas que precisam de melhoria."""
        )
        
        self.chain = self.prompt | self.llm
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.log_action("Avaliando website", {"url": input_data.get('url', '')})
            
            url = input_data['url']
            result = self.chain.invoke({"url": url})
            avaliacao = result.content if hasattr(result, 'content') else str(result)
            avaliacao = avaliacao.strip()
            
            self.log_action("Avaliação concluída")
            
            return {"avaliacao": avaliacao}
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação do website: {str(e)}")
            return {"avaliacao": "Não foi possível avaliar o website", "error": str(e)}