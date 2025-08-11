"""
Primary judge agent using Gemini Pro for accessibility evaluation.
References: Master Plan - Agent Specifications, Phase 2 - Core Agents
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from crewai import Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config.llm_config import LLMManager
from .tools.evaluation_framework import EvaluationFrameworkTool
from .tools.gap_analyzer import GapAnalyzerTool
from .tools.scoring_calculator import ScoringCalculatorTool

logger = logging.getLogger(__name__)


class PrimaryJudgeAgent:
    """
    Expert accessibility consultant using Gemini Pro for primary evaluation.

    This agent follows the evaluation framework from promt/eval-prompt.md exactly
    and provides comprehensive assessment of remediation plans using weighted criteria:
    - Strategic Prioritization (40%)
    - Technical Specificity (30%)
    - Comprehensiveness (20%)
    - Long-term Vision (10%)
    """

    def __init__(self, llm_manager: LLMManager):
        """
        Initialize the primary judge agent.

        Args:
            llm_manager: LLM configuration manager with Gemini Pro access
        """
        self.llm_manager = llm_manager
        self.llm = llm_manager.gemini
        self.agent = self._create_agent()
        self.tools = self._initialize_tools()

    def _create_agent(self) -> Agent:
        """Create the primary judge agent with proper configuration"""
        return Agent(
            role="Expert Accessibility Consultant - Primary Judge",
            goal="""Provide comprehensive evaluation of remediation plans using the
                   established framework from promt/eval-prompt.md with weighted criteria:
                   - Strategic Prioritization (40%)
                   - Technical Specificity (30%)
                   - Comprehensiveness (20%)
                   - Long-term Vision (10%)

                   Deliver thorough, evidence-based assessments that help organizations
                   choose the most effective accessibility remediation approach.""",
            backstory="""You are a senior accessibility consultant with 15+ years of experience
                        implementing WCAG 2.1/2.2 standards across diverse organizations.
                        You have guided Fortune 500 companies, government agencies, and
                        startups through complex accessibility transformations.

                        Your expertise combines:
                        - Deep technical knowledge of web standards and assistive technologies
                        - Strategic thinking about organizational change and resource allocation
                        - Practical experience with real-world implementation challenges
                        - User-centered perspective informed by disability community feedback

                        You evaluate remediation plans not just for technical correctness,
                        but for strategic coherence, implementation feasibility, and genuine
                        impact on users with disabilities. You think like a senior developer,
                        project manager, and user advocate simultaneously.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[],  # Tools will be added separately to avoid circular imports
        )

    def _initialize_tools(self) -> List:
        """Initialize the tools used by this agent"""
        try:
            return [
                EvaluationFrameworkTool(),
                ScoringCalculatorTool(),
                GapAnalyzerTool(),
            ]
        except Exception as e:
            logger.warning(f"Some tools failed to initialize: {e}")
            return []

    def evaluate_plan(
        self, plan_name: str, plan_content: str, audit_context: str
    ) -> Dict[str, Any]:
        """
        Evaluate a single remediation plan using the established framework.

        Args:
            plan_name: Name of the plan (e.g., "PlanA")
            plan_content: Full text content of the remediation plan
            audit_context: Original accessibility audit report

        Returns:
            Structured evaluation results
        """
        try:
            logger.info(f"Primary judge evaluating {plan_name}")

            # Create evaluation task
            evaluation_task = Task(
                description=f"""
                Evaluate {plan_name} for accessibility remediation effectiveness using the
                established evaluation framework.

                CONTEXT (Original Audit):
                {audit_context[:2000]}...

                PLAN TO EVALUATE ({plan_name}):
                {plan_content[:3000]}...

                EVALUATION REQUIREMENTS:
                1. Apply each weighted criterion systematically:
                   - Strategic Prioritization (40%): Risk-based sequencing, critical path analysis
                   - Technical Specificity (30%): Implementation detail, clarity, feasibility
                   - Comprehensiveness (20%): Coverage of audit findings, completeness
                   - Long-term Vision (10%): Sustainability, maintenance, scalability

                2. For each criterion, provide:
                   - Score (1-10 scale)
                   - Detailed reasoning (2-3 sentences minimum)
                   - Specific evidence from the plan
                   - Areas for improvement

                3. Calculate weighted final score

                4. Provide overall assessment with strengths and weaknesses

                5. Make specific recommendations for improvement

                Use the evaluation_framework tool to structure your analysis.
                Use the gap_analyzer tool to identify missing elements.
                Use the scoring_calculator tool for weighted score calculations.
                """,
                agent=self.agent,
                expected_output="""
                Comprehensive evaluation report with:
                - Individual criterion scores and reasoning
                - Weighted overall score
                - Strengths and weaknesses analysis
                - Gap analysis findings
                - Specific improvement recommendations
                """,
            )

            # Execute evaluation using the agent directly
            # Note: In CrewAI, tasks are typically executed by Crew, not individually
            # For now, we'll use the agent's LLM directly for evaluation

            evaluation_prompt = f"""
            As an expert accessibility consultant, evaluate {plan_name} using the
            comprehensive framework established in promt/eval-prompt.md.

            CONTEXT (Original Audit):
            {audit_context[:2000]}...

            PLAN TO EVALUATE ({plan_name}):
            {plan_content[:3000]}...

            EVALUATION REQUIREMENTS:
            1. Apply each weighted criterion systematically:
               - Strategic Prioritization (40%): Risk-based sequencing, critical path analysis
               - Technical Specificity (30%): Implementation detail, clarity, feasibility
               - Comprehensiveness (20%): Coverage of audit findings, completeness
               - Long-term Vision (10%): Sustainability, maintenance, scalability

            2. For each criterion, provide:
               - Score (1-10 scale)
               - Detailed reasoning (2-3 sentences minimum)
               - Specific evidence from the plan
               - Areas for improvement

            3. Calculate weighted final score
            4. Provide overall assessment with strengths and weaknesses
            5. Make specific recommendations for improvement
            """

            result = self.llm.invoke(evaluation_prompt)
            result_content = (
                result.content if hasattr(result, "content") else str(result)
            )

            # Structure the response
            evaluation_result = {
                "plan_name": plan_name,
                "evaluator": "Primary Judge (Gemini Pro)",
                "evaluation_content": result_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": True,
            }

            logger.info(f"Primary judge completed evaluation of {plan_name}")
            return evaluation_result

        except Exception as e:
            logger.error(f"Primary judge evaluation failed for {plan_name}: {e}")
            return {
                "plan_name": plan_name,
                "evaluator": "Primary Judge (Gemini Pro)",
                "evaluation_content": f"Evaluation failed: {str(e)}",
                "success": False,
                "error": str(e),
            }

    def create_evaluation_task(
        self, plan_name: str, plan_content: str, audit_context: str
    ) -> Task:
        """
        Create a structured evaluation task for the agent.

        Args:
            plan_name: Name of the plan to evaluate
            plan_content: Full content of the remediation plan
            audit_context: Original audit report for context

        Returns:
            Configured CrewAI Task for evaluation
        """
        return Task(
            description=f"""
            As an expert accessibility consultant, evaluate {plan_name} using the
            comprehensive framework established in promt/eval-prompt.md.

            Your evaluation must cover all weighted criteria with detailed analysis,
            evidence-based scoring, and actionable recommendations.

            Plan Content: {plan_content[:1000]}...
            Audit Context: {audit_context[:1000]}...
            """,
            agent=self.agent,
            expected_output="Detailed evaluation with scores, reasoning, and recommendations",
        )

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        return {
            "name": "Primary Judge Agent",
            "llm": "Gemini Pro",
            "role": self.agent.role,
            "tools": [tool.name for tool in self.tools],
            "capabilities": [
                "Comprehensive plan evaluation",
                "Weighted scoring using established criteria",
                "Gap analysis and missing element identification",
                "Strategic recommendation generation",
            ],
        }


