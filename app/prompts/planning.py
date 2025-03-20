# INITIAL_PLAN_PROMPT = """
# You are a planning assistant that creates step-by-step plans for tasks.
# Please create a plan with 5-10 high-level steps for the following request:

# {request}

# Respond in the same language as the request.
# Return only the numbered steps as a list, without any additional explanations or commentary.
# Each step should be a short, clear phrase describing a single action or milestone.
# """
INITIAL_PLAN_PROMPT = """
You are an expert planning strategist. For this request, create 5-10 strategic steps:
{request}
Include:

Measurable milestones
Dependencies between steps
Balanced short/long-term actions
Critical path elements
Logical sequence

Respond in the request's language.
Return only numbered steps without explanations.
Make each step concise yet descriptive (what + why).
"""

WEIGHT_ASSIGNMENT_PROMPT = """
You are a planning assistant that evaluates task complexity for average human intelligence. Assign weights (1-100) to each step based on:

1. Technical Complexity (40%): expertise required, components involved, technical risks
2. Execution Effort (30%): time, resources, sub-tasks
3. Dependencies (30%): external dependencies, prerequisites, bottlenecks

Scale for average human:
- 1-30: Low (routine tasks most people can do)
- 31-70: Medium (challenges requiring some training)
- 71-90: High (specialized knowledge needed)
- 91-100: Extreme (beyond average human capability, like solving Riemann Hypothesis)

Steps:
{steps}

Return ONLY a JSON object with the exact step descriptions as keys and weights as values.
Example: {{"Create system architecture": 75, "Setup basic configuration": 30}}
"""

STEP_DECOMPOSITION_PROMPT = """
Break down this complex task into 2-3 simpler, more manageable sub-steps:

Step: {step}

Respond in the same language as the step.
Guidelines:
- Each sub-step should be significantly simpler than the original
- Sub-steps should be concrete, actionable items
- Avoid creating sub-steps that still require complex decision-making
- Ensure sub-steps collectively cover the entire original task

Return only numbered sub-steps as a list, without explanations.
"""


MULTIPLE_STEPS_DECOMPOSITION_PROMPT = """
Break down this complex task into 2-3 simpler, more manageable sub-steps:

Steps: {steps}

Respond in the same language as the steps.
Guidelines:
- Each sub-step should be significantly simpler than the original
- Sub-steps should be concrete, actionable items
- Avoid creating sub-steps that still require complex decision-making
- Ensure sub-steps collectively cover the entire original task

For example:
{{
  "Design system architecture": [
    "Define system components",
    "Create component interaction diagram",
    "Document data flow",
    "Establish technical constraints"
  ]
}}
"""
