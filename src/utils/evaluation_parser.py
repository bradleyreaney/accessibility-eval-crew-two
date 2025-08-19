"""
Evaluation parser for extracting structured data from text-based evaluation results.

This module parses the text output from CrewAI agents and extracts:
- Overall scores
- Criteria scores
- Evaluation details
- Plan rankings
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EvaluationParser:
    """
    Parser for extracting structured evaluation data from text-based agent outputs.
    """

    @staticmethod
    def parse_evaluation_results(evaluation_text: str) -> Dict[str, Any]:
        """
        Parse evaluation text and extract structured scoring data.

        Args:
            evaluation_text: Text output from evaluation agent

        Returns:
            Structured evaluation data with scores and details
        """
        try:
            # Extract overall score
            overall_score = EvaluationParser._extract_overall_score(evaluation_text)

            # Extract criteria scores
            criteria_scores = EvaluationParser._extract_criteria_scores(evaluation_text)

            # Extract plan name
            plan_name = EvaluationParser._extract_plan_name(evaluation_text)

            # Extract evaluation details
            strengths = EvaluationParser._extract_strengths(evaluation_text)
            weaknesses = EvaluationParser._extract_weaknesses(evaluation_text)
            rationale = EvaluationParser._extract_rationale(evaluation_text)

            return {
                "plan_name": plan_name,
                "overall_score": overall_score,
                "criteria_scores": criteria_scores,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "rationale": rationale,
                "raw_text": evaluation_text,
            }
        except Exception as e:
            logger.error(f"Error parsing evaluation results: {e}")
            return {
                "plan_name": "Unknown",
                "overall_score": 0.0,
                "criteria_scores": {},
                "strengths": [],
                "weaknesses": [],
                "rationale": "Error parsing evaluation",
                "raw_text": evaluation_text,
            }

    @staticmethod
    def _extract_overall_score(text: str) -> float:
        """Extract overall score from evaluation text."""
        # Look for patterns like "Overall Score: 7.4/10" or "Overall Score: 7.4"
        patterns = [
            r"Overall Score:\s*(\d+\.?\d*)/10",
            r"Overall Score:\s*(\d+\.?\d*)",
            r"Overall Assessment\s*\*\*Overall Score:\s*(\d+\.?\d*)/10",
            r"Overall Assessment\s*\*\*Overall Score:\s*(\d+\.?\d*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        # If no pattern found, try to extract from the end of the text
        # Look for the last number that might be a score
        numbers = re.findall(r"\d+\.?\d*", text)
        if numbers:
            try:
                # Take the last number that's between 0 and 10
                for num in reversed(numbers):
                    score = float(num)
                    if 0 <= score <= 10:
                        return score
            except ValueError:
                pass

        return 0.0

    @staticmethod
    def _extract_criteria_scores(text: str) -> Dict[str, float]:
        """Extract individual criteria scores from evaluation text."""
        criteria_scores = {}

        # Look for patterns like "Score: 7.5/10" or "Score: 7.5"
        criteria_patterns = [
            (
                r"Strategic Prioritization.*?Score:\s*(\d+\.?\d*)/10",
                "strategic_prioritization",
            ),
            (
                r"Strategic Prioritization.*?Score:\s*(\d+\.?\d*)",
                "strategic_prioritization",
            ),
            (
                r"Technical Specificity.*?Score:\s*(\d+\.?\d*)/10",
                "technical_specificity",
            ),
            (r"Technical Specificity.*?Score:\s*(\d+\.?\d*)", "technical_specificity"),
            (r"Comprehensiveness.*?Score:\s*(\d+\.?\d*)/10", "comprehensiveness"),
            (r"Comprehensiveness.*?Score:\s*(\d+\.?\d*)", "comprehensiveness"),
            (r"Long-term Vision.*?Score:\s*(\d+\.?\d*)/10", "long_term_vision"),
            (r"Long-term Vision.*?Score:\s*(\d+\.?\d*)", "long_term_vision"),
        ]

        for pattern, criteria_name in criteria_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                try:
                    score = float(match.group(1))
                    criteria_scores[criteria_name] = score
                except ValueError:
                    continue

        return criteria_scores

    @staticmethod
    def _extract_plan_name(text: str) -> str:
        """Extract plan name from evaluation text."""
        # Look for patterns like "Primary Evaluation: PlanA" or "Secondary Evaluation: PlanA"
        patterns = [
            r"Primary Evaluation:\s*(\w+)",
            r"Secondary Evaluation:\s*(\w+)",
            r"Evaluation:\s*(\w+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1)

        return "Unknown"

    @staticmethod
    def _extract_strengths(text: str) -> List[str]:
        """Extract key strengths from evaluation text."""
        strengths = []

        # Look for strengths section
        strength_patterns = [
            r"Key Strengths:.*?(?=Key Weaknesses:|Rationale:|$)",
            r"\*\*Key Strengths:\*\*.*?(?=\*\*Key Weaknesses:\*\*|\*\*Rationale:\*\*|$)",
        ]

        for pattern in strength_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                strength_text = match.group(0)
                # Extract bullet points
                bullet_points = re.findall(r"[-*]\s*([^-\n]+)", strength_text)
                strengths.extend(
                    [point.strip() for point in bullet_points if point.strip()]
                )
                break

        return strengths

    @staticmethod
    def _extract_weaknesses(text: str) -> List[str]:
        """Extract key weaknesses from evaluation text."""
        weaknesses = []

        # Look for weaknesses section
        weakness_patterns = [
            r"Key Weaknesses:.*?(?=Rationale:|$)",
            r"\*\*Key Weaknesses:\*\*.*?(?=\*\*Rationale:\*\*|$)",
        ]

        for pattern in weakness_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                weakness_text = match.group(0)
                # Extract bullet points
                bullet_points = re.findall(r"[-*]\s*([^-\n]+)", weakness_text)
                weaknesses.extend(
                    [point.strip() for point in bullet_points if point.strip()]
                )
                break

        return weaknesses

    @staticmethod
    def _extract_rationale(text: str) -> str:
        """Extract rationale from evaluation text."""
        # Look for rationale section
        rationale_patterns = [
            r"Rationale:\s*(.*?)(?=\n\n|\n\*\*|$)",
            r"\*\*Rationale:\*\*\s*(.*?)(?=\n\n|\n\*\*|$)",
        ]

        for pattern in rationale_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return ""

    @staticmethod
    def _parse_list_results(
        individual_results: List, parsed_results: Dict[str, Any]
    ) -> None:
        """Parse individual results when they are in a list format."""
        for result in individual_results:
            if isinstance(result, str):
                # Direct string result
                parsed = EvaluationParser.parse_evaluation_results(result)
                plan_name = parsed.get("plan_name", "Unknown")
                parsed_results["individual_evaluations"][plan_name] = parsed
            elif hasattr(result, "raw") and result.raw:
                # CrewOutput object with raw attribute
                result_str = result.raw
                parsed = EvaluationParser.parse_evaluation_results(result_str)
                plan_name = parsed.get("plan_name", "Unknown")
                parsed_results["individual_evaluations"][plan_name] = parsed
            else:
                # Try to convert to string
                try:
                    result_str = str(result)
                    parsed = EvaluationParser.parse_evaluation_results(result_str)
                    plan_name = parsed.get("plan_name", "Unknown")
                    parsed_results["individual_evaluations"][plan_name] = parsed
                except Exception as e:
                    logger.warning(f"Could not parse result: {e}")

    @staticmethod
    def _parse_dict_results(
        individual_results: Dict, parsed_results: Dict[str, Any]
    ) -> None:
        """Parse individual results when they are in a dictionary format."""
        for plan_name, result in individual_results.items():
            if isinstance(result, str):
                parsed = EvaluationParser.parse_evaluation_results(result)
                parsed_results["individual_evaluations"][plan_name] = parsed
            else:
                parsed_results["individual_evaluations"][plan_name] = result

    @staticmethod
    def _parse_iterable_results(
        individual_results, parsed_results: Dict[str, Any]
    ) -> None:
        """Parse individual results when they are in an iterable format."""
        try:
            # Handle CrewOutput objects - they have a 'raw' attribute with the text
            if hasattr(individual_results, "raw") and individual_results.raw:
                result_str = individual_results.raw
                parsed = EvaluationParser.parse_evaluation_results(result_str)
                plan_name = parsed.get("plan_name", "Unknown")
                parsed_results["individual_evaluations"][plan_name] = parsed
            else:
                # Try to iterate over the object
                for result in individual_results:
                    if isinstance(result, str):
                        parsed = EvaluationParser.parse_evaluation_results(result)
                        plan_name = parsed.get("plan_name", "Unknown")
                        parsed_results["individual_evaluations"][plan_name] = parsed
        except Exception as e:
            logger.warning(f"Iteration failed: {e}")
            # If iteration fails, try to convert to string
            try:
                result_str = str(individual_results)
                parsed = EvaluationParser.parse_evaluation_results(result_str)
                plan_name = parsed.get("plan_name", "Unknown")
                parsed_results["individual_evaluations"][plan_name] = parsed
            except Exception as e2:
                logger.warning(f"Could not parse individual_results: {e2}")

    @staticmethod
    def _parse_fallback_results(crew_results, parsed_results: Dict[str, Any]) -> None:
        """Parse results when individual_evaluations key is not present."""
        if isinstance(crew_results, list):
            # CrewAI kickoff() returns a list of task results
            for result in crew_results:
                if isinstance(result, str):
                    parsed = EvaluationParser.parse_evaluation_results(result)
                    plan_name = parsed.get("plan_name", "Unknown")
                    parsed_results["individual_evaluations"][plan_name] = parsed
        elif isinstance(crew_results, dict):
            # If crew_results is a dictionary but doesn't have individual_evaluations key
            # This might be the case if the structure is different
            for key, value in crew_results.items():
                if isinstance(value, list):
                    # This might be the individual evaluations list
                    for result in value:
                        if isinstance(result, str):
                            parsed = EvaluationParser.parse_evaluation_results(result)
                            plan_name = parsed.get("plan_name", "Unknown")
                            parsed_results["individual_evaluations"][plan_name] = parsed

    @staticmethod
    def _parse_analysis_results(
        crew_results: Dict[str, Any], parsed_results: Dict[str, Any]
    ) -> None:
        """Parse comparison analysis and optimal plan results."""
        # Parse comparison analysis
        if "comparison_analysis" in crew_results:
            comparison_result = crew_results["comparison_analysis"]
            if isinstance(comparison_result, str):
                parsed_results["comparison_analysis"] = {
                    "analysis": comparison_result,
                    "type": "text_analysis",
                }
            else:
                parsed_results["comparison_analysis"] = comparison_result

        # Parse optimal plan
        if "optimal_plan" in crew_results:
            optimal_result = crew_results["optimal_plan"]
            if isinstance(optimal_result, str):
                parsed_results["optimal_plan"] = {
                    "synthesis": optimal_result,
                    "type": "text_synthesis",
                }
            else:
                parsed_results["optimal_plan"] = optimal_result

    @staticmethod
    def parse_crew_results(crew_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse CrewAI results and extract structured evaluation data.

        Args:
            crew_results: Raw results from CrewAI execution

        Returns:
            Structured evaluation results
        """
        parsed_results = {
            "individual_evaluations": {},
            "comparison_analysis": {},
            "optimal_plan": {},
            "resilience_info": (
                crew_results.get("resilience_info", {})
                if isinstance(crew_results, dict)
                else {}
            ),
            "llm_availability": (
                crew_results.get("llm_availability", {})
                if isinstance(crew_results, dict)
                else {}
            ),
        }

        # Parse individual evaluations
        if "individual_evaluations" in crew_results:
            individual_results = crew_results["individual_evaluations"]

            # Handle different result formats
            if isinstance(individual_results, list):
                EvaluationParser._parse_list_results(individual_results, parsed_results)
            elif isinstance(individual_results, dict):
                EvaluationParser._parse_dict_results(individual_results, parsed_results)
            elif hasattr(individual_results, "__iter__") and not isinstance(
                individual_results, str
            ):
                EvaluationParser._parse_iterable_results(
                    individual_results, parsed_results
                )
        else:
            # If individual_evaluations is not in crew_results, try fallback parsing
            EvaluationParser._parse_fallback_results(crew_results, parsed_results)

        # Parse analysis results
        EvaluationParser._parse_analysis_results(crew_results, parsed_results)

        return parsed_results
