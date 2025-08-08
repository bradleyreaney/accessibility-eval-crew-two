"""
Pydantic models for data validation and structure
References: Master Plan - Data Models section
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List
from enum import Enum
from datetime import datetime


class PlanType(str, Enum):
    """Enumeration of available remediation plan types"""

    PLAN_A = "PlanA"
    PLAN_B = "PlanB"
    PLAN_C = "PlanC"
    PLAN_D = "PlanD"
    PLAN_E = "PlanE"
    PLAN_F = "PlanF"
    PLAN_G = "PlanG"


class DocumentContent(BaseModel):
    """Structured representation of parsed document content"""

    title: str
    content: str
    page_count: int
    metadata: Dict[str, str]


class EvaluationCriteria(BaseModel):
    """Evaluation criteria from promt/eval-prompt.md"""

    strategic_prioritization_weight: float = 0.40
    technical_specificity_weight: float = 0.30
    comprehensiveness_weight: float = 0.20
    long_term_vision_weight: float = 0.10

    @field_validator(
        "strategic_prioritization_weight",
        "technical_specificity_weight",
        "comprehensiveness_weight",
        "long_term_vision_weight",
    )
    @classmethod
    def weights_valid_range(cls, v):
        """Ensure weights are between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError("Weights must be between 0 and 1")
        return v

    def validate_weights_sum(self):
        """Ensure all weights sum to 1.0"""
        total = (
            self.strategic_prioritization_weight
            + self.technical_specificity_weight
            + self.comprehensiveness_weight
            + self.long_term_vision_weight
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Evaluation weights must sum to 1.0, got {total}")


class EvaluationInput(BaseModel):
    """Input data for evaluation process"""

    audit_report: DocumentContent
    remediation_plans: Dict[str, DocumentContent]
    evaluation_criteria: EvaluationCriteria = EvaluationCriteria()

    @field_validator("remediation_plans")
    @classmethod
    def validate_plan_names(cls, v):
        """Ensure plan names follow expected format"""
        valid_names = [plan.value for plan in PlanType]
        for plan_name in v.keys():
            if plan_name not in valid_names:
                raise ValueError(f"Invalid plan name: {plan_name}")
        return v


class JudgmentScore(BaseModel):
    """Individual criterion score from a judge"""

    criterion: str
    score: float = Field(..., ge=0.0, le=10.0)
    rationale: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class PlanEvaluation(BaseModel):
    """Complete evaluation of a single plan by one judge"""

    plan_name: str
    judge_id: str  # "gemini" or "gpt4"
    scores: List[JudgmentScore]
    overall_score: float = Field(..., ge=0.0, le=10.0)
    detailed_analysis: str
    pros: List[str]
    cons: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
