import json
import os
import logging
from openai import OpenAI
from typing import List, Dict, Tuple
from app.core.interfaces import LLMClient
from app.prompts.planning import (
    INITIAL_PLAN_PROMPT,
    WEIGHT_ASSIGNMENT_PROMPT,
    STEP_DECOMPOSITION_PROMPT,
    MULTIPLE_STEPS_DECOMPOSITION_PROMPT,
)

logger = logging.getLogger(__name__)


class OpenAILLMClient(LLMClient):
    """OpenAI LLM client implementation"""

    def __init__(self, api_key: str = None):
        """Initialize OpenAI client"""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key)  # Initialize client
        logger.info(f"OpenAI LLM client initialized with model: {self.model}")

    def generate_initial_plan(self, request: str) -> List[str]:
        """Generate initial plan with dynamic number of steps (5-10)"""
        logger.info(f"Generating initial plan for request: {request[:50]}...")

        prompt = INITIAL_PLAN_PROMPT.format(request=request)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional planning assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        steps_text = response.choices[0].message.content.strip()
        steps = []

        for line in steps_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split(". ", 1)
            if len(parts) > 1 and parts[0].isdigit():
                steps.append(parts[1])
            else:
                parts = line.split(" ", 1)
                if len(parts) > 1 and parts[0].strip().isdigit():
                    steps.append(parts[1])
                else:
                    steps.append(line)

        logger.info(f"Generated {len(steps)} initial plan steps")
        return steps

    def _parse_llm_json_response(self, response_text: str) -> dict:
        """Parse JSON response from LLM, handling various formats and cleanup"""
        logger.debug(f"Parsing raw response: {response_text}")

        # Remove markdown code blocks
        if "```" in response_text:
            parts = response_text.split("```")
            for part in parts:
                if "{" in part and "}" in part:
                    response_text = part
                    break

        # Remove any leading/trailing non-JSON content
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        if start_idx != -1 and end_idx != 0:
            response_text = response_text[start_idx:end_idx]

        # Clean up common formatting issues
        response_text = response_text.replace("\n", " ")
        response_text = response_text.replace("    ", " ")
        response_text = " ".join(response_text.split())

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Initial JSON parse failed: {e}")
            # Try additional cleanup
            response_text = response_text.replace("\\", "")
            response_text = response_text.replace('""', '"')
            return json.loads(response_text)

    def assign_weights(self, steps: List[str]) -> List[Tuple[str, float]]:
        """Assign weights to plan steps based on complexity"""
        logger.info(f"Assigning weights to {len(steps)} steps")

        steps_as_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        prompt = WEIGHT_ASSIGNMENT_PROMPT.format(steps=steps_as_text)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON-focused planning assistant. Always return only valid JSON without any additional text or formatting.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )

        try:
            weights_text = response.choices[0].message.content.strip()
            weights_dict = self._parse_llm_json_response(weights_text)

            weighted_steps = []
            for step in steps:
                weight = None

                # Try multiple matching strategies
                if step in weights_dict:
                    weight = weights_dict[step]
                else:
                    # Try normalized comparison
                    step_normalized = step.lower().strip()
                    for dict_key, dict_weight in weights_dict.items():
                        dict_key_normalized = dict_key.lower().strip()
                        if step_normalized == dict_key_normalized:
                            weight = dict_weight
                            break
                        # Try partial matching if exact match fails
                        elif (
                            step_normalized in dict_key_normalized
                            or dict_key_normalized in step_normalized
                        ):
                            weight = dict_weight
                            logger.debug(
                                f"Partial match found for step: {step} -> {dict_key}"
                            )
                            break

                if weight is None:
                    logger.warning(f"No weight found for step: {step}")
                    weight = 50  # Default to middle value
                elif not isinstance(weight, (int, float)) or weight < 1 or weight > 100:
                    logger.warning(f"Invalid weight value ({weight}) for step: {step}")
                    weight = 50

                weighted_steps.append((step, float(weight)))
                logger.debug(
                    f"Final weight assignment - Step: '{step}', Weight: {weight}"
                )

            return weighted_steps

        except Exception as e:
            logger.error(f"Weight assignment failed: {str(e)}")
            return [(step, 0.5) for step in steps]

    def decompose_step(self, step: str) -> List[str]:
        """Decompose a single step into sub-steps"""
        logger.info(f"Decomposing step: {step}")

        prompt = STEP_DECOMPOSITION_PROMPT.format(step=step)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional planning assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )

        steps_text = response.choices[0].message.content.strip()
        steps = []

        for line in steps_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split(". ", 1)
            if len(parts) > 1 and parts[0].isdigit():
                steps.append(parts[1])
            else:
                parts = line.split(" ", 1)
                if len(parts) > 1 and parts[0].strip().isdigit():
                    steps.append(parts[1])
                else:
                    steps.append(line)

        return steps

    def decompose_multiple_steps(self, steps: List[str]) -> Dict[str, List[str]]:
        """Decompose multiple steps at once for efficiency"""
        logger.info(f"Decomposing {len(steps)} steps at once")

        steps_as_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        prompt = MULTIPLE_STEPS_DECOMPOSITION_PROMPT.format(steps=steps_as_text)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional planning assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1000,
        )

        try:
            decomposition_text = response.choices[0].message.content.strip()
            decomposition_dict = self._parse_llm_json_response(decomposition_text)

            result = {}
            for step in steps:
                if step in decomposition_dict:
                    result[step] = decomposition_dict[step]
                else:
                    result[step] = self.decompose_step(step)

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse decomposition JSON: {e}")
            return {step: self.decompose_step(step) for step in steps}
