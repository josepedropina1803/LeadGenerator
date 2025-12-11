# src/agents/classification_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from typing import Dict, Any
from .base_agent import BaseAgent

class ClassificationAgent(BaseAgent):
    def __init__(self, temperature: float = 0.3):
        super().__init__("ClassificationAgent")
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt = PromptTemplate.from_template(
            "Agrupe as seguintes necessidades em categorias como: "
            "Infraestrutura, Segurança, Automação, Análise de Dados, "
            "Desenvolvimento, Marketing Digital, CRM, etc. "
            "Para cada categoria, liste as necessidades correspondentes.\n\n"
            "Necessidades: {necessidades}\n\n"
            "Responda no formato:\n"
            "Categoria 1: necessidade 1, necessidade 2\n"
            "Categoria 2: necessidade 3, necessidade 4"
        )
        
        self.chain = self.prompt | self.llm
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.log_action("Classificando necessidades", {"count": len(input_data.get('necessidades', []))})
            
            necessidades = input_data['necessidades']
            necessidades_str = "\n".join([f"- {n}" for n in necessidades])
            
            result = self.chain.invoke({"necessidades": necessidades_str})
            classificacao_text = result.content if hasattr(result, 'content') else str(result)
            classificacao_text = classificacao_text.strip()
            
            # Processar o texto em dicionário
            categorias = {}
            for line in classificacao_text.split('\n'):
                if ':' in line:
                    categoria, items = line.split(':', 1)
                    categoria = categoria.strip()
                    items_list = [item.strip() for item in items.split(',')]
                    categorias[categoria] = items_list
            
            self.log_action("Classificação concluída", {"categorias": list(categorias.keys())})
            
            return {"categorias": categorias}
            
        except Exception as e:
            self.logger.error(f"Erro na classificação de necessidades: {str(e)}")
            return {"categorias": {"Erro": ["Não foi possível classificar necessidades"]}, "error": str(e)}
