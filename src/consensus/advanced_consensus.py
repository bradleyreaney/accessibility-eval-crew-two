"""
Advanced consensus building system for judge disagreements
References: Master Plan - Multi-Judge Consensus, Phase 3 - Quality Assurance

Phase 5: Advanced Features & Optimization - Consensus Mechanisms
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np

from ..models.evaluation_models import JudgmentScore, PlanEvaluation


class ConflictSeverity(Enum):
    """Enum for classifying conflict severity levels"""

    LOW = "low"  # <0.5 score difference
    MEDIUM = "medium"  # 0.5-1.0 score difference
    HIGH = "high"  # 1.0-2.0 score difference
    CRITICAL = "critical"  # >2.0 score difference


@dataclass
class ConflictAnalysis:
    """Data structure for analyzing conflicts between judge evaluations"""

    plan_name: str
    criterion: str
    primary_score: float
    secondary_score: float
    difference: float
    severity: ConflictSeverity
    primary_rationale: str
    secondary_rationale: str
    confidence_delta: float


class AdvancedConsensusEngine:
    """
    Sophisticated consensus building with multiple resolution strategies
    """

    def __init__(self):
        self.resolution_strategies = {
            ConflictSeverity.LOW: self._weighted_average_resolution,
            ConflictSeverity.MEDIUM: self._evidence_based_resolution,
            ConflictSeverity.HIGH: self._expert_mediation_resolution,
            ConflictSeverity.CRITICAL: self._human_escalation_resolution,
        }

        self.judge_reliability_scores = {
            "gemini": {"accuracy": 0.85, "consistency": 0.80, "bias_factor": 0.05},
            "gpt4": {"accuracy": 0.88, "consistency": 0.82, "bias_factor": 0.03},
        }

    def analyze_conflicts(
        self, evaluations: List[PlanEvaluation]
    ) -> List[ConflictAnalysis]:
        """
        Identify and analyze all conflicts between judge evaluations

        Args:
            evaluations: All evaluation results from both judges

        Returns:
            List of detailed conflict analyses
        """
        conflicts = []

        # Group evaluations by plan
        plan_groups = self._group_evaluations_by_plan(evaluations)

        for plan_name, plan_evals in plan_groups.items():
            if len(plan_evals) >= 2:  # Have both judge evaluations
                primary_eval = next(
                    (e for e in plan_evals if e.judge_id == "gemini"), None
                )
                secondary_eval = next(
                    (e for e in plan_evals if e.judge_id == "gpt4"), None
                )

                if primary_eval and secondary_eval:
                    plan_conflicts = self._analyze_plan_conflicts(
                        primary_eval, secondary_eval
                    )
                    conflicts.extend(plan_conflicts)

        return conflicts

    def resolve_conflicts(
        self, conflicts: List[ConflictAnalysis]
    ) -> Dict[str, Dict[str, float]]:
        """
        Resolve conflicts using appropriate strategies based on severity

        Args:
            conflicts: List of identified conflicts

        Returns:
            Dictionary of resolved scores by plan and criterion
        """
        resolved_scores = {}

        for conflict in conflicts:
            # Select resolution strategy based on severity
            resolution_func = self.resolution_strategies[conflict.severity]
            resolved_score = resolution_func(conflict)

            # Store resolved score (only if not None from human escalation)
            if resolved_score is not None:
                if conflict.plan_name not in resolved_scores:
                    resolved_scores[conflict.plan_name] = {}

                resolved_scores[conflict.plan_name][conflict.criterion] = resolved_score

        return resolved_scores

    def _weighted_average_resolution(self, conflict: ConflictAnalysis) -> float:
        """
        Resolve low-severity conflicts with weighted averaging
        Weights based on judge reliability scores
        """
        primary_weight = self.judge_reliability_scores["gemini"]["accuracy"]
        secondary_weight = self.judge_reliability_scores["gpt4"]["accuracy"]

        total_weight = primary_weight + secondary_weight

        resolved_score = (
            (conflict.primary_score * primary_weight)
            + (conflict.secondary_score * secondary_weight)
        ) / total_weight

        return round(resolved_score, 2)

    def _evidence_based_resolution(self, conflict: ConflictAnalysis) -> float:
        """
        Resolve medium-severity conflicts by analyzing evidence quality
        """
        # Analyze rationale quality and evidence strength
        primary_evidence_score = self._score_evidence_quality(
            conflict.primary_rationale
        )
        secondary_evidence_score = self._score_evidence_quality(
            conflict.secondary_rationale
        )

        # Weight scores based on evidence quality
        if primary_evidence_score > secondary_evidence_score * 1.2:
            # Primary has significantly stronger evidence
            return conflict.primary_score
        elif secondary_evidence_score > primary_evidence_score * 1.2:
            # Secondary has significantly stronger evidence
            return conflict.secondary_score
        else:
            # Evidence quality similar, use confidence-weighted average
            primary_confidence = (
                1.0 - conflict.confidence_delta
                if conflict.confidence_delta < 0
                else 1.0
            )
            secondary_confidence = (
                1.0 + conflict.confidence_delta
                if conflict.confidence_delta > 0
                else 1.0
            )

            total_confidence = primary_confidence + secondary_confidence

            resolved_score = (
                (conflict.primary_score * primary_confidence)
                + (conflict.secondary_score * secondary_confidence)
            ) / total_confidence

            return round(resolved_score, 2)

    def _expert_mediation_resolution(self, conflict: ConflictAnalysis) -> float:
        """
        Resolve high-severity conflicts with expert mediation logic
        Uses sophisticated heuristics to determine most likely correct score
        """
        # Multi-factor analysis for resolution
        factors = {
            "judge_reliability": self._calculate_judge_reliability_factor(conflict),
            "consistency_check": self._perform_consistency_check(conflict),
            "external_validation": self._validate_against_benchmarks(conflict),
            "bias_detection": self._detect_systematic_bias(conflict),
        }

        # Weighted decision based on multiple factors
        if factors["judge_reliability"] > 0.7:
            # High confidence in one judge's reliability for this type of evaluation
            if factors["judge_reliability"] > 0:
                return conflict.primary_score
            else:
                return conflict.secondary_score

        # No clear reliability winner, use comprehensive analysis
        composite_score = self._calculate_composite_resolution(conflict, factors)
        return round(composite_score, 2)

    def _human_escalation_resolution(
        self, conflict: ConflictAnalysis
    ) -> Optional[float]:
        """
        Mark critical conflicts for human expert review
        These require domain expert intervention
        """
        # Log for human review
        escalation_data = {
            "conflict": conflict,
            "automated_resolution": "ESCALATED_TO_HUMAN",
            "urgency": "HIGH",
            "required_expertise": "ACCESSIBILITY_EXPERT",
            "review_deadline": "24_HOURS",
        }

        # In production, this would integrate with issue tracking system
        self._log_escalation(escalation_data)

        # Return None to indicate human review required
        return None

    def _score_evidence_quality(self, rationale: str) -> float:
        """
        Score the quality of evidence in judge rationale

        Args:
            rationale: Judge's explanation for their score

        Returns:
            Evidence quality score (0-1)
        """
        quality_indicators = {
            "specific_examples": 0.3,  # Contains specific examples from plan
            "wcag_references": 0.2,  # References WCAG guidelines
            "technical_details": 0.2,  # Includes technical implementation details
            "user_impact": 0.15,  # Discusses user impact
            "quantitative_data": 0.15,  # Includes measurable criteria
        }

        score = 0.0
        rationale_lower = rationale.lower()

        # Check for specific examples
        if any(
            phrase in rationale_lower
            for phrase in ["for example", "such as", "specifically"]
        ):
            score += quality_indicators["specific_examples"]

        # Check for WCAG references
        if any(
            phrase in rationale_lower
            for phrase in ["wcag", "guideline", "level aa", "level a"]
        ):
            score += quality_indicators["wcag_references"]

        # Check for technical details
        if any(
            phrase in rationale_lower
            for phrase in ["code", "css", "html", "aria", "implementation"]
        ):
            score += quality_indicators["technical_details"]

        # Check for user impact discussion
        if any(
            phrase in rationale_lower
            for phrase in ["user", "accessibility", "usability", "barrier"]
        ):
            score += quality_indicators["user_impact"]

        # Check for quantitative elements
        if any(char.isdigit() for char in rationale) and any(
            phrase in rationale_lower for phrase in ["%", "seconds", "pixels", "ratio"]
        ):
            score += quality_indicators["quantitative_data"]

        return min(score, 1.0)  # Cap at 1.0

    def generate_consensus_report(
        self,
        conflicts: List[ConflictAnalysis],
        resolutions: Dict[str, Dict[str, float]],
    ) -> str:
        """
        Generate comprehensive consensus building report
        """
        report = f"""
