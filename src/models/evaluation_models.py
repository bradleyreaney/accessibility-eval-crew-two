"""
Pydantic models for data validation and structure
References: Master Plan - Data Models section
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


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


class EvaluationStatus(str, Enum):
    """Status of an evaluation result"""

    COMPLETED = "completed"
    NA = "NA"  # Not Available
    FAILED = "failed"


class EvaluationResult(BaseModel):
    """Enhanced evaluation result with availability tracking"""

    plan_name: str
    evaluator: str
    evaluation_content: Optional[str] = None
    status: EvaluationStatus = EvaluationStatus.COMPLETED
    na_reason: Optional[str] = None
    llm_used: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    overall_score: Optional[float] = None
    criteria_scores: Optional[Dict[str, float]] = None
    analysis: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None


class PartialEvaluationSummary(BaseModel):
    """Summary of partial evaluation results"""

    total_plans: int
    completed_evaluations: int
    na_evaluations: int
    failed_evaluations: int
    available_llms: List[str]
    unavailable_llms: List[str]
    completion_percentage: float
    evaluation_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )


class LLMAvailabilityStatus(BaseModel):
    """LLM availability status information"""

    llm_type: str
    available: bool
    last_check: str
    failure_count: int = 0
    last_failure_reason: Optional[str] = None


class ResilienceInfo(BaseModel):
    """Information about resilience handling during evaluation"""

    partial_evaluation: bool
    available_llms: List[str]
    unavailable_llms: List[str]
    na_evaluations_count: int
    completion_percentage: float
    resilience_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
