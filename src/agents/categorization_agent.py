from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from typing import Dict, Any
from .base_agent import BaseAgent
from domain.models import CategoriasValidas

class CategorizationAgent(BaseAgent):
    def __init__(self, temperature: float = 0.1):
        super().__init__("CategorizationAgent")

        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        categorias_formatadas = "\n".join([f"- {cat.value}" for cat in CategoriasValidas])

        self.prompt = PromptTemplate.from_template(
            "Com base na descrição: '{descricao}', classifique esta empresa "
            "em UM dos seguintes setores EXATOS: \n"
            "{categorias}\n\n"
            "INSTRUÇÕES:\n"
            "1. Escolha APENAS um setor da lista\n"
            "2. Responda com o NOME EXATO do setor\n"
            "3. Se não se encaixar, escolha 'Outros'\n\n"
            "Setor escolhido:"
        )

        self.chain = self.prompt.partial(categorias=categorias_formatadas) | self.llm

    def _normalizar_categoria(self, categoria_sugerida: str) -> str:
        """Normaliza categoria usando enum"""
        if not categoria_sugerida:
            return CategoriasValidas.OUTROS.value
            
        categoria_sugerida = categoria_sugerida.strip()

        
        for categoria in CategoriasValidas:
            if categoria.value.lower() == categoria_sugerida.lower():
                return categoria.value
            
       
        categoria_lower = categoria_sugerida.lower()
        for categoria in CategoriasValidas:
            if (categoria_lower in categoria.value.lower() or 
                categoria.value.lower() in categoria_lower):
                return categoria.value
                
        return CategoriasValidas.OUTROS.value
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            descricao = input_data.get('descricao', "")
            
            
            if descricao is None:
                descricao = ""
            
            
            if descricao and len(descricao) > 100:
                descricao_preview = descricao[:100] + "..."
            else:
                descricao_preview = descricao or "Descrição vazia"
            
            self.log_action("Processando a categorização", {
                "descricao_preview": descricao_preview
            })

            if not descricao:
                return {"setor": CategoriasValidas.OUTROS.value, "error": "Descrição ausente"}
                
            result = self.chain.invoke({
                "descricao": descricao,
            })
            
            
            if hasattr(result, 'content'):
                result_text = result.content
            elif hasattr(result, 'text'):
                result_text = result.text
            else:
                result_text = str(result)
                
            setor_sugerido = result_text.strip() if result_text else ""

            setor_final = self._normalizar_categoria(setor_sugerido)

            self.log_action("Categorização Concluída", {
                "setor_sugerido": setor_sugerido,
                "setor_final": setor_final
            })

            return {"setor": setor_final}

        except Exception as e:
            self.logger.error(f"Erro na categorização: {str(e)}")
            return {"setor": CategoriasValidas.OUTROS.value, "error": str(e)}

def categorizar_empresa(descricao: str) -> str:
    """Agente real de categorização"""
    agent = CategorizationAgent()
    print(f"Tipo da descrição: {type(descricao)}")
    print(f"Conteúdo da descrição: {repr(descricao)}")  # ✅ Melhor debug
    result = agent.process({"descricao": descricao})
    return result.get("setor", "Não identificado")
