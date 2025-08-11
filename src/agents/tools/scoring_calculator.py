"""
Scoring calculator tool for weighted evaluation calculations.
References: Master Plan - Scoring System, Phase 2 - Tool Implementation
"""

import logging
from typing import Any, Dict, List, Optional

from crewai_tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ScoringInput(BaseModel):
    """Input model for scoring calculator tool"""

    criterion_scores: Dict[str, float] = Field(
        description="Dict of criterion name to score (1-10)"
    )
    criteria_weights: Dict[str, float] = Field(
        description="Dict of criterion name to weight (0-1)"
    )
    plan_name: str = Field(description="Name of the plan being scored")


class ScoringCalculatorTool(BaseTool):
    """
    Tool for calculating weighted scores and comparative analysis.

    This tool handles:
    - Weighted score calculations
    - Score normalization
    - Comparative ranking
    - Statistical analysis
    """

    name: str = "scoring_calculator"
    description: str = """
    Calculate weighted scores for remediation plans using evaluation criteria.
    Provides statistical analysis and comparative rankings.
    """
    args_schema: type[BaseModel] = ScoringInput

    def __init__(self):
        """
        Initialize the Scoring Calculator Tool.

        Sets up the tool for calculating weighted scores and performing
        statistical analysis on remediation plan evaluations.
        """
        super().__init__(
            name="scoring_calculator",
            description="""Calculate weighted scores for remediation plans using evaluation criteria.
            Provides statistical analysis and comparative rankings.""",
        )

    def _run(
        self,
        criterion_scores: Dict[str, float],
        criteria_weights: Dict[str, float],
        plan_name: str,
    ) -> str:
        """
        Calculate weighted score for a plan.

        Args:
            criterion_scores: Dict of criterion name to score (1-10)
            criteria_weights: Dict of criterion name to weight (0-1)
            plan_name: Name of the plan being scored

        Returns:
            Formatted scoring analysis
        """
        try:
            logger.info(f"Calculating weighted score for {plan_name}")

            # Validate inputs
            if not criterion_scores or not criteria_weights:
                return "Error: Missing scores or weights for calculation"

            # Calculate weighted score
            weighted_score = self._calculate_weighted_score(
                criterion_scores, criteria_weights
            )

            # Generate detailed analysis
            analysis = self._generate_scoring_analysis(
                criterion_scores, criteria_weights, weighted_score, plan_name
            )

            return analysis

        except Exception as e:
            logger.error(f"Scoring calculation failed for {plan_name}: {e}")
            return f"Error: Failed to calculate score for {plan_name}: {str(e)}"

    def _calculate_weighted_score(
        self, scores: Dict[str, float], weights: Dict[str, float]
    ) -> float:
        """Calculate the weighted average score"""
        total_weighted_score = 0.0
        total_weight = 0.0

        for criterion, score in scores.items():
            if criterion in weights:
                weight = weights[criterion]
                total_weighted_score += score * weight
                total_weight += weight

        # Normalize if weights don't sum to 1.0
        if total_weight > 0:
            return (
                total_weighted_score / total_weight
                if total_weight != 1.0
                else total_weighted_score
            )
        return 0.0

    def _generate_scoring_analysis(
        self,
        scores: Dict[str, float],
        weights: Dict[str, float],
        weighted_score: float,
        plan_name: str,
    ) -> str:
        """Generate detailed scoring analysis"""

        analysis_lines = [
            f"SCORING ANALYSIS - {plan_name}",
            "=" * 40,
            f"Overall Weighted Score: {weighted_score:.2f}/10",
            "",
            "Detailed Breakdown:",
        ]

        # Add individual criterion analysis
        for criterion, score in scores.items():
            if criterion in weights:
                weight = weights[criterion]
                weighted_contribution = score * weight
                analysis_lines.append(
                    f"  {criterion}: {score:.1f}/10 (weight: {weight:.1%}) = {weighted_contribution:.2f}"
                )

        # Add performance assessment
        performance_level = self._assess_performance_level(weighted_score)
        analysis_lines.extend(
            [
                "",
                f"Performance Level: {performance_level}",
                "",
                "Score Interpretation:",
                "  9-10: Exceptional",
                "  7-8:  Strong",
                "  5-6:  Adequate",
                "  3-4:  Needs Improvement",
                "  1-2:  Poor",
            ]
        )

        return "\n".join(analysis_lines)

    def _assess_performance_level(self, score: float) -> str:
        """Assess performance level based on score"""
        if score >= 9.0:
            return "Exceptional"
        elif score >= 7.0:
            return "Strong"
        elif score >= 5.0:
            return "Adequate"
        elif score >= 3.0:
            return "Needs Improvement"
        else:
            return "Poor"

    def calculate_comparative_rankings(self, plan_scores: Dict[str, float]) -> str:
        """Calculate rankings across multiple plans"""
        if not plan_scores:
            return "No scores provided for ranking"

        # Sort plans by score (descending)
        ranked_plans = sorted(plan_scores.items(), key=lambda x: x[1], reverse=True)

        ranking_lines = ["COMPARATIVE RANKINGS", "=" * 30]

        for rank, (plan_name, score) in enumerate(ranked_plans, 1):
            ranking_lines.append(f"{rank}. {plan_name}: {score:.2f}/10")

        return "\n".join(ranking_lines)