class SecondaryJudgeAgent:
    """
    Secondary accessibility consultant using GPT-4 for independent evaluation.

    This agent provides a second opinion using the same evaluation framework
    but with a different LLM to ensure objectivity and catch potential biases.
    """

    def __init__(self, llm_manager: LLMManager):
        """
        Initialize the secondary judge agent.

        Args:
            llm_manager: LLM configuration manager with GPT-4 access
        """
        self.llm_manager = llm_manager
        self.llm = llm_manager.openai
        self.agent = self._create_agent()
        self.tools = self._initialize_tools()

    def _create_agent(self) -> Agent:
        """Create the secondary judge agent with proper configuration"""
        return Agent(
            role="Expert Accessibility Consultant - Secondary Judge",
            goal="""Provide independent evaluation of remediation plans using the same
                   framework as the primary judge, offering a second perspective to
                   ensure comprehensive and unbiased assessment.""",
            backstory="""You are an independent accessibility consultant specializing
                        in objective evaluation and quality assurance. Your role is to
                        provide a fresh perspective on remediation plans, validating
                        or challenging the primary assessment through rigorous analysis.

                        You bring complementary expertise in:
                        - Alternative evaluation methodologies and frameworks
                        - Cross-industry accessibility implementation patterns
                        - Risk assessment and mitigation strategies
                        - Quality assurance and validation processes

                        Your independent evaluation helps ensure that final decisions
                        are well-informed and consider multiple expert perspectives.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[],
        )

    def _initialize_tools(self) -> List:
        """Initialize the tools used by this agent"""
        try:
            return [
                EvaluationFrameworkTool(),
                ScoringCalculatorTool(),
                GapAnalyzerTool(),
            ]
        except Exception as e:
            logger.warning(f"Some tools failed to initialize for secondary judge: {e}")
            return []

    def evaluate_plan(
        self,
        plan_name: str,
        plan_content: str,
        audit_context: str,
        primary_evaluation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Provide independent evaluation of a remediation plan.

        Args:
            plan_name: Name of the plan (e.g., "PlanA")
            plan_content: Full text content of the remediation plan
            audit_context: Original accessibility audit report
            primary_evaluation: Optional primary judge evaluation for comparison

        Returns:
            Structured evaluation results
        """
        try:
            logger.info(f"Secondary judge evaluating {plan_name}")

            evaluation_prompt = f"""
            As an independent accessibility consultant, provide a thorough evaluation
            of {plan_name} using the established framework from promt/eval-prompt.md.

            Your role is to offer an independent second opinion that validates or
            challenges assessments through rigorous analysis.

            CONTEXT (Original Audit):
            {audit_context[:2000]}...

            PLAN TO EVALUATE ({plan_name}):
            {plan_content[:3000]}...

            {"PRIMARY EVALUATION FOR REFERENCE:" if primary_evaluation else ""}
            {primary_evaluation[:1000] if primary_evaluation else ""}

            INDEPENDENT EVALUATION REQUIREMENTS:
            1. Apply the same weighted criteria independently:
               - Strategic Prioritization (40%)
               - Technical Specificity (30%)
               - Comprehensiveness (20%)
               - Long-term Vision (10%)

            2. Provide your independent assessment with:
               - Objective scoring and reasoning
               - Alternative perspectives where applicable
               - Validation or constructive challenge of other viewpoints
               - Focus on aspects that may have been overlooked

            3. Offer recommendations that complement the overall evaluation
            """

            result = self.llm.invoke(evaluation_prompt)
            result_content = (
                result.content if hasattr(result, "content") else str(result)
            )

            evaluation_result = {
                "plan_name": plan_name,
                "evaluator": "Secondary Judge (GPT-4)",
                "evaluation_content": result_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": True,
                "includes_primary_comparison": primary_evaluation is not None,
            }

            logger.info(f"Secondary judge completed evaluation of {plan_name}")
            return evaluation_result

        except Exception as e:
            logger.error(f"Secondary judge evaluation failed for {plan_name}: {e}")
            return {
                "plan_name": plan_name,
                "evaluator": "Secondary Judge (GPT-4)",
                "evaluation_content": f"Evaluation failed: {str(e)}",
                "success": False,
                "error": str(e),
            }

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        return {
            "name": "Secondary Judge Agent",
            "llm": "GPT-4",
            "role": self.agent.role,
            "tools": [tool.name for tool in self.tools],
            "capabilities": [
                "Independent plan evaluation",
                "Objective second opinion analysis",
                "Primary evaluation validation",
                "Alternative perspective identification",
            ],
        }
