"""
Task definitions for individual plan evaluations.
References: Phase 2 - Judge Agents, Master Plan - Task Definitions
"""

from typing import Any, Dict, List, Optional

from crewai import Task

from ..agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from ..models.evaluation_models import EvaluationInput, PlanEvaluation


class EvaluationTaskManager:
    """
    Manages task creation and execution for plan evaluations.
    Coordinates between primary and secondary judges.
    """

    def __init__(
        self, primary_judge: PrimaryJudgeAgent, secondary_judge: SecondaryJudgeAgent
    ):
        """
        Initialize the evaluation task manager.

        Args:
            primary_judge: Primary judge agent (Gemini Pro)
            secondary_judge: Secondary judge agent (GPT-4)
        """
        self.primary_judge = primary_judge
        self.secondary_judge = secondary_judge

    def create_primary_evaluation_task(
        self, plan_name: str, plan_content: str, audit_context: str
    ) -> Task:
        """
        Create primary evaluation task for Gemini Pro judge.

        Args:
            plan_name: Name of the plan to evaluate (e.g., "PlanA")
            plan_content: Full text content of the remediation plan
            audit_context: Original accessibility audit report

        Returns:
            CrewAI Task configured for primary evaluation
        """
        # Truncate content for task description to avoid overly long prompts
        truncated_plan = plan_content[:500] + ("..." if len(plan_content) > 500 else "")
        truncated_audit = audit_context[:500] + (
            "..." if len(audit_context) > 500 else ""
        )

        return Task(
            description=f"""
            Evaluate {plan_name} using the comprehensive framework from promt/eval-prompt.md.

            EVALUATION CONTEXT:
            - Plan Name: {plan_name}
            - Original Audit: {truncated_audit}
            - Plan Content: {truncated_plan}

            EVALUATION FRAMEWORK:
            Apply the exact evaluation criteria with weighted scoring:
            1. Strategic Prioritization (40%) - Assess logic, sequencing, prioritization models
            2. Technical Specificity (30%) - Evaluate clarity, accuracy, actionability
            3. Comprehensiveness (20%) - Check coverage and structure
            4. Long-term Vision (10%) - Review post-remediation plans

            OUTPUT REQUIREMENTS:
            - Detailed analysis following eval-prompt.md structure
            - Numerical scores for each criterion (0-10 scale)
            - Weighted overall score calculation
            - Specific pros and cons identification
            - Evidence-based rationale for all scores

            QUALITY STANDARDS:
            - Provide specific examples from the plan content
            - Reference specific sections of the audit report
            - Ensure scores are justified with concrete evidence
            - Maintain consistency with evaluation framework
            """,
            agent=self.primary_judge.agent,
            expected_output=f"""
            ## Primary Evaluation: {plan_name}

            ### Strategic Prioritization (40%)
            **Score: [X.X/10]**
            [Detailed analysis with specific examples from plan]

            ### Technical Specificity (30%)
            **Score: [X.X/10]**
            [Detailed analysis with specific examples from plan]

            ### Comprehensiveness (20%)
            **Score: [X.X/10]**
            [Detailed analysis with specific examples from plan]

            ### Long-term Vision (10%)
            **Score: [X.X/10]**
            [Detailed analysis with specific examples from plan]

            ### Overall Assessment
            **Overall Score: [X.X/10]**
            **Key Strengths:**
            - [Specific strength with evidence]
            - [Specific strength with evidence]
            - [Specific strength with evidence]

            **Key Weaknesses:**
            - [Specific weakness with evidence]
            - [Specific weakness with evidence]
            - [Specific weakness with evidence]

            **Rationale:** [Comprehensive reasoning for overall score]
            """,
            output_file=f"output/evaluations/{plan_name}_primary_evaluation.md",
        )

    def create_secondary_evaluation_task(
        self,
        plan_name: str,
        plan_content: str,
        audit_context: str,
        primary_result: Optional[str] = None,
    ) -> Task:
        """
        Create secondary evaluation task for GPT-4 judge.
        Includes cross-validation with primary judge if result available.

        Args:
            plan_name: Name of the plan to evaluate
            plan_content: Full text content of the remediation plan
            audit_context: Original accessibility audit report
            primary_result: Optional primary judge result for cross-validation

        Returns:
            CrewAI Task configured for secondary evaluation
        """
        # Truncate content for task description
        truncated_plan = plan_content[:500] + ("..." if len(plan_content) > 500 else "")
        truncated_audit = audit_context[:500] + (
            "..." if len(audit_context) > 500 else ""
        )

        cross_validation_note = ""
        if primary_result:
            truncated_primary = primary_result[:300] + (
                "..." if len(primary_result) > 300 else ""
            )
            cross_validation_note = f"""
            CROSS-VALIDATION NOTE:
            The primary judge has completed their evaluation. You should evaluate
            independently using the same framework, then note any significant
            differences (>1.0 score difference) for consensus discussion.

            Primary Judge Result Summary: {truncated_primary}
            """

        return Task(
            description=f"""
            Provide independent secondary evaluation of {plan_name} using identical
            framework from promt/eval-prompt.md for cross-validation and consensus building.

            EVALUATION CONTEXT:
            - Plan Name: {plan_name}
            - Original Audit: {truncated_audit}
            - Plan Content: {truncated_plan}

            {cross_validation_note}

            EVALUATION FRAMEWORK:
            Apply identical evaluation criteria as primary judge:
            1. Strategic Prioritization (40%) - Independent assessment of approach
            2. Technical Specificity (30%) - Focus on implementation feasibility
            3. Comprehensiveness (20%) - Verify coverage completeness
            4. Long-term Vision (10%) - Assess sustainability provisions

            SECONDARY JUDGE FOCUS:
            - Technical implementation perspective
            - User experience considerations
            - Development team feasibility
            - Cross-validation of primary scores

            OUTPUT REQUIREMENTS:
            - Same structured format as primary evaluation
            - Independent scoring (don't be influenced by primary scores)
            - Flag any significant disagreements with primary judge
            - Provide complementary perspective on technical aspects
            """,
            agent=self.secondary_judge.agent,
            expected_output=f"""
            ## Secondary Evaluation: {plan_name}

            ### Strategic Prioritization (40%)
            **Score: [X.X/10]**
            [Detailed analysis with specific examples from plan]

            ### Technical Specificity (30%)
            **Score: [X.X/10]**
            [Detailed analysis with specific examples from plan]

            ### Comprehensiveness (20%)
            **Score: [X.X/10]**
            [Detailed analysis with specific examples from plan]

            ### Long-term Vision (10%)
            **Score: [X.X/10]**
            [Detailed analysis with specific examples from plan]

            ### Overall Assessment
            **Overall Score: [X.X/10]**
            **Key Strengths:**
            - [Specific strength with evidence]

            **Key Weaknesses:**
            - [Specific weakness with evidence]

            **Rationale:** [Comprehensive reasoning for overall score]

            ### Cross-Validation Notes
            **Consensus Areas:** [Where secondary aligns with primary]
            **Disagreement Areas:** [Significant differences in scoring/analysis]
            **Confidence Level:** [High/Medium/Low confidence in assessment]
            """,
            output_file=f"output/evaluations/{plan_name}_secondary_evaluation.md",
        )

    def create_batch_evaluation_tasks(
        self, evaluation_input: EvaluationInput
    ) -> List[Task]:
        """
        Create evaluation tasks for all remediation plans.
        Returns list of tasks for both primary and secondary judges.

        Args:
            evaluation_input: Input containing audit report and remediation plans

        Returns:
            List of Task objects for all plan evaluations
        """
        tasks = []

        for plan_name, plan_content in evaluation_input.remediation_plans.items():
            # Primary evaluation task
            primary_task = self.create_primary_evaluation_task(
                plan_name, plan_content.content, evaluation_input.audit_report.content
            )
            tasks.append(primary_task)

            # Secondary evaluation task
            secondary_task = self.create_secondary_evaluation_task(
                plan_name, plan_content.content, evaluation_input.audit_report.content
            )
            tasks.append(secondary_task)

        return tasks
