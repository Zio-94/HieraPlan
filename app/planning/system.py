import json
import logging
from ..core.interfaces import PlanningStrategy
from ..core.models import Plan, PlanNode

logger = logging.getLogger(__name__)


class PlanningSystem:
    """Planning system class"""

    def __init__(self, planning_strategy: PlanningStrategy):
        """Initialize planning system"""
        self.planning_strategy = planning_strategy
        logger.info("Planning system initialized")

    def process_request(
        self, request: str, weight_threshold: float = None, max_depth: int = None
    ) -> Plan:
        """Process a request and generate a hierarchical plan"""
        logger.info(f"Processing request: {request[:50]}...")

        # Create initial plan
        plan = self.planning_strategy.create_plan(request)

        # Decompose plan
        decomposed_plan = self.planning_strategy.decompose_plan(
            plan, weight_threshold, max_depth
        )

        return decomposed_plan

    def export_plan(self, plan: Plan, format: str = "json") -> str:
        """Export plan in the specified format"""
        if format == "json":
            return json.dumps(plan.to_dict(), indent=2)
        elif format == "md":
            return self._generate_markdown(plan)
        elif format == "txt":
            return self._generate_text(plan)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown(self, plan: Plan) -> str:
        """Generate markdown representation of the plan"""
        md = f"# Hierarchical Plan for: {plan.request}\n\n"

        def _add_node_to_md(node: PlanNode, depth: int, parent_num: str = "") -> str:
            node_md = ""

            if depth == 0:
                # Skip root node
                for i, child in enumerate(node.children, 1):
                    node_md += _add_node_to_md(child, depth + 1, str(i))
                return node_md

            # Create indentation
            indent = "    " * (depth - 1)

            # Create step number and bullet point
            step_num = f"{parent_num}. " if parent_num else ""

            # Add current node with indentation
            node_md += (
                f"{indent}- {step_num}{node.description} (Complexity: {node.weight}%)\n"
            )

            # Add children with proper numbering
            for i, child in enumerate(node.children, 1):
                child_num = f"{parent_num}.{i}" if parent_num else str(i)
                node_md += _add_node_to_md(child, depth + 1, child_num)

            return node_md

        md += _add_node_to_md(plan.root_node, 0)
        return md

    def _generate_text(self, plan: Plan) -> str:
        """Generate text representation of the plan"""
        text = f"HIERARCHICAL PLAN FOR: {plan.request}\n\n"

        def _add_node_to_text(node: PlanNode, depth: int) -> str:
            node_text = ""
            indent = "  " * depth

            if depth == 0:
                # Skip root node
                for child in node.children:
                    node_text += _add_node_to_text(child, depth + 1)
                return node_text

            node_text += f"{indent}- {node.description} (Weight: {node.weight:.2f})\n"

            if node.children:
                for child in node.children:
                    node_text += _add_node_to_text(child, depth + 1)

            return node_text

        text += _add_node_to_text(plan.root_node, 0)
        return text
