import logging
from typing import List
from app.core.interfaces import PlanningStrategy, LLMClient
from app.core.models import Plan, PlanNode

logger = logging.getLogger(__name__)


class HTNPlanningStrategy(PlanningStrategy):
    """HTN (Hierarchical Task Network) planning strategy implementation"""

    def __init__(
        self, llm_client: LLMClient, weight_threshold: float = 70, max_depth: int = 3
    ):
        """Initialize HTN planning strategy"""
        self.llm_client = llm_client
        self.weight_threshold = weight_threshold
        self.max_depth = max_depth
        logger.info(
            f"HTN planning strategy initialized (weight threshold: {weight_threshold}, max depth: {max_depth})"
        )

    def create_plan(self, request: str) -> Plan:
        """Create a plan for the given request"""
        logger.info(f"Creating plan for request: {request[:50]}...")

        # Generate initial plan
        initial_steps = self.llm_client.generate_initial_plan(request)

        # Assign weights
        weighted_steps = self.llm_client.assign_weights(initial_steps)

        # Create root node
        root_node = PlanNode(id="root", description="Root Plan")

        # Create and connect step nodes
        for i, (step, weight) in enumerate(weighted_steps):
            step_node = PlanNode(id=f"step_{i}", description=step, weight=weight)
            root_node.add_child(step_node)

        return Plan(request=request, root_node=root_node)

    def decompose_plan(
        self, plan: Plan, weight_threshold: float = None, max_depth: int = None
    ) -> Plan:
        """Decompose the plan based on weight threshold and max depth"""
        if weight_threshold is None:
            weight_threshold = self.weight_threshold
        if max_depth is None:
            max_depth = self.max_depth

        logger.info(
            f"Decomposing plan (weight threshold: {weight_threshold}, max depth: {max_depth})"
        )

        for current_depth in range(max_depth):
            nodes_to_decompose = self._identify_nodes_at_depth(
                plan.root_node, weight_threshold, current_depth
            )

            if not nodes_to_decompose:
                logger.info(f"No nodes to decompose at depth {current_depth}")
                continue

            steps_to_decompose = [node.description for node in nodes_to_decompose]
            logger.info(
                f"Decomposing {len(steps_to_decompose)} nodes at depth {current_depth}"
            )

            decomposed_steps = self.llm_client.decompose_multiple_steps(
                steps_to_decompose
            )

            for node in nodes_to_decompose:
                if node.description in decomposed_steps:
                    sub_steps = decomposed_steps[node.description]
                    weighted_sub_steps = self.llm_client.assign_weights(sub_steps)

                    for i, (sub_step, weight) in enumerate(weighted_sub_steps):
                        sub_node = PlanNode(
                            id=f"{node.id}_sub_{i}", description=sub_step, weight=weight
                        )
                        node.add_child(sub_node)

        return plan

    def _identify_nodes_at_depth(
        self,
        node: PlanNode,
        weight_threshold: float,
        target_depth: int,
        current_depth: int = 0,
    ) -> List[PlanNode]:
        """특정 깊이에서 분해가 필요한 노드 식별"""
        if current_depth > target_depth:
            return []

        nodes_to_decompose = []

        if current_depth == target_depth:
            if node.weight > weight_threshold and not node.children:
                nodes_to_decompose.append(node)
            return nodes_to_decompose

        for child in node.children:
            nodes_to_decompose.extend(
                self._identify_nodes_at_depth(
                    child, weight_threshold, target_depth, current_depth + 1
                )
            )

        return nodes_to_decompose
