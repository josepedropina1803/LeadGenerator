# src/agents/needs_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from typing import Dict, Any
from .base_agent import BaseAgent

class NeedsAgent(BaseAgent):
    def __init__(self, temperature: float = 0.4):
        super().__init__("NeedsAgent")
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt = PromptTemplate.from_template(
            "Com base na descrição: '{descricao}' e setor: '{setor}', "
            "liste as 4-5 principais necessidades de sistema ou tecnologia que essa empresa pode ter. "
            "Seja específico e objetivo. Retorne apenas a lista numerada."
        )
        
        self.chain = self.prompt | self.llm
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.log_action("Identificando necessidades", {
                "setor": input_data.get('setor', ''),
                "descricao": input_data.get('descricao', '')[:50] + "..."
            })
            
            descricao = input_data['descricao']
            setor = input_data['setor']
            
            result = self.chain.invoke({
                "descricao": descricao,
                "setor": setor
            })
            
            # Processar a lista numerada
            necessidades_text = result.content if hasattr(result, 'content') else str(result)
            necessidades_text = necessidades_text.strip()
            necessidades = [line.strip() for line in necessidades_text.split('\n') if line.strip()]
            # Remover números iniciais se existirem
            necessidades = [n.split('. ', 1)[1] if '. ' in n else n for n in necessidades]
            
            self.log_action("Necessidades identificadas", {"count": len(necessidades)})
            
            return {"necessidades": necessidades}
            
        except Exception as e:
            self.logger.error(f"Erro na identificação de necessidades: {str(e)}")
            return {"necessidades": ["Não foi possível identificar necessidades"], "error": str(e)}
