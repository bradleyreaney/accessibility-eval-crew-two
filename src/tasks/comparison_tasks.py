"""
Task definitions for cross-plan comparison and analysis.
References: Phase 2 - Comparison Agent, Master Plan - Workflow Orchestration
"""

from typing import Dict, List

from crewai import Task

from ..agents.analysis_agent import AnalysisAgent
from ..models.evaluation_models import PlanEvaluation


class ComparisonTaskManager:
    """
    Manages comparison tasks between multiple evaluated plans.
    Coordinates consensus building and conflict resolution.
    """

    def __init__(self, comparison_agent: AnalysisAgent):
        """
        Initialize the comparison task manager.

        Args:
            comparison_agent: Analysis agent for comparison tasks
        """
        self.comparison_agent = comparison_agent

    def create_cross_plan_comparison_task(
        self, plan_evaluations: List[PlanEvaluation], audit_context: str
    ) -> Task:
        """
        Create comprehensive comparison task for all evaluated plans.

        Args:
            plan_evaluations: All individual plan evaluations
            audit_context: Original audit report

        Returns:
            CrewAI Task for cross-plan comparison
        """
        plan_summary = self._create_evaluation_summary(plan_evaluations)
        num_unique_plans = len(set(eval.plan_name for eval in plan_evaluations))

        # Truncate audit context for task description
        truncated_audit = audit_context[:300] + (
            "..." if len(audit_context) > 300 else ""
        )

        return Task(
            description=f"""
            Perform comprehensive cross-plan comparison and analysis of all evaluated
            accessibility remediation plans to identify the best elements from each
            and prepare for optimal plan synthesis.

            COMPARISON INPUT:
            - Number of Plans: {num_unique_plans}
            - Evaluation Data: {len(plan_evaluations)} individual evaluations
            - Original Audit Context: {truncated_audit}

            PLAN EVALUATION SUMMARY:
            {plan_summary}

            COMPARISON REQUIREMENTS:

            1. **Quantitative Analysis**:
               - Create detailed scoring comparison matrix
               - Identify highest and lowest scoring approaches per criterion
               - Calculate consensus levels between primary and secondary judges
               - Flag significant disagreements (>1.0 score difference)

            2. **Qualitative Analysis**:
               - Extract unique strengths from each plan
               - Identify common weaknesses across plans
               - Analyze strategic trade-offs between approaches
               - Assess complementary elements that could be combined

            3. **Gap Analysis**:
               - Identify issues addressed by some plans but not others
               - Find audit requirements missed by ALL plans
               - Highlight innovative approaches unique to specific plans
               - Note missing best practices not present in any plan

            4. **Synthesis Preparation**:
               - Recommend best elements to incorporate in final plan
               - Identify conflicts that need resolution
               - Suggest hybrid approaches for competing strategies
               - Prioritize improvements for synthesis phase

            QUALITY REQUIREMENTS:
            - Use specific evidence from plan evaluations
            - Provide quantitative comparisons where possible
            - Maintain objectivity in trade-off analysis
            - Prepare actionable insights for synthesis agent
            """,
            agent=self.comparison_agent.agent,
            expected_output="""
            ## Comprehensive Plan Comparison Analysis

            ### Executive Summary
            [High-level comparison overview and key findings]

            ### Quantitative Comparison Matrix
            | Plan | Overall Score | Judge Consensus | Top Strengths | Key Weaknesses |
            |------|---------------|-----------------|---------------|----------------|
            | Plan A | X.X (±Y.Y) | High/Med/Low | [Strength] | [Weakness] |
            [Continue for all plans]

            ### Qualitative Analysis by Plan

            #### Plan A
            **Unique Strengths:**
            - [Specific strength with evidence]

            **Notable Weaknesses:**
            - [Specific weakness with evidence]

            **Strategic Approach:**
            - [Description of plan's strategy]

            **Best Use Cases:**
            - [Scenarios where this plan excels]

            [Repeat for all plans]

            ### Cross-Plan Trade-off Analysis
            #### Speed vs. Thoroughness
            [Analysis of plans favoring quick fixes vs comprehensive approaches]

            #### Technical Complexity vs. Implementation Ease
            [Analysis of sophisticated vs. simple implementation approaches]

            #### Resource Requirements vs. Impact
            [Analysis of resource-intensive vs. efficient approaches]

            ### Critical Gap Analysis
            #### Missed by ALL Plans
            - [Issues not addressed by any plan]
            - [Missing implementation details]
            - [Absent process considerations]

            #### Best Practice Opportunities
            - [Advanced techniques not used by any plan]
            - [Industry standards not referenced]
            - [Innovative approaches missing]

            ### Synthesis Recommendations
            #### Elements to Incorporate
            - [Best prioritization logic from Plan X]
            - [Best technical solutions from Plan Y]
            - [Best process approach from Plan Z]

            #### Conflicts to Resolve
            - [Competing approaches that need harmonization]

            #### Innovation Opportunities
            - [New approaches to develop in synthesis]

            ### Consensus Assessment
            **High Consensus Areas:** [Where all judges agree]
            **Areas for Review:** [Where significant disagreement exists]
            **Confidence Level:** [Overall confidence in comparison findings]
            """,
            output_file="output/comparisons/cross_plan_analysis.md",
        )

    def create_consensus_building_task(
        self, conflicting_evaluations: List[PlanEvaluation]
    ) -> Task:
        """
        Create task to resolve significant disagreements between judges.

        Args:
            conflicting_evaluations: Plan evaluations with significant score differences

        Returns:
            CrewAI Task for consensus building
        """
        conflict_summary = self._format_conflicts(conflicting_evaluations)

        return Task(
            description=f"""
            Resolve significant disagreements between primary and secondary judges
            for plans where score differences exceed 1.0 points.

            CONFLICTING EVALUATIONS:
            {conflict_summary}

            CONSENSUS BUILDING REQUIREMENTS:
            1. Analyze the source of disagreement for each conflict
            2. Identify which perspective has stronger evidence
            3. Propose consensus scores with detailed justification
            4. Flag areas requiring human expert review

            RESOLUTION APPROACH:
            - Evidence-based reconciliation
            - Weighted averaging where appropriate
            - Clear documentation of resolution rationale
            - Escalation recommendations for unresolvable conflicts
            """,
            agent=self.comparison_agent.agent,
            expected_output="""
            ## Consensus Resolution Report

            ### Conflict Analysis
            [Detailed analysis of each disagreement]

            ### Proposed Consensus Scores
            [Recommended final scores with justification]

            ### Escalation Items
            [Issues requiring human expert review]
            """,
            output_file="output/comparisons/consensus_resolution.md",
        )

    def _create_evaluation_summary(self, evaluations: List[PlanEvaluation]) -> str:
        """Create formatted summary of all evaluations for comparison task."""
        summary = ""
        plans = {}

        # Group evaluations by plan
        for eval in evaluations:
            if eval.plan_name not in plans:
                plans[eval.plan_name] = []
            plans[eval.plan_name].append(eval)

        # Format summary
        for plan_name, plan_evals in plans.items():
            summary += f"\n### {plan_name}\n"
            for eval in plan_evals:
                summary += (
                    f"**{eval.judge_id.upper()} Judge:** Score {eval.overall_score}\n"
                )
                if eval.pros:
                    summary += f"Pros: {', '.join(eval.pros[:2])}\n"
                if eval.cons:
                    summary += f"Cons: {', '.join(eval.cons[:2])}\n"

        return summary

    def _format_conflicts(self, conflicts: List[PlanEvaluation]) -> str:
        """Format conflicting evaluations for consensus task."""
        formatted = ""
        for eval in conflicts:
            formatted += f"{eval.plan_name} ({eval.judge_id}): {eval.overall_score}\n"
        return formatted
