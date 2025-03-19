from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from .models import Plan

class LLMClient(ABC):
    """LLM client interface"""
    
    @abstractmethod
    def generate_initial_plan(self, request: str) -> List[str]:
        """Generate initial plan steps"""
        pass
    
    @abstractmethod
    def assign_weights(self, steps: List[str]) -> List[Tuple[str, float]]:
        """Assign weights to plan steps"""
        pass
    
    @abstractmethod
    def decompose_step(self, step: str) -> List[str]:
        """Decompose a single step"""
        pass
    
    @abstractmethod
    def decompose_multiple_steps(self, steps: List[str]) -> Dict[str, List[str]]:
        """Decompose multiple steps at once"""
        pass

class PlanningStrategy(ABC):
    """Planning strategy interface"""
    
    @abstractmethod
    def create_plan(self, request: str) -> Plan:
        """Create a plan for the given request"""
        pass
    
    @abstractmethod
    def decompose_plan(self, plan: Plan, weight_threshold: float, max_depth: int) -> Plan:
        """Decompose the plan based on weight threshold and max depth"""
        pass