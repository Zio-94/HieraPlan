from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class PlanNode:
    """Plan node class representing a task in the hierarchical plan"""
    id: str
    description: str
    weight: float = 0.0
    parent_id: Optional[str] = None
    children: List['PlanNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def add_child(self, child: 'PlanNode'):
        """Add a child node to the current node"""
        self.children.append(child)
        child.parent_id = self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            'id': self.id,
            'description': self.description,
            'weight': self.weight,
            'parent_id': self.parent_id,
            'children': [child.to_dict() for child in self.children] if self.children else []
        }

@dataclass
class Plan:
    """Plan class representing the complete hierarchical plan"""
    request: str
    root_node: PlanNode
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary"""
        return {
            'request': self.request,
            'plan': self.root_node.to_dict()
        }