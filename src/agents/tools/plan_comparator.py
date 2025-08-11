"""
Plan comparator tool for head-to-head analysis of remediation plans.
References: Master Plan - Comparative Analysis, Phase 2 - Multi-Plan Evaluation
"""

import logging
from typing import Any, Dict, List, Tuple

from crewai_tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ComparisonInput(BaseModel):
    """Input model for plan comparison tool"""

    plan_a_name: str = Field(description="Name of first plan")
    plan_a_content: str = Field(description="Content of first plan")
    plan_b_name: str = Field(description="Name of second plan")
    plan_b_content: str = Field(description="Content of second plan")
    comparison_criteria: List[str] = Field(description="Criteria for comparison")


class PlanComparatorTool(BaseTool):
    """
    Tool for comparative analysis between remediation plans.

    This tool provides:
    - Head-to-head comparisons
    - Strengths and weaknesses analysis
    - Recommendation synthesis
    - Approach differentiation
    """

    name: str = "plan_comparator"
    description: str = """
    Perform detailed head-to-head comparison between remediation plans.
    Analyzes strengths, weaknesses, and strategic differences.
    """
    args_schema: type[BaseModel] = ComparisonInput

    def __init__(self):
        super().__init__(
            name="plan_comparator",
            description="""Perform detailed head-to-head comparison between remediation plans.
            Analyzes strengths, weaknesses, and strategic differences.""",
        )

        # Comparison dimensions for analysis - use object.__setattr__ to bypass Pydantic
        object.__setattr__(
            self,
            "comparison_dimensions",
            {
                "scope": [
                    "comprehensive",
                    "scope",
                    "coverage",
                    "breadth",
                    "wide",
                    "narrow",
                ],
                "depth": [
                    "detailed",
                    "specific",
                    "depth",
                    "thorough",
                    "surface",
                    "deep",
                ],
                "priority": ["priority", "critical", "important", "urgent", "sequence"],
                "timeline": ["timeline", "schedule", "phase", "milestone", "deadline"],
                "resources": ["resource", "cost", "effort", "team", "budget"],
                "methodology": [
                    "approach",
                    "method",
                    "strategy",
                    "technique",
                    "framework",
                ],
                "testing": ["test", "validate", "verify", "check", "audit"],
                "maintenance": [
                    "maintain",
                    "monitor",
                    "ongoing",
                    "continuous",
                    "sustain",
                ],
            },
        )

    def _run(
        self,
        plan_a_name: str,
        plan_a_content: str,
        plan_b_name: str,
        plan_b_content: str,
        comparison_criteria: List[str],
    ) -> str:
        """
        Compare two remediation plans across multiple dimensions.

        Args:
            plan_a_name: Name of first plan
            plan_a_content: Content of first plan
            plan_b_name: Name of second plan
            plan_b_content: Content of second plan
            comparison_criteria: Criteria for comparison

        Returns:
            Detailed comparative analysis
        """
        try:
            logger.info(f"Comparing {plan_a_name} vs {plan_b_name}")

            # Analyze each plan's characteristics
            plan_a_analysis = self._analyze_plan_characteristics(plan_a_content)
            plan_b_analysis = self._analyze_plan_characteristics(plan_b_content)

            # Perform dimensional comparison
            dimensional_comparison = self._compare_dimensions(
                plan_a_content, plan_b_content, plan_a_name, plan_b_name
            )

            # Identify unique strengths
            unique_strengths = self._identify_unique_strengths(
                plan_a_content, plan_b_content, plan_a_name, plan_b_name
            )

            # Generate comprehensive comparison report
            comparison_report = self._generate_comparison_report(
                plan_a_name,
                plan_b_name,
                plan_a_analysis,
                plan_b_analysis,
                dimensional_comparison,
                unique_strengths,
            )

            return comparison_report

        except Exception as e:
            logger.error(f"Plan comparison failed: {e}")
            return f"Error: Failed to compare {plan_a_name} vs {plan_b_name}: {str(e)}"

    def _analyze_plan_characteristics(self, plan_content: str) -> Dict[str, Any]:
        """Analyze key characteristics of a plan"""
        content_lower = plan_content.lower()

        characteristics = {
            "length": len(plan_content),
            "structure_indicators": 0,
            "technical_depth": 0,
            "strategic_elements": 0,
            "timeline_mentions": 0,
            "testing_focus": 0,
        }

        # Structure indicators
        structure_words = ["section", "phase", "step", "stage", "part", "component"]
        characteristics["structure_indicators"] = sum(
            content_lower.count(word) for word in structure_words
        )

        # Technical depth
        technical_words = [
            "implement",
            "code",
            "development",
            "technical",
            "specific",
            "detailed",
        ]
        characteristics["technical_depth"] = sum(
            content_lower.count(word) for word in technical_words
        )

        # Strategic elements
        strategic_words = [
            "strategy",
            "approach",
            "methodology",
            "framework",
            "philosophy",
        ]
        characteristics["strategic_elements"] = sum(
            content_lower.count(word) for word in strategic_words
        )

        # Timeline mentions
        timeline_words = [
            "timeline",
            "schedule",
            "deadline",
            "milestone",
            "phase",
            "week",
            "month",
        ]
        characteristics["timeline_mentions"] = sum(
            content_lower.count(word) for word in timeline_words
        )

        # Testing focus
        testing_words = ["test", "validate", "verify", "check", "audit", "review"]
        characteristics["testing_focus"] = sum(
            content_lower.count(word) for word in testing_words
        )

        return characteristics

    def _compare_dimensions(
        self, plan_a: str, plan_b: str, name_a: str, name_b: str
    ) -> Dict[str, Dict[str, Any]]:
        """Compare plans across different dimensions"""
        comparison = {}

        for dimension, keywords in self.comparison_dimensions.items():
            plan_a_score = sum(plan_a.lower().count(keyword) for keyword in keywords)
            plan_b_score = sum(plan_b.lower().count(keyword) for keyword in keywords)

            # Determine advantage
            if plan_a_score > plan_b_score:
                advantage = name_a
                difference = plan_a_score - plan_b_score
            elif plan_b_score > plan_a_score:
                advantage = name_b
                difference = plan_b_score - plan_a_score
            else:
                advantage = "Equal"
                difference = 0

            comparison[dimension] = {
                f"{name_a}_score": plan_a_score,
                f"{name_b}_score": plan_b_score,
                "advantage": advantage,
                "difference": difference,
            }

        return comparison

    def _identify_unique_strengths(
        self, plan_a: str, plan_b: str, name_a: str, name_b: str
    ) -> Dict[str, List[str]]:
        """Identify unique strengths of each plan"""
        strengths: Dict[str, List[str]] = {name_a: [], name_b: []}

        # Define strength indicators
        strength_patterns = {
            "Comprehensive Coverage": [
                "comprehensive",
                "complete",
                "thorough",
                "extensive",
            ],
            "Technical Specificity": ["specific", "detailed", "precise", "exact"],
            "Clear Timeline": ["schedule", "timeline", "milestone", "deadline"],
            "Resource Planning": ["resource", "team", "cost", "budget"],
            "Quality Assurance": ["test", "validate", "review", "audit"],
            "User-Centered": ["user", "accessibility", "usability", "experience"],
            "Maintenance Focus": ["maintain", "monitor", "ongoing", "sustain"],
            "Risk Management": ["risk", "challenge", "mitigation", "contingency"],
        }

        plan_a_lower = plan_a.lower()
        plan_b_lower = plan_b.lower()

        for strength, keywords in strength_patterns.items():
            plan_a_mentions = sum(plan_a_lower.count(keyword) for keyword in keywords)
            plan_b_mentions = sum(plan_b_lower.count(keyword) for keyword in keywords)

            # Assign strength if one plan significantly outperforms
            if plan_a_mentions > plan_b_mentions * 1.5:  # 50% more mentions
                strengths[name_a].append(strength)
            elif plan_b_mentions > plan_a_mentions * 1.5:
                strengths[name_b].append(strength)

        return strengths

    def _generate_comparison_report(
        self,
        name_a: str,
        name_b: str,
        analysis_a: Dict[str, Any],
        analysis_b: Dict[str, Any],
        dimensional_comparison: Dict[str, Dict[str, Any]],
        unique_strengths: Dict[str, List[str]],
    ) -> str:
        """Generate comprehensive comparison report"""

        report_lines = [
            f"COMPARATIVE ANALYSIS: {name_a} vs {name_b}",
            "=" * 60,
            "",
            "OVERVIEW COMPARISON:",
            f"  {name_a} Length: {analysis_a['length']:,} characters",
            f"  {name_b} Length: {analysis_b['length']:,} characters",
            f"  Structure: {name_a} ({analysis_a['structure_indicators']}) vs {name_b} ({analysis_b['structure_indicators']})",
            f"  Technical Depth: {name_a} ({analysis_a['technical_depth']}) vs {name_b} ({analysis_b['technical_depth']})",
            "",
        ]

        # Add dimensional analysis
        report_lines.extend(["DIMENSIONAL COMPARISON:", "📊 Advantage by dimension:"])

        for dimension, data in dimensional_comparison.items():
            advantage = data["advantage"]
            difference = data["difference"]
            if advantage != "Equal":
                report_lines.append(
                    f"  {dimension.title()}: {advantage} (+{difference})"
                )
            else:
                report_lines.append(f"  {dimension.title()}: Equal coverage")

        report_lines.append("")

        # Add unique strengths
        report_lines.extend(["UNIQUE STRENGTHS:", f"🎯 {name_a} excels in:"])

        if unique_strengths[name_a]:
            for strength in unique_strengths[name_a]:
                report_lines.append(f"  • {strength}")
        else:
            report_lines.append("  • No significant unique advantages identified")

        report_lines.extend(["", f"🎯 {name_b} excels in:"])

        if unique_strengths[name_b]:
            for strength in unique_strengths[name_b]:
                report_lines.append(f"  • {strength}")
        else:
            report_lines.append("  • No significant unique advantages identified")

        # Add strategic recommendations
        recommendations = self._generate_strategic_recommendations(
            name_a, name_b, analysis_a, analysis_b, dimensional_comparison
        )

        if recommendations:
            report_lines.extend(
                [
                    "",
                    "STRATEGIC RECOMMENDATIONS:",
                    "💡 Key insights for decision making:",
                ]
            )
            for rec in recommendations:
                report_lines.append(f"  • {rec}")

        return "\n".join(report_lines)

    def _generate_strategic_recommendations(
        self,
        name_a: str,
        name_b: str,
        analysis_a: Dict[str, Any],
        analysis_b: Dict[str, Any],
        dimensional_comparison: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        """Generate strategic recommendations based on comparison"""
        recommendations = []

        # Length-based recommendations
        if analysis_a["length"] > analysis_b["length"] * 1.5:
            recommendations.append(
                f"{name_a} provides more comprehensive coverage but may be resource-intensive"
            )
        elif analysis_b["length"] > analysis_a["length"] * 1.5:
            recommendations.append(
                f"{name_b} provides more comprehensive coverage but may be resource-intensive"
            )

        # Technical depth recommendations
        if analysis_a["technical_depth"] > analysis_b["technical_depth"] * 2:
            recommendations.append(
                f"{name_a} offers superior technical specificity for complex implementations"
            )
        elif analysis_b["technical_depth"] > analysis_a["technical_depth"] * 2:
            recommendations.append(
                f"{name_b} offers superior technical specificity for complex implementations"
            )

        # Timeline recommendations
        if analysis_a["timeline_mentions"] > analysis_b["timeline_mentions"] * 2:
            recommendations.append(
                f"{name_a} provides clearer project timeline and milestone planning"
            )
        elif analysis_b["timeline_mentions"] > analysis_a["timeline_mentions"] * 2:
            recommendations.append(
                f"{name_b} provides clearer project timeline and milestone planning"
            )

        # Testing recommendations
        if analysis_a["testing_focus"] > analysis_b["testing_focus"] * 2:
            recommendations.append(
                f"{name_a} emphasizes quality assurance and validation processes"
            )
        elif analysis_b["testing_focus"] > analysis_a["testing_focus"] * 2:
            recommendations.append(
                f"{name_b} emphasizes quality assurance and validation processes"
            )

        return recommendations
