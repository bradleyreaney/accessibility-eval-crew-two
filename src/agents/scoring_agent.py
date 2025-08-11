"""
Scoring agent for comprehensive evaluation and ranking of remediation plans.
References: Master Plan - Agent Specifications, Phase 2 - Scoring System
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

from .tools.scoring_calculator import ScoringCalculatorTool
from .tools.plan_comparator import PlanComparatorTool
from ..config.llm_config import LLMManager

logger = logging.getLogger(__name__)


class ScoringAgent:
    """
    Specialized agent for scoring, ranking, and comparative analysis of remediation plans.

    This agent synthesizes evaluations from judge agents and provides:
    - Weighted final scores
    - Comparative rankings
    - Statistical analysis
    - Recommendation synthesis
    """

    def __init__(self, llm_manager: LLMManager):
        """
        Initialize the scoring agent.

        Args:
            llm_manager: LLM configuration manager
        """
        self.llm_manager = llm_manager
        self.llm = llm_manager.gemini  # Use Gemini for scoring consistency
        self.agent = self._create_agent()
        self.tools = self._initialize_tools()

    def _create_agent(self) -> Agent:
        """Create the scoring agent with proper configuration"""
        return Agent(
            role="Accessibility Evaluation Scoring Specialist",
            goal="""Synthesize judge evaluations into comprehensive scoring and ranking
                   analysis that helps organizations make informed decisions about
                   remediation plan selection.""",
            backstory="""You are a quantitative analysis specialist with expertise in
                        accessibility evaluation methodology. Your role is to transform
                        qualitative judge assessments into clear, actionable scoring
                        and ranking insights.
                        
                        Your analytical expertise includes:
                        - Multi-criteria decision analysis (MCDA)
                        - Statistical evaluation and comparative ranking
                        - Weighted scoring methodology
                        - Risk-benefit analysis for accessibility projects
                        
                        You excel at synthesizing complex evaluations into clear
                        recommendations that account for organizational context,
                        resource constraints, and strategic priorities.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[],
        )

    def _initialize_tools(self) -> List:
        """Initialize the tools used by this agent"""
        try:
            return [ScoringCalculatorTool(), PlanComparatorTool()]
        except Exception as e:
            logger.warning(f"Some tools failed to initialize for scoring agent: {e}")
            return []

    def calculate_final_scores(
        self, evaluations: List[Dict[str, Any]], criteria_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate final weighted scores for all evaluated plans.

        Args:
            evaluations: List of evaluation results from judge agents
            criteria_weights: Dictionary of criteria names to weights

        Returns:
            Comprehensive scoring analysis with rankings
        """
        try:
            logger.info(f"Calculating final scores for {len(evaluations)} evaluations")

            # Extract scores from evaluations
            plan_scores = self._extract_scores_from_evaluations(evaluations)

            # Calculate weighted scores
            weighted_scores = {}
            for plan_name, scores in plan_scores.items():
                if scores:  # Only process plans with valid scores
                    weighted_score = self._calculate_weighted_score(
                        scores, criteria_weights
                    )
                    weighted_scores[plan_name] = weighted_score

            # Generate comprehensive scoring analysis
            scoring_prompt = f"""
            As a scoring specialist, provide comprehensive analysis of the remediation plan
            evaluations and generate final rankings with detailed insights.
            
            EVALUATION DATA:
            {self._format_evaluations_for_analysis(evaluations)}
            
            CALCULATED SCORES:
            {self._format_scores_for_analysis(weighted_scores)}
            
            ANALYSIS REQUIREMENTS:
            1. Validate the scoring methodology and calculations
            2. Provide final rankings with confidence levels
            3. Identify any scoring anomalies or concerns
            4. Generate strategic recommendations based on scores
            5. Account for organizational decision factors beyond scores
            6. Provide implementation risk assessment for top-ranked plans
            
            Output a comprehensive scoring report with clear recommendations.
            """

            result = self.llm.invoke(scoring_prompt)
            result_content = (
                result.content if hasattr(result, "content") else str(result)
            )

            scoring_analysis = {
                "scoring_method": "Weighted Multi-Criteria Analysis",
                "criteria_weights": criteria_weights,
                "plan_scores": weighted_scores,
                "rankings": self._generate_rankings(weighted_scores),
                "analysis_content": result_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "evaluations_processed": len(evaluations),
                "success": True,
            }

            logger.info("Final scoring analysis completed successfully")
            return scoring_analysis

        except Exception as e:
            logger.error(f"Final scoring calculation failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    def compare_plans(
        self,
        plan_a: Dict[str, Any],
        plan_b: Dict[str, Any],
        evaluation_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Perform detailed head-to-head comparison between two plans.

        Args:
            plan_a: Plan data including name and content
            plan_b: Plan data including name and content
            evaluation_data: List of evaluations for context

        Returns:
            Detailed comparison analysis
        """
        try:
            logger.info(f"Comparing {plan_a['name']} vs {plan_b['name']}")

            comparison_prompt = f"""
            Provide expert comparative analysis between two remediation plans using
            evaluation data and scoring insights.
            
            PLAN A: {plan_a['name']}
            Content: {plan_a.get('content', '')[:1000]}...
            
            PLAN B: {plan_b['name']} 
            Content: {plan_b.get('content', '')[:1000]}...
            
            EVALUATION CONTEXT:
            {self._format_evaluations_for_analysis(evaluation_data)}
            
            COMPARISON REQUIREMENTS:
            1. Head-to-head analysis across all evaluation criteria
            2. Strengths and weaknesses identification for each plan
            3. Risk-benefit analysis for implementation
            4. Resource requirement comparison
            5. Strategic fit assessment
            6. Clear recommendation with rationale
            
            Provide actionable insights for decision makers.
            """

            result = self.llm.invoke(comparison_prompt)
            result_content = (
                result.content if hasattr(result, "content") else str(result)
            )

            comparison_result = {
                "plan_a": plan_a["name"],
                "plan_b": plan_b["name"],
                "comparison_analysis": result_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": True,
            }

            logger.info(
                f"Plan comparison completed: {plan_a['name']} vs {plan_b['name']}"
            )
            return comparison_result

        except Exception as e:
            logger.error(f"Plan comparison failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    def _extract_scores_from_evaluations(
        self, evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """Extract numerical scores from evaluation text"""
        plan_scores = {}

        for eval_data in evaluations:
            if eval_data.get("success") and "plan_name" in eval_data:
                plan_name = eval_data["plan_name"]
                content = eval_data.get("evaluation_content", "")

                # Simple score extraction - in production this would be more sophisticated
                scores = self._parse_scores_from_text(content)
                if scores:
                    plan_scores[plan_name] = scores

        return plan_scores

    def _parse_scores_from_text(self, text: str) -> Dict[str, float]:
        """Parse scores from evaluation text - simplified implementation"""
        import re

        scores = {}
        criteria_map = {
            "strategic": "Strategic Prioritization",
            "technical": "Technical Specificity",
            "comprehensive": "Comprehensiveness",
            "vision": "Long-term Vision",
        }

        # Look for score patterns like "Strategic: 8/10" or "Technical Specificity: 7.5"
        for key, criterion in criteria_map.items():
            pattern = rf"{key}[^0-9]*([0-9]+(?:\.[0-9]+)?)"
            match = re.search(pattern, text.lower())
            if match:
                score = float(match.group(1))
                scores[criterion] = min(score, 10.0)  # Cap at 10

        return scores

    def _calculate_weighted_score(
        self, scores: Dict[str, float], weights: Dict[str, float]
    ) -> float:
        """Calculate weighted average score"""
        total_weighted = 0.0
        total_weight = 0.0

        for criterion, score in scores.items():
            if criterion in weights:
                weight = weights[criterion]
                total_weighted += score * weight
                total_weight += weight

        return total_weighted / total_weight if total_weight > 0 else 0.0

    def _generate_rankings(
        self, weighted_scores: Dict[str, float]
    ) -> List[Tuple[str, float]]:
        """Generate ranked list of plans by score"""
        return sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)

    def _format_evaluations_for_analysis(
        self, evaluations: List[Dict[str, Any]]
    ) -> str:
        """Format evaluations for LLM analysis"""
        formatted = []
        for eval_data in evaluations:
            if eval_data.get("success"):
                formatted.append(
                    f"""
                Plan: {eval_data.get('plan_name', 'Unknown')}
                Evaluator: {eval_data.get('evaluator', 'Unknown')}
                Content: {eval_data.get('evaluation_content', '')[:500]}...
                """
                )
        return "\n".join(formatted)

    def _format_scores_for_analysis(self, scores: Dict[str, float]) -> str:
        """Format scores for LLM analysis"""
        if not scores:
            return "No valid scores calculated"

        formatted = []
        for plan, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            formatted.append(f"{plan}: {score:.2f}/10")

        return "\n".join(formatted)

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        return {
            "name": "Scoring Agent",
            "llm": "Gemini Pro",
            "role": self.agent.role,
            "tools": [tool.name for tool in self.tools],
            "capabilities": [
                "Weighted score calculation",
                "Comparative ranking analysis",
                "Statistical evaluation synthesis",
                "Decision support recommendations",
            ],
        }