# Consensus Building Report

## Executive Summary
- Total Conflicts Identified: {len(conflicts)}
- Conflicts Resolved Automatically: {len([c for c in conflicts if c.severity != ConflictSeverity.CRITICAL])}
- Conflicts Requiring Human Review: {len([c for c in conflicts if c.severity == ConflictSeverity.CRITICAL])}

## Conflict Severity Breakdown
"""

        severity_counts = {}
        for conflict in conflicts:
            severity_counts[conflict.severity] = (
                severity_counts.get(conflict.severity, 0) + 1
            )

        for severity, count in severity_counts.items():
            report += f"- {severity.value.title()}: {count} conflicts\n"

        report += "\n## Resolution Strategies Applied\n"

        for conflict in conflicts:
            strategy = self.resolution_strategies[conflict.severity].__name__
            report += f"- {conflict.plan_name} ({conflict.criterion}): {strategy}\n"

        report += "\n## Judge Performance Analysis\n"
        report += self._generate_judge_performance_analysis(conflicts)

        return report

    def _group_evaluations_by_plan(
        self, evaluations: List[PlanEvaluation]
    ) -> Dict[str, List[PlanEvaluation]]:
        """Group evaluations by plan name"""
        plan_groups = {}
        for evaluation in evaluations:
            if evaluation.plan_name not in plan_groups:
                plan_groups[evaluation.plan_name] = []
            plan_groups[evaluation.plan_name].append(evaluation)
        return plan_groups

    def _analyze_plan_conflicts(
        self, primary_eval, secondary_eval
    ) -> List[ConflictAnalysis]:
        """Analyze conflicts between two evaluations of the same plan"""
        conflicts = []

        # Match criteria between evaluations
        primary_scores = {
            score.criterion: score for score in primary_eval.judgment_scores
        }
        secondary_scores = {
            score.criterion: score for score in secondary_eval.judgment_scores
        }

        for criterion in primary_scores:
            if criterion in secondary_scores:
                primary_score_obj = primary_scores[criterion]
                secondary_score_obj = secondary_scores[criterion]

                difference = abs(primary_score_obj.score - secondary_score_obj.score)

                # Classify severity
                if difference < 0.5:
                    severity = ConflictSeverity.LOW
                elif difference <= 1.0:
                    severity = ConflictSeverity.MEDIUM
                elif difference <= 2.0:
                    severity = ConflictSeverity.HIGH
                else:
                    severity = ConflictSeverity.CRITICAL

                conflict = ConflictAnalysis(
                    plan_name=primary_eval.plan_name,
                    criterion=criterion,
                    primary_score=primary_score_obj.score,
                    secondary_score=secondary_score_obj.score,
                    difference=difference,
                    severity=severity,
                    primary_rationale=primary_score_obj.rationale,
                    secondary_rationale=secondary_score_obj.rationale,
                    confidence_delta=0.0,  # Placeholder for now
                )

                conflicts.append(conflict)

        return conflicts

    def _calculate_judge_reliability_factor(self, conflict: ConflictAnalysis) -> float:
        """Calculate judge reliability factor for this specific conflict"""
        # Simplified implementation - could be enhanced with more sophisticated analysis
        return 0.5  # Neutral factor

    def _perform_consistency_check(self, conflict: ConflictAnalysis) -> float:
        """Perform consistency check against historical patterns"""
        # Simplified implementation
        return 0.5

    def _validate_against_benchmarks(self, conflict: ConflictAnalysis) -> float:
        """Validate scores against external benchmarks"""
        # Simplified implementation
        return 0.5

    def _detect_systematic_bias(self, conflict: ConflictAnalysis) -> float:
        """Detect systematic bias in judge evaluations"""
        # Simplified implementation
        return 0.1  # Low bias detected

    def _calculate_composite_resolution(
        self, conflict: ConflictAnalysis, factors: Dict
    ) -> float:
        """Calculate composite resolution score from multiple factors"""
        # Weighted average of the two scores based on factors
        primary_weight = sum(factors.values()) / len(factors)
        secondary_weight = 1.0 - primary_weight

        composite = (
            conflict.primary_score * primary_weight
            + conflict.secondary_score * secondary_weight
        )
        return composite

    def _log_escalation(self, escalation_data: Dict):
        """Log escalation for human review (placeholder implementation)"""
        # In production, this would integrate with logging/ticketing system
        print(
            f"ESCALATION: {escalation_data['conflict'].plan_name} - {escalation_data['conflict'].criterion}"
        )

    def _generate_judge_performance_analysis(
        self, conflicts: List[ConflictAnalysis]
    ) -> str:
        """Generate analysis of judge performance from conflicts"""
        return "Judge performance analysis would be generated here based on conflict patterns."


class MetaEvaluationSystem:
    """
    System for evaluating and improving judge performance over time
    """

    def __init__(self):
        self.evaluation_history = []
        self.performance_metrics = {}

    def track_judge_performance(self, evaluation_session: Dict):
        """Track judge performance metrics across evaluations"""
        self.evaluation_history.append(evaluation_session)
        self._update_performance_metrics()

    def identify_bias_patterns(self) -> Dict[str, List[str]]:
        """Identify systematic bias patterns in judge evaluations"""
        bias_patterns = {"gemini": [], "gpt4": []}

        # Analyze scoring patterns
        for judge in ["gemini", "gpt4"]:
            judge_scores = self._extract_judge_scores(judge)

            # Check for systematic biases
            if self._detect_criterion_bias(judge_scores, "Strategic Prioritization"):
                bias_patterns[judge].append("Overweights strategic considerations")

            if self._detect_score_clustering(judge_scores):
                bias_patterns[judge].append(
                    "Tends to cluster scores around specific values"
                )

            if self._detect_severity_bias(judge_scores):
                bias_patterns[judge].append("Systematically lenient/harsh scoring")

        return bias_patterns

    def generate_calibration_recommendations(self) -> List[str]:
        """Generate recommendations for improving judge calibration"""
        recommendations = []

        bias_patterns = self.identify_bias_patterns()

        for judge, biases in bias_patterns.items():
            if biases:
                recommendations.append(
                    f"Recalibrate {judge} to address: {', '.join(biases)}"
                )

        # Additional recommendations based on performance analysis
        if self._detect_inconsistency():
            recommendations.append("Implement consistency checking mechanisms")

        if self._detect_confidence_issues():
            recommendations.append("Enhance evidence validation requirements")

        return recommendations

    def _update_performance_metrics(self):
        """Update performance metrics based on evaluation history"""
        # Placeholder implementation
        pass

    def _extract_judge_scores(self, judge: str) -> List[float]:
        """Extract scores for a specific judge from evaluation history"""
        # Placeholder implementation
        return [7.0, 8.0, 6.5, 7.5]  # Mock scores

    def _detect_criterion_bias(self, scores: List[float], criterion: str) -> bool:
        """Detect bias toward specific criterion"""
        # Placeholder implementation
        return False

    def _detect_score_clustering(self, scores: List[float]) -> bool:
        """Detect clustering of scores around specific values"""
        # Placeholder implementation
        return False

    def _detect_severity_bias(self, scores: List[float]) -> bool:
        """Detect systematic leniency or harshness in scoring"""
        # Placeholder implementation
        return False

    def _detect_inconsistency(self) -> bool:
        """Detect inconsistency in evaluation patterns"""
        # Placeholder implementation
        return False

    def _detect_confidence_issues(self) -> bool:
        """Detect confidence issues in evaluations"""
        # Placeholder implementation
        return False
