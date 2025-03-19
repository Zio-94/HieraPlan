INITIAL_PLAN_PROMPT = """
You are a planning assistant that creates step-by-step plans for tasks.
Please create a plan with 5-10 high-level steps for the following request:

{request}

Return only the numbered steps as a list, without any additional explanations or commentary.
Each step should be a short, clear phrase describing a single action or milestone.
"""

WEIGHT_ASSIGNMENT_PROMPT = """
You are a planning assistant that evaluates the complexity of tasks.
Below is a list of steps in a plan. Please assign a weight to each step based on its complexity, importance, and effort required.

Use a scale from 1 to 100, where:
- 1-30: Low complexity, straightforward tasks
- 31-70: Medium complexity, moderate effort
- 71-100: High complexity, significant effort required

Steps:
{steps}

Return ONLY a valid JSON object with the exact step descriptions as keys and weights as values.
Do not include any other text, markdown formatting, or explanations.
Example format: {{"Step 1": 75, "Step 2": 30}}
"""

STEP_DECOMPOSITION_PROMPT = """
You are a planning assistant that breaks down complex tasks into simpler steps.
Please decompose the following step into 2-3 smaller, more specific sub-steps:

Step: {step}

Return only the numbered sub-steps as a list, without any additional explanations or commentary.
Each sub-step should be a short, clear phrase describing a single action or milestone.
"""

MULTIPLE_STEPS_DECOMPOSITION_PROMPT = """
You are a planning assistant that breaks down complex tasks into simpler steps.
Please decompose each of the following steps into 2-3 smaller, more specific sub-steps:

Steps:
{steps}

Return the results as a JSON object where keys are the original steps and values are arrays of sub-steps.
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