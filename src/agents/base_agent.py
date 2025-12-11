from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa os dados e retorna resultado"""
        pass
    
    def log_action(self, action: str, data: Dict[str, Any] = None):
        self.logger.info(f"{self.name}: {action} - {data or ''}")