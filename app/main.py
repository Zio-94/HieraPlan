import os
import logging
from dotenv import load_dotenv
from app.llm.openai_client import OpenAILLMClient  # Changed to absolute import
from app.planning.htn import HTNPlanningStrategy  # Changed to absolute import
from app.planning.system import PlanningSystem  # Changed to absolute import

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    # Create LLM client
    llm_client = OpenAILLMClient(api_key=os.environ.get("OPENAI_API_KEY"))

    # Create planning strategy
    planning_strategy = HTNPlanningStrategy(
        llm_client=llm_client, weight_threshold=70, max_depth=2
    )

    # Create planning system
    planning_system = PlanningSystem(planning_strategy=planning_strategy)

    # Get user input
    prompt = input("Enter your prompt: ")
    if not prompt.strip():
        logger.warning("Empty prompt provided.")
        return

    # Process request
    plan = planning_system.process_request(prompt)

    # Export plan
    plan_md = planning_system.export_plan(plan, format="md")
    print(plan_md)

    # Save plan to file
    with open("hierarchical_plan.md", "w") as f:
        f.write(plan_md)

    logger.info("Plan exported to hierarchical_plan.md")


if __name__ == "__main__":
    main()
