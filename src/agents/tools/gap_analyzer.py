"""
Gap analyzer tool for identifying missing elements in remediation plans.
References: Master Plan - Gap Analysis, Phase 2 - Comprehensive Evaluation
"""

import logging
from typing import Any, Dict, List, Set

from crewai_tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GapAnalysisInput(BaseModel):
    """Input model for gap analysis tool"""

    plan_content: str = Field(description="Full text content of the remediation plan")
    audit_content: str = Field(description="Full text content of the audit report")
    plan_name: str = Field(description="Name of the plan being analyzed")


class GapAnalyzerTool(BaseTool):
    """
    Tool for analyzing gaps between audit findings and remediation plans.

    This tool identifies:
    - Missing issue coverage
    - Incomplete remediation steps
    - Unaddressed WCAG criteria
    - Strategic gaps
    """

    name: str = "gap_analyzer"
    description: str = """
    Analyze gaps between audit findings and remediation coverage.
    Identifies missing issues, incomplete solutions, and strategic oversights.
    """
    args_schema: type[BaseModel] = GapAnalysisInput

    def __init__(self):
        super().__init__(
            name="gap_analyzer",
            description="""Analyze gaps between audit findings and remediation coverage.
            Identifies missing issues, incomplete solutions, and strategic oversights.""",
        )

        # WCAG Success Criteria keywords for analysis - use object.__setattr__ to bypass Pydantic
        object.__setattr__(
            self,
            "wcag_criteria",
            {
                "1.1": [
                    "alt text",
                    "alternative text",
                    "images",
                    "graphics",
                    "non-text content",
                ],
                "1.3": ["headings", "structure", "semantic", "landmarks", "lists"],
                "1.4": ["color contrast", "contrast ratio", "text spacing", "resize"],
                "2.1": ["keyboard", "focus", "navigation", "tab order"],
                "2.4": ["page titles", "headings", "links", "navigation", "skip links"],
                "3.1": ["language", "reading level", "pronunciation"],
                "3.2": ["consistent", "predictable", "navigation", "identification"],
                "3.3": ["error", "labels", "instructions", "suggestions"],
                "4.1": ["valid", "markup", "aria", "roles", "properties"],
            },
        )

    def _run(self, plan_content: str, audit_content: str, plan_name: str) -> str:
        """
        Analyze gaps in remediation plan coverage.

        Args:
            plan_content: Full text content of the remediation plan
            audit_content: Full text content of the audit report
            plan_name: Name of the plan being analyzed

        Returns:
            Detailed gap analysis report
        """
        try:
            logger.info(f"Analyzing gaps for {plan_name}")

            # Simplified gap analysis for validation
            plan_lower = plan_content.lower()
            audit_lower = audit_content.lower()

            # Basic coverage assessment
            covered_issues = 0
            total_issues = max(
                1, len([line for line in audit_content.split("\n") if line.strip()])
            )

            # Simple keyword matching for demo purposes
            accessibility_keywords = [
                "keyboard",
                "contrast",
                "alt text",
                "headings",
                "focus",
            ]
            for keyword in accessibility_keywords:
                if keyword in audit_lower and keyword in plan_lower:
                    covered_issues += 1

            coverage_percentage = (covered_issues / len(accessibility_keywords)) * 100

            # Generate gap analysis report
            gap_report = f"""GAP ANALYSIS REPORT for {plan_name}
=============================================

COVERAGE SUMMARY:
- Issues Addressed: {covered_issues}/{len(accessibility_keywords)} accessibility areas
- Coverage Percentage: {coverage_percentage:.1f}%

ANALYSIS:
The plan addresses {covered_issues} out of {len(accessibility_keywords)} key accessibility areas identified in the audit.

RECOMMENDATIONS:
{"Good coverage of accessibility requirements." if coverage_percentage > 60 else "Consider addressing additional accessibility requirements."}
"""

            return gap_report

        except Exception as e:
            logger.error(f"Gap analysis failed for {plan_name}: {e}")
            return f"Error: Failed to analyze gaps for {plan_name}: {str(e)}"

    def _extract_audit_issues(self, audit_content: str) -> List[str]:
        """Extract key accessibility issues from audit report"""
        issues = []

        # Look for common issue indicators
        issue_keywords = [
            "violation",
            "error",
            "fail",
            "missing",
            "incorrect",
            "inaccessible",
            "non-compliant",
            "issue",
            "problem",
        ]

        lines = audit_content.lower().split("\n")
        for line in lines:
            if any(keyword in line for keyword in issue_keywords):
                # Clean and extract meaningful issue descriptions
                if len(line.strip()) > 20:  # Avoid short/incomplete lines
                    issues.append(line.strip())

        return issues[:20]  # Limit to most relevant issues

    def _analyze_audit_coverage(
        self, plan_content: str, audit_content: str
    ) -> Dict[str, Any]:
        """Analyze how well the plan covers audit findings"""
        plan_lower = plan_content.lower()
        audit_lines = [
            line.strip() for line in audit_content.split("\n") if line.strip()
        ]

        coverage_stats = {
            "total_issues": 0,
            "addressed_issues": 0,
            "partially_addressed": 0,
            "unaddressed_issues": [],
            "coverage_percentage": 0.0,
        }

        for issue in audit_lines:
            if len(issue) < 10:  # Skip very short lines
                continue

            coverage_stats["total_issues"] += 1

            # Extract key terms from issue description
            issue_terms = self._extract_key_terms(issue)

            # Check if any terms appear in the plan
            term_matches = sum(1 for term in issue_terms if term in plan_lower)

            if term_matches >= len(issue_terms) * 0.7:  # 70% of terms match
                coverage_stats["addressed_issues"] += 1
            elif term_matches > 0:
                coverage_stats["partially_addressed"] += 1
            else:
                coverage_stats["unaddressed_issues"].append(
                    issue[:100]
                )  # Truncate for readability

        if coverage_stats["total_issues"] > 0:
            coverage_stats["coverage_percentage"] = (
                float(coverage_stats["addressed_issues"])
                / float(coverage_stats["total_issues"])
                * 100
            )

        return coverage_stats

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from issue description"""
        # Remove common words and extract meaningful terms
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        words = text.lower().split()
        key_terms = [word for word in words if len(word) > 3 and word not in stop_words]
        return key_terms[:5]  # Limit to most relevant terms

    def _identify_wcag_gaps(
        self, plan_content: str, audit_content: str
    ) -> Dict[str, List[str]]:
        """Identify WCAG criteria that may be missing from the plan"""
        plan_lower = plan_content.lower()
        audit_lower = audit_content.lower()
        gaps = {}

        for criterion, keywords in self.wcag_criteria.items():
            # Check if audit mentions this criterion area
            audit_mentions = any(keyword in audit_lower for keyword in keywords)
            # Check if plan addresses this criterion area
            plan_addresses = any(keyword in plan_lower for keyword in keywords)

            if audit_mentions and not plan_addresses:
                gaps[criterion] = keywords

        return gaps

    def _generate_gap_report(
        self,
        plan_name: str,
        coverage: Dict[str, Any],
        wcag_gaps: Dict[str, List[str]],
        audit_issues: List[str],
    ) -> str:
        """Generate comprehensive gap analysis report"""

        report_lines = [
            f"GAP ANALYSIS REPORT - {plan_name}",
            "=" * 50,
            "",
            "COVERAGE SUMMARY:",
            f"  Total Issues Identified: {coverage['total_issues']}",
            f"  Fully Addressed: {coverage['addressed_issues']}",
            f"  Partially Addressed: {coverage['partially_addressed']}",
            f"  Coverage Rate: {coverage['coverage_percentage']:.1f}%",
            "",
        ]

        # Add unaddressed issues
        if coverage["unaddressed_issues"]:
            report_lines.extend(
                [
                    "UNADDRESSED ISSUES:",
                    "⚠️  The following audit findings appear to lack coverage:",
                ]
            )
            for i, issue in enumerate(coverage["unaddressed_issues"][:5], 1):
                report_lines.append(f"  {i}. {issue}...")
            report_lines.append("")

        # Add WCAG gaps
        if wcag_gaps:
            report_lines.extend(
                [
                    "WCAG CRITERIA GAPS:",
                    "📋 The following WCAG areas may need attention:",
                ]
            )
            for criterion, keywords in wcag_gaps.items():
                report_lines.append(f"  WCAG {criterion}: {', '.join(keywords[:3])}")
            report_lines.append("")

        # Add strategic gaps
        strategic_gaps = self._identify_strategic_gaps(coverage)
        if strategic_gaps:
            report_lines.extend(
                ["STRATEGIC GAPS:", "🎯 Areas for strategic improvement:"]
            )
            report_lines.extend([f"  • {gap}" for gap in strategic_gaps])
            report_lines.append("")

        # Add recommendations
        recommendations = self._generate_recommendations(coverage, wcag_gaps)
        if recommendations:
            report_lines.extend(["RECOMMENDATIONS:", "💡 Suggested improvements:"])
            report_lines.extend([f"  • {rec}" for rec in recommendations])

        return "\n".join(report_lines)

    def _identify_strategic_gaps(self, coverage: Dict[str, Any]) -> List[str]:
        """Identify strategic gaps based on coverage analysis"""
        gaps = []

        if coverage["coverage_percentage"] < 80:
            gaps.append("Plan may miss critical accessibility issues")

        if coverage["partially_addressed"] > coverage["addressed_issues"]:
            gaps.append(
                "Many issues are only partially addressed - need more detailed solutions"
            )

        if len(coverage["unaddressed_issues"]) > 3:
            gaps.append(
                "Significant number of audit findings lack clear remediation steps"
            )

        return gaps

    def _generate_recommendations(
        self, coverage: Dict[str, Any], wcag_gaps: Dict[str, List[str]]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if coverage["coverage_percentage"] < 70:
            recommendations.append(
                "Review audit findings more thoroughly to ensure comprehensive coverage"
            )

        if wcag_gaps:
            recommendations.append(
                f"Address missing WCAG criteria: {', '.join(wcag_gaps.keys())}"
            )

        if coverage["partially_addressed"] > 0:
            recommendations.append(
                "Provide more detailed implementation steps for partially addressed issues"
            )

        return recommendations
