"""
Task definitions package for CrewAI workflow integration.
Phase 3 implementation: Task management for evaluation, comparison, and synthesis.
"""

from .comparison_tasks import ComparisonTaskManager
from .evaluation_tasks import EvaluationTaskManager

__all__ = ["EvaluationTaskManager", "ComparisonTaskManager"]
