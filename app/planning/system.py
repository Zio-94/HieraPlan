import json
import logging
from app.core.interfaces import PlanningStrategy
from app.core.models import Plan, PlanNode

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

        def _generate_complexity_bar(weight: float) -> str:
            """Generate a visual complexity indicator"""
            level = int(weight / 10)

            # Determine difficulty level and emoji
            if level <= 2:
                return "  (Easy 🌱)"
            elif level <= 4:
                return "  (Moderate 🌟)"
            elif level <= 7:
                return "  (Challenging 🔥)"
            else:
                return "  (Intense 🚀)"

        def _add_node_to_md(node: PlanNode, depth: int, parent_num: str = "") -> str:
            node_md = ""

            if depth == 0:
                # Skip root node
                for i, child in enumerate(node.children, 1):
                    # Top-level nodes use h2 heading
                    node_md += f"### **{i}. {child.description}** {_generate_complexity_bar(child.weight)}\n\n"

                    # Add children with proper numbering
                    if child.children:
                        for j, grandchild in enumerate(child.children, 1):
                            child_num = f"{i}.{j}"
                            node_md += (
                                f"- [ ] **{child_num}. {grandchild.description}**\n"
                            )
                            node_md += (
                                f"  {_generate_complexity_bar(grandchild.weight)}\n"
                            )

                            # Add third level children if they exist
                            if grandchild.children:
                                for k, great_grandchild in enumerate(
                                    grandchild.children, 1
                                ):
                                    grand_child_num = f"{i}.{j}.{k}"
                                    node_md += f"    - [ ] **{grand_child_num}. {great_grandchild.description}**\n"
                                    node_md += f"        {_generate_complexity_bar(great_grandchild.weight)}\n"

                            node_md += "\n"

                    # Add horizontal line between top-level tasks
                    if i < len(node.children):
                        node_md += "---\n\n"
                return node_md

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
