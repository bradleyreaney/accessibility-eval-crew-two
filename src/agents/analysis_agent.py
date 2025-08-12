"""
Analysis agent for comprehensive strategic insights and recommendations.
References: Master Plan - Agent Specifications, Phase 2 - Strategic Analysis
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config.llm_config import LLMManager
from .tools.gap_analyzer import GapAnalyzerTool
from .tools.plan_comparator import PlanComparatorTool

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """
    Strategic analysis agent for comprehensive insights and decision support.

    This agent provides:
    - Strategic recommendation synthesis
    - Implementation roadmap guidance
    - Risk assessment and mitigation
    - Organizational fit analysis
    """

    def __init__(self, llm_manager: LLMManager):
        """
        Initialize the analysis agent.

        Args:
            llm_manager: LLM configuration manager
        """
        self.llm_manager = llm_manager
        self.llm = llm_manager.openai  # Use GPT-4 for strategic analysis
        self.agent = self._create_agent()
        self.tools = self._initialize_tools()

    def _create_agent(self) -> Agent:
        """Create the analysis agent with proper configuration"""
        return Agent(
            role="Strategic Accessibility Implementation Analyst",
            goal="""Provide comprehensive strategic analysis and implementation guidance
                   that helps organizations successfully execute their chosen remediation
                   approach with minimal risk and maximum impact.""",
            backstory="""You are a strategic implementation consultant specializing in
                        large-scale accessibility transformation projects. Your expertise
                        spans organizational change management, technical project delivery,
                        and accessibility program development.

                        Your strategic perspective includes:
                        - Enterprise-scale accessibility program implementation
                        - Change management and stakeholder alignment strategies
                        - Risk assessment and mitigation planning
                        - Resource optimization and timeline management
                        - Success metrics and measurement frameworks

                        You excel at translating evaluation insights into actionable
                        strategic roadmaps that consider organizational culture, technical
                        constraints, and business objectives.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[],
        )

    def _initialize_tools(self) -> List:
        """Initialize the tools used by this agent"""
        try:
            return [GapAnalyzerTool(), PlanComparatorTool()]
        except Exception as e:
            logger.warning(f"Some tools failed to initialize for analysis agent: {e}")
            return []

    def generate_strategic_analysis(
        self,
        evaluations: List[Dict[str, Any]],
        scoring_results: Dict[str, Any],
        organizational_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive strategic analysis and recommendations.

        Args:
            evaluations: List of evaluation results from judge agents
            scoring_results: Scoring and ranking results
            organizational_context: Optional context about the organization

        Returns:
            Strategic analysis with implementation recommendations
        """
        try:
            logger.info("Generating strategic analysis and recommendations")

            analysis_prompt = f"""
            As a strategic accessibility implementation analyst, provide comprehensive
            analysis and actionable recommendations based on the evaluation results.

            EVALUATION SUMMARY:
            {self._format_evaluations_summary(evaluations)}

            SCORING RESULTS:
            {self._format_scoring_summary(scoring_results)}

            {"ORGANIZATIONAL CONTEXT:" if organizational_context else ""}
            {self._format_organizational_context(organizational_context) if organizational_context else ""}

            STRATEGIC ANALYSIS REQUIREMENTS:

            1. EXECUTIVE SUMMARY
               - Key findings and primary recommendation
               - Strategic rationale for plan selection
               - Critical success factors

            2. IMPLEMENTATION ROADMAP
               - Phased implementation approach
               - Resource requirements and timeline
               - Key milestones and dependencies
               - Risk mitigation strategies

            3. ORGANIZATIONAL CONSIDERATIONS
               - Change management requirements
               - Stakeholder alignment strategies
               - Training and capability building needs
               - Communication and engagement plan

            4. SUCCESS METRICS
               - KPIs for tracking progress
               - Measurement framework
               - Review and adjustment mechanisms

            5. RISK ASSESSMENT
               - Implementation risks and mitigation
               - Contingency planning
               - Quality assurance approaches

            6. ALTERNATIVE SCENARIOS
               - If top choice fails, what's the fallback?
               - How to optimize lower-ranked plans
               - Hybrid approach possibilities

            Provide strategic insights that enable confident decision-making and successful implementation.
            """

            result = self.llm.invoke(analysis_prompt)
            result_content = (
                result.content if hasattr(result, "content") else str(result)
            )

            strategic_analysis = {
                "analysis_type": "Strategic Implementation Analysis",
                "primary_recommendation": self._extract_primary_recommendation(
                    str(result_content)
                ),
                "analysis_content": result_content,
                "evaluations_analyzed": len(evaluations),
                "scoring_data_included": bool(scoring_results.get("success")),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": True,
            }

            logger.info("Strategic analysis completed successfully")
            return strategic_analysis

        except Exception as e:
            logger.error(f"Strategic analysis generation failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    def analyze_implementation_readiness(
        self,
        recommended_plan: str,
        plan_content: str,
        evaluation_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze implementation readiness for the recommended plan.

        Args:
            recommended_plan: Name of the recommended plan
            plan_content: Full content of the recommended plan
            evaluation_data: Evaluation results for context

        Returns:
            Implementation readiness assessment
        """
        try:
            logger.info(f"Analyzing implementation readiness for {recommended_plan}")

            readiness_prompt = f"""
            Assess the implementation readiness and provide actionable guidance for
            executing the recommended accessibility remediation plan.

            RECOMMENDED PLAN: {recommended_plan}

            PLAN CONTENT:
            {plan_content[:2000]}...

            EVALUATION CONTEXT:
            {self._format_evaluations_summary(evaluation_data)}

            READINESS ASSESSMENT REQUIREMENTS:

            1. IMMEDIATE ACTIONS
               - What can start immediately?
               - Prerequisites that must be completed first
               - Quick wins to build momentum

            2. RESOURCE REQUIREMENTS
               - Team composition and skills needed
               - Technology and tool requirements
               - Budget considerations and cost optimization

            3. TIMELINE ANALYSIS
               - Realistic timeline estimates
               - Critical path dependencies
               - Opportunities for parallel execution

            4. RISK FACTORS
               - Technical implementation risks
               - Organizational resistance points
               - External dependency risks

            5. SUCCESS ENABLERS
               - Factors that will accelerate success
               - Stakeholder engagement strategies
               - Communication and training needs

            6. MEASUREMENT APPROACH
               - How to track progress
               - Success criteria and KPIs
               - Review and adjustment triggers

            Provide practical, actionable guidance for successful implementation.
            """

            result = self.llm.invoke(readiness_prompt)
            result_content = (
                result.content if hasattr(result, "content") else str(result)
            )

            readiness_assessment = {
                "recommended_plan": recommended_plan,
                "assessment_type": "Implementation Readiness Analysis",
                "readiness_content": result_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": True,
            }

            logger.info(
                f"Implementation readiness analysis completed for {recommended_plan}"
            )
            return readiness_assessment

        except Exception as e:
            logger.error(f"Implementation readiness analysis failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    def generate_executive_summary(
        self, all_analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate executive summary for leadership decision-making.

        Args:
            all_analysis_data: Complete analysis results including evaluations, scoring, and strategic analysis

        Returns:
            Executive summary with key insights and recommendations
        """
        try:
            logger.info("Generating executive summary")

            executive_prompt = f"""
            Create a concise executive summary for organizational leadership to support
            accessibility remediation plan decision-making.

            ANALYSIS DATA:
            {self._format_complete_analysis(all_analysis_data)}

            EXECUTIVE SUMMARY REQUIREMENTS:

            1. SITUATION OVERVIEW (2-3 sentences)
               - Current accessibility challenges
               - Options evaluated

            2. RECOMMENDATION (1-2 sentences)
               - Primary recommended approach
               - Key rationale

            3. EXPECTED OUTCOMES (3-4 bullet points)
               - Accessibility improvements achieved
               - Timeline for results
               - Resource investment required

            4. NEXT STEPS (3-4 bullet points)
               - Immediate actions required
               - Key decisions needed
               - Success enablers

            5. RISK CONSIDERATIONS (2-3 bullet points)
               - Primary risks and mitigation
               - Contingency planning

            Keep the summary to 1 page, focused on decision-making insights.
            """

            result = self.llm.invoke(executive_prompt)
            result_content = (
                result.content if hasattr(result, "content") else str(result)
            )

            executive_summary = {
                "summary_type": "Executive Decision Summary",
                "summary_content": result_content,
                "data_sources": list(all_analysis_data.keys()),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": True,
            }

            logger.info("Executive summary generated successfully")
            return executive_summary

        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    def _format_evaluations_summary(self, evaluations: List[Dict[str, Any]]) -> str:
        """Format evaluations for strategic analysis"""
        if not evaluations:
            return "No evaluations available"

        summary_lines = [f"Total Evaluations: {len(evaluations)}", ""]

        for eval_data in evaluations:
            if eval_data.get("success"):
                plan_name = eval_data.get("plan_name", "Unknown")
                evaluator = eval_data.get("evaluator", "Unknown")
                content_preview = eval_data.get("evaluation_content", "")[:200]
                summary_lines.append(
                    f"Plan {plan_name} ({evaluator}): {content_preview}..."
                )

        return "\n".join(summary_lines)

    def _format_scoring_summary(self, scoring_results: Dict[str, Any]) -> str:
        """Format scoring results for strategic analysis"""
        if not scoring_results.get("success"):
            return "Scoring analysis not available"

        rankings = scoring_results.get("rankings", [])
        summary_lines = ["PLAN RANKINGS:"]

        for i, (plan_name, score) in enumerate(rankings[:5], 1):
            summary_lines.append(f"{i}. {plan_name}: {score:.2f}/10")

        return "\n".join(summary_lines)

    def _format_organizational_context(self, context: Dict[str, Any]) -> str:
        """Format organizational context for analysis"""
        if not context:
            return ""

        formatted = []
        for key, value in context.items():
            formatted.append(f"{key.title()}: {value}")

        return "\n".join(formatted)

    def _format_complete_analysis(self, data: Dict[str, Any]) -> str:
        """Format complete analysis data for executive summary"""
        formatted_sections = []

        for section_name, section_data in data.items():
            if isinstance(section_data, dict) and section_data.get("success"):
                preview = str(section_data).replace("\n", " ")[:300]
                formatted_sections.append(f"{section_name.upper()}: {preview}...")

        return "\n\n".join(formatted_sections)

    def _extract_primary_recommendation(self, content: str) -> str:
        """Extract primary recommendation from analysis content"""
        # Simple extraction - look for recommendation keywords
        lines = content.split("\n")
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["recommend", "primary", "best", "top"]
            ):
                return line.strip()[:200]

        return "See full analysis for recommendations"

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        return {
            "name": "Analysis Agent",
            "llm": "GPT-4",
            "role": self.agent.role,
            "tools": [tool.name for tool in self.tools],
            "capabilities": [
                "Strategic implementation analysis",
                "Implementation readiness assessment",
                "Executive summary generation",
                "Risk assessment and mitigation planning",
            ],
        }
