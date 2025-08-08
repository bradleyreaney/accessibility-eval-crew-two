"""
Evaluation framework tool for accessibility remediation plan assessment.
References: Master Plan - Evaluation Framework, promt/eval-prompt.md
"""

import logging
from pathlib import Path
from typing import Dict, List, Any
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

from ...models.evaluation_models import EvaluationCriteria, DocumentContent
from ...tools.prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class EvaluationFrameworkInput(BaseModel):
    """Input model for evaluation framework tool"""
    plan_name: str = Field(description="Name of the remediation plan")
    plan_content: str = Field(description="Full text content of the plan")
    audit_context: str = Field(description="Original accessibility audit report")


class EvaluationFrameworkTool(BaseTool):
    """
    Tool for applying the standardized evaluation framework to remediation plans.
    
    This tool implements the evaluation criteria from promt/eval-prompt.md:
    - Strategic Prioritization (40%)
    - Technical Specificity (30%) 
    - Comprehensiveness (20%)
    - Long-term Vision (10%)
    """
    
    name: str = "evaluation_framework"
    description: str = """
    Apply the standardized evaluation framework to assess a remediation plan.
    This tool evaluates plans against the 4 weighted criteria established in 
    the evaluation framework and provides structured scoring.
    """
    args_schema: type[BaseModel] = EvaluationFrameworkInput
    
    def __init__(self):
        super().__init__(
            name="evaluation_framework",
            description="""Apply the standardized evaluation framework to assess a remediation plan.
            This tool evaluates plans against the 4 weighted criteria established in 
            the evaluation framework and provides structured scoring."""
        )
        # Get the path to the evaluation prompt
        prompt_path = Path(__file__).parent.parent.parent.parent / "promt" / "eval-prompt.md"
        # Store everything as private attributes to avoid Pydantic field issues
        self.__prompt_manager = PromptManager(prompt_path)
        self.__criteria_weights = self._load_evaluation_framework()
    
    def _load_evaluation_framework(self) -> Dict[str, float]:
        """Load the evaluation framework from promt/eval-prompt.md"""
        try:
            criteria_weights = self.__prompt_manager.extract_evaluation_criteria()
            logger.info(f"Loaded evaluation framework with {len(criteria_weights)} criteria")
            return criteria_weights
        except Exception as e:
            logger.error(f"Failed to load evaluation framework: {e}")
            # Provide fallback criteria if loading fails
            fallback_criteria = {
                'Strategic Prioritization': 0.4,
                'Technical Specificity': 0.3,
                'Comprehensiveness': 0.2,
                'Long-term Vision': 0.1
            }
            logger.warning("Using fallback evaluation criteria")
            return fallback_criteria
    
    @property
    def criteria_weights(self) -> Dict[str, float]:
        """Get the evaluation criteria weights"""
        return self.__criteria_weights
    
    def _run(self, plan_name: str, plan_content: str, audit_context: str) -> str:
        """
        Apply evaluation framework to a remediation plan.
        
        Args:
            plan_name: Name of the plan (e.g., "PlanA")
            plan_content: Full text content of the remediation plan
            audit_context: Original accessibility audit report
            
        Returns:
            Structured evaluation results as formatted string
        """
        try:
            logger.info(f"Evaluating {plan_name} using standardized framework")
            
            # Create evaluation context
            evaluation_context = {
                "plan_name": plan_name,
                "plan_content": plan_content,
                "audit_context": audit_context,
                "criteria": self.criteria_weights
            }
            
            # Generate structured evaluation prompt
            evaluation_prompt = self._build_evaluation_prompt(evaluation_context)
            
            # Return the evaluation structure for the agent to process
            return evaluation_prompt
            
        except Exception as e:
            logger.error(f"Evaluation framework failed for {plan_name}: {e}")
            return f"Error: Failed to apply evaluation framework to {plan_name}: {str(e)}"
    
    def _build_evaluation_prompt(self, context: Dict[str, Any]) -> str:
        """Build structured evaluation prompt for the agent"""
        
        criteria_text = "\n".join([
            f"- {criterion_name} ({weight*100:.0f}%)"
            for criterion_name, weight in context["criteria"].items()
        ])
        
        prompt = f"""
EVALUATION FRAMEWORK ASSESSMENT

Plan: {context['plan_name']}

EVALUATION CRITERIA (apply each with specified weight):
{criteria_text}

ORIGINAL AUDIT CONTEXT:
{context['audit_context'][:2000]}...

PLAN TO EVALUATE:
{context['plan_content'][:3000]}...

REQUIRED OUTPUT FORMAT:
For each criterion, provide:
1. Score (1-10 scale)
2. Detailed reasoning (2-3 sentences)
3. Specific evidence from the plan
4. Areas for improvement

Calculate weighted final score and provide overall assessment.
"""
        return prompt
    
    def get_criteria_weights(self) -> Dict[str, float]:
        """Get the evaluation criteria weights for scoring calculations"""
        return self.__criteria_weights
