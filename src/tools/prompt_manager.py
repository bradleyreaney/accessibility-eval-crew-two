"""
Manages integration with existing evaluation framework
References: Master Plan - Integration with Existing Evaluation Framework
"""

from pathlib import Path
from typing import Dict, List
import re
import logging

logger = logging.getLogger(__name__)


class PromptManager:
    """
    Integrates with existing promt/eval-prompt.md framework
    Handles dynamic content injection and prompt preparation
    """

    def __init__(self, prompt_path: Path):
        """
        Initialize the prompt manager with evaluation framework.

        Args:
            prompt_path: Path to the evaluation prompt markdown file
        """
        self.prompt_path = prompt_path
        self.base_prompt = self._load_evaluation_framework()

    def _load_evaluation_framework(self) -> str:
        """Load the master evaluation prompt from promt/eval-prompt.md"""
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.info(f"Loaded evaluation framework: {len(content)} characters")
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Evaluation prompt not found: {self.prompt_path}")
        except Exception as e:
            raise ValueError(f"Failed to load evaluation prompt: {e}")

    def prepare_judge_prompt(
        self, audit_report: str, remediation_plans: Dict[str, str]
    ) -> str:
        """
        Inject audit report and remediation plans into evaluation framework

        Args:
            audit_report: Full text of accessibility audit
            remediation_plans: Dict of plan_name -> plan_content

        Returns:
            Complete evaluation prompt ready for LLM
        """
        prompt = self.base_prompt

        # Inject audit report
        audit_marker = "### CONTEXT: ACCESSIBILITY AUDIT FINDINGS"
        if audit_marker in prompt:
            prompt = prompt.replace(audit_marker, f"{audit_marker}\n\n{audit_report}")

        # Inject remediation plans
        for plan_name, plan_content in remediation_plans.items():
            # Find the plan section (e.g., "#### Plan A:")
            pattern = f"#### {plan_name}:"
            if pattern in prompt:
                prompt = prompt.replace(pattern, f"#### {plan_name}:\n\n{plan_content}")

        return prompt

    def validate_prompt_structure(self) -> List[str]:
        """
        Validate that the evaluation prompt has required sections
        Returns list of any missing sections
        """
        required_sections = [
            "### PERSONA",
            "### CORE TASK",
            "### CONTEXT: ACCESSIBILITY AUDIT FINDINGS",
            "### CANDIDATE REMEDIATION PLANS",
            "### EVALUATION FRAMEWORK & OUTPUT STRUCTURE",
        ]

        missing_sections = []
        for section in required_sections:
            if section not in self.base_prompt:
                missing_sections.append(section)

        if missing_sections:
            logger.warning(f"Missing required sections: {missing_sections}")

        return missing_sections

    def extract_evaluation_criteria(self) -> Dict[str, float]:
        """
        Extract evaluation criteria and their weights from the prompt.
        Returns dictionary of criterion -> weight
        """
        criteria = {}

        # Pattern 1: Numbered format like "**(1) Strategic Prioritization (Weight: 40%):**"
        pattern1 = r"\*\*\([0-9]+\)\s*([^(]+?)\s*\(Weight:\s*(\d+)%\):\*\*"
        matches1 = re.findall(pattern1, self.base_prompt)
        for criterion, weight_str in matches1:
            criterion_clean = criterion.strip()
            weight = float(weight_str) / 100.0
            criteria[criterion_clean] = weight

        # Pattern 2: Bullet format like "*   **Strategic Prioritization (Weight: 40%)**:"
        pattern2 = r"\*\s+\*\*([^(]+?)\s*\(Weight:\s*(\d+)%\)\*\*:"
        matches2 = re.findall(pattern2, self.base_prompt)
        for criterion, weight_str in matches2:
            criterion_clean = criterion.strip()
            weight = float(weight_str) / 100.0
            criteria[criterion_clean] = weight

        # Pattern 3: Simple format like "**Strategic Prioritization (Weight: 40%):**"
        pattern3 = r"\*\*([^(]+?)\s*\(Weight:\s*(\d+)%\):\*\*"
        matches3 = re.findall(pattern3, self.base_prompt)
        for criterion, weight_str in matches3:
            criterion_clean = criterion.strip()
            weight = float(weight_str) / 100.0
            criteria[criterion_clean] = weight

        # If no weighted criteria found, try alternative patterns
        if not criteria:
            logger.warning(
                "No weighted criteria found in prompt, trying alternative patterns"
            )
            # Try simpler pattern
            alt_pattern = r"(\d+)%.*?([A-Z][^:]+):"
            alt_matches = re.findall(alt_pattern, self.base_prompt)
            for weight_str, criterion in alt_matches:
                criterion_clean = criterion.strip()
                weight = float(weight_str) / 100.0
                criteria[criterion_clean] = weight

        logger.info(f"Extracted evaluation criteria: {criteria}")
        return criteria

    def get_plan_sections(self) -> List[str]:
        """Extract plan section headers from the prompt"""
        # Try both formats: "Plan A" and "PlanA"
        plan_pattern = r"#### (Plan[A-G]|Plan [A-G]):"
        plans = re.findall(plan_pattern, self.base_prompt)
        logger.info(f"Found plan sections: {plans}")
        return plans

    def get_prompt_length(self) -> int:
        """Get the length of the base prompt"""
        return len(self.base_prompt)

    def get_prompt_preview(self, max_chars: int = 500) -> str:
        """Get a preview of the prompt for debugging"""
        if len(self.base_prompt) <= max_chars:
            return self.base_prompt
        return self.base_prompt[:max_chars] + "..."
