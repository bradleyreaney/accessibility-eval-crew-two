"""
Task definitions for optimal plan synthesis.

This module provides task management for synthesizing optimal remediation plans
from comparison analysis results. It integrates with the AnalysisAgent to create
comprehensive synthesis tasks.

References:
    - Phase 2: AnalysisAgent implementation
    - Master Plan: Synthesis Task requirements
    - Phase 3: Workflow orchestration
"""

from typing import Any, Dict, List

from crewai import Task

from ..agents.analysis_agent import AnalysisAgent
from ..models.evaluation_models import PlanEvaluation


class SynthesisTaskManager:
    """
    Manages synthesis tasks for creating optimal remediation plans.

    This task manager orchestrates the creation of synthesis tasks that combine
    the best elements from multiple evaluated plans while addressing their
    collective weaknesses and incorporating expert recommendations.

    Attributes:
        synthesis_agent: The AnalysisAgent instance for synthesis operations
    """

    def __init__(self, synthesis_agent: AnalysisAgent):
        """
        Initialize the synthesis task manager.

        Args:
            synthesis_agent: AnalysisAgent instance configured for synthesis
        """
        self.synthesis_agent = synthesis_agent

    def create_optimal_plan_synthesis_task(
        self,
        plan_evaluations: List[PlanEvaluation],
        comparison_analysis: str,
        audit_context: str,
    ) -> Task:
        """
        Create task for synthesizing optimal remediation plan.

        This method creates a comprehensive synthesis task that combines the best
        elements from all evaluated plans while addressing identified gaps and
        weaknesses.

        Args:
            plan_evaluations: List of individual plan evaluations
            comparison_analysis: Comprehensive comparison analysis results
            audit_context: Original accessibility audit report

        Returns:
            CrewAI Task configured for optimal plan synthesis
        """
        synthesis_context = self._create_synthesis_context(
            plan_evaluations, comparison_analysis
        )

        return Task(
            description=f"""
            Create the ultimate accessibility remediation plan by synthesizing the
            best elements from all evaluated plans while addressing their collective
            weaknesses and incorporating expert recommendations.

            SYNTHESIS INPUT:
            - {len(plan_evaluations)} individual plan evaluations from both judges
            - Comprehensive comparison analysis with trade-offs and gaps
            - Original audit report requiring remediation
            - Identified improvement opportunities and best practices

            CONTEXT SUMMARY:
            {synthesis_context}

            ORIGINAL AUDIT CONTEXT:
            {audit_context[:500]}...

            SYNTHESIS OBJECTIVES:

            1. **Strategic Excellence**: Design prioritization strategy combining:
               - Best prioritization logic from highest-scoring plans
               - Multi-factor considerations (user impact, architectural leverage, effort, risk)
               - Clear sequencing with dependencies and rationale
               - Risk mitigation and contingency planning

            2. **Technical Superiority**: Integrate most effective solutions:
               - Specific, actionable implementation guidance
               - Code examples and technical specifications
               - Modern web development best practices
               - Clear acceptance criteria and testing approaches

            3. **Complete Coverage**: Ensure comprehensive audit coverage:
               - Address ALL issues identified in original audit
               - Fill gaps missed by individual plans
               - Connect all fixes to POUR principles explicitly
               - Provide clear implementation roadmap with milestones

            4. **Long-term Success**: Include robust sustainability provisions:
               - Post-remediation verification processes
               - Continuous monitoring and maintenance strategies
               - Team training and capability building programs
               - Cultural integration and change management

            5. **Innovation Integration**: Add expert enhancements:
               - Advanced accessibility considerations beyond basic compliance
               - Innovative implementation approaches and tools
               - Process improvements and automation opportunities
               - Stakeholder engagement and communication strategies

            QUALITY REQUIREMENTS:
            - Build on proven strengths from comparison analysis
            - Address all identified weaknesses and gaps
            - Maintain internal consistency and coherence
            - Provide realistic timelines and resource estimates
            - Include success metrics and validation criteria
            """,
            agent=self.synthesis_agent.agent,
            expected_output="""
            # Synthesized Optimal Accessibility Remediation Plan

            ## Executive Summary
            [Comprehensive overview of synthesized approach with key innovations and expected outcomes]

            ## Strategic Foundation

            ### Prioritization Framework
            **Multi-Factor Prioritization Logic:**
            - User Impact Assessment (Weight: 40%)
            - Architectural Leverage Opportunities (Weight: 30%)
            - Implementation Effort and Complexity (Weight: 20%)
            - Risk and Dependency Factors (Weight: 10%)

            **Implementation Sequencing:**
            [Clear phases with dependencies, timelines, and decision points]

            ## Technical Implementation Guide

            ### Phase 1: Critical User Path Fixes (Weeks 1-4)
            [High-impact, low-complexity fixes with immediate user benefit]

            #### Issue 1: [Specific Audit Finding]
            **Solution:** [Detailed technical approach]
            **Implementation:** [Step-by-step guidance with code examples]
            **Testing:** [Validation criteria and testing approach]
            **Success Metrics:** [How to measure success]

            ### Phase 2: Structural Improvements (Weeks 5-12)
            [Architectural changes and systematic fixes]

            ### Phase 3: Enhancement and Optimization (Weeks 13-20)
            [Advanced features and comprehensive optimization]

            ## POUR Principle Alignment

            ### Perceivable
            [How remediation improves content perception]

            ### Operable
            [How remediation improves interface operation]

            ### Understandable
            [How remediation improves content comprehension]

            ### Robust
            [How remediation improves technical reliability]

            ## Implementation Strategy

            ### Resource Requirements
            - Development Team: [Specific roles and time allocation]
            - External Resources: [Tools, services, consultants needed]
            - Budget Considerations: [Cost estimates and justification]

            ### Risk Mitigation
            [Identified risks and mitigation strategies]

            ### Success Metrics
            [Quantitative and qualitative measures of success]

            ## Long-term Sustainability

            ### Verification and Testing
            [Comprehensive testing strategy for all remediation work]

            ### Continuous Monitoring
            [Ongoing accessibility monitoring and maintenance processes]

            ### Team Development
            [Training programs and capability building initiatives]

            ### Process Integration
            [How to integrate accessibility into development workflows]

            ## Innovation and Best Practices

            ### Expert Recommendations
            [Advanced considerations and cutting-edge approaches]

            ### Automation Opportunities
            [Tools and processes to automate accessibility testing and monitoring]

            ### Future Considerations
            [Preparation for evolving accessibility standards and technologies]

            ## Implementation Timeline
            [Detailed project timeline with milestones, dependencies, and deliverables]

            ## Conclusion
            [Summary of key benefits and expected outcomes from synthesized plan]
            """,
        )

    def _create_synthesis_context(
        self, plan_evaluations: List[PlanEvaluation], comparison_analysis: str
    ) -> str:
        """
        Create formatted context summary for synthesis task.

        Args:
            plan_evaluations: Individual plan evaluations
            comparison_analysis: Cross-plan comparison results

        Returns:
            Formatted context string for synthesis task
        """
        context = "### PLAN EVALUATION SUMMARY:\n"

        # Group evaluations by plan
        plans = {}
        for evaluation in plan_evaluations:
            if evaluation.plan_name not in plans:
                plans[evaluation.plan_name] = []
            plans[evaluation.plan_name].append(evaluation)

        # Format plan summaries
        for plan_name, evaluations in plans.items():
            context += f"\n**{plan_name}:**\n"

            for eval in evaluations:
                context += f"- {eval.judge_id.upper()} Judge: {eval.overall_score}/10\n"
                if eval.pros:
                    context += f"  Strengths: {', '.join(eval.pros[:2])}\n"
                if eval.cons:
                    context += f"  Weaknesses: {', '.join(eval.cons[:2])}\n"

        context += f"\n### COMPARISON ANALYSIS:\n{comparison_analysis[:300]}...\n"

        return context
