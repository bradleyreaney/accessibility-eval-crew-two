"""
Workflow controller for managing evaluation execution and status tracking.

This module provides the WorkflowController class that orchestrates the
evaluation workflow, tracks progress, and manages status updates for the UI.

References:
    - Phase 4 Plan: Workflow Controller requirements
    - Master Plan: Workflow orchestration
    - LLM Error Handling Enhancement Plan - Phase 2
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator

from ..config.crew_config import AccessibilityEvaluationCrew
from ..models.evaluation_models import EvaluationInput
from .llm_resilience_manager import LLMResilienceManager, ResilienceConfig


class WorkflowPhase(str, Enum):
    """Enumeration of workflow phases"""

    INITIALIZATION = "initialization"
    INDIVIDUAL_EVALUATIONS = "individual_evaluations"
    CROSS_PLAN_COMPARISON = "cross_plan_comparison"
    CONSENSUS_BUILDING = "consensus_building"
    PLAN_SYNTHESIS = "plan_synthesis"
    FINAL_COMPILATION = "final_compilation"


class WorkflowStatus(BaseModel):
    """
    Model representing the current status of an evaluation workflow.

    Used by the UI to display progress and provide real-time updates
    to users during evaluation execution.
    """

    status: str = Field(default="idle", description="Current workflow status")
    progress: int = Field(default=0, description="Progress percentage (0-100)")
    phase: str = Field(default="initialization", description="Current execution phase")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    started_at: Optional[datetime] = Field(
        default=None, description="Workflow start time"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Workflow completion time"
    )

    @field_validator("progress")
    @classmethod
    def validate_progress_range(cls, v: int) -> int:
        """Ensure progress is between 0 and 100"""
        if v < 0 or v > 100:
            raise ValueError("Progress must be between 0 and 100")
        return v


class WorkflowController:
    """
    Controller for managing evaluation workflow execution and status tracking.

    This class provides the interface between the UI and the evaluation crew,
    managing asynchronous execution, progress tracking, and error handling.
    Enhanced with LLM resilience capabilities for graceful degradation.

    Attributes:
        crew: The AccessibilityEvaluationCrew instance
        resilience_manager: LLM resilience manager for failure handling
        current_status: Current workflow status
        current_task: Currently running asyncio task
    """

    def __init__(
        self,
        crew: AccessibilityEvaluationCrew,
        resilience_manager: Optional[LLMResilienceManager] = None,
    ):
        """
        Initialize the workflow controller.

        Args:
            crew: Configured AccessibilityEvaluationCrew instance
            resilience_manager: Optional LLM resilience manager for enhanced error handling
        """
        self.crew = crew
        self.resilience_manager = resilience_manager
        self.current_status = WorkflowStatus()
        self.current_task: Optional[asyncio.Task] = None

    def get_status(self) -> WorkflowStatus:
        """
        Get the current workflow status.

        Returns:
            Current WorkflowStatus instance
        """
        return self.current_status

    def start_evaluation(
        self,
        evaluation_input: EvaluationInput,
        mode: str = "sequential",
        include_consensus: bool = True,
    ) -> asyncio.Task:
        """
        Start the evaluation workflow asynchronously.

        Args:
            evaluation_input: The evaluation input
            mode: Execution mode (sequential, parallel)
            include_consensus: Whether to include consensus building

        Returns:
            Asyncio task for the evaluation workflow
        """
        # Update status to running
        self.current_status = WorkflowStatus(
            status="running",
            progress=10,
            phase=WorkflowPhase.INITIALIZATION,
            started_at=datetime.now(),
        )

        # Create and start the async task
        self.current_task = asyncio.create_task(
            self._run_evaluation_workflow(evaluation_input, mode, include_consensus)
        )

        return self.current_task

    async def _run_evaluation_workflow(
        self, evaluation_input: EvaluationInput, mode: str, include_consensus: bool
    ) -> Dict[str, Any]:
        """
        Internal method to run the evaluation workflow with progress tracking.
        Enhanced with LLM resilience capabilities for graceful degradation.

        Args:
            evaluation_input: The evaluation input
            mode: Execution mode
            include_consensus: Whether to include consensus building

        Returns:
            Evaluation results dictionary

        Raises:
            Exception: If evaluation fails
        """
        try:
            # Check LLM availability before starting if resilience manager is available
            availability_status = None
            if self.resilience_manager:
                availability_status = self.resilience_manager.check_llm_availability()

                # Check if we have minimum required LLMs
                available_count = sum(availability_status.values())
                if (
                    available_count
                    < self.resilience_manager.config.minimum_llm_requirement
                ):
                    raise RuntimeError(
                        f"Insufficient LLMs available ({available_count}). "
                        f"Minimum required: {self.resilience_manager.config.minimum_llm_requirement}"
                    )

                # Log availability status
                available_llms = [
                    llm for llm, status in availability_status.items() if status
                ]
                unavailable_llms = [
                    llm for llm, status in availability_status.items() if not status
                ]

                if unavailable_llms:
                    print(
                        f"⚠️  Warning: Some LLMs unavailable: {', '.join(unavailable_llms)}"
                    )
                    print(
                        f"✅ Continuing with available LLMs: {', '.join(available_llms)}"
                    )

            # Phase 1: Individual Evaluations (10-40%)
            self._update_progress(40, WorkflowPhase.INDIVIDUAL_EVALUATIONS)

            # Phase 2: Cross-Plan Comparison (40-60%)
            self._update_progress(60, WorkflowPhase.CROSS_PLAN_COMPARISON)

            # Phase 3: Consensus Building (60-75%) - if enabled
            if include_consensus:
                self._update_progress(75, WorkflowPhase.CONSENSUS_BUILDING)

            # Phase 4: Plan Synthesis (75-90%)
            self._update_progress(90, WorkflowPhase.PLAN_SYNTHESIS)

            # Run the actual evaluation with resilience handling
            if self.resilience_manager:
                results = await self._execute_resilient_evaluation(
                    evaluation_input, mode, availability_status
                )
            else:
                # Fallback to original execution if no resilience manager
                if mode == "parallel":
                    results = self.crew.execute_parallel_evaluation(evaluation_input)
                else:
                    results = self.crew.execute_complete_evaluation(evaluation_input)

            # Phase 5: Final Compilation (90-100%)
            self._update_progress(100, WorkflowPhase.FINAL_COMPILATION)

            # Mark as completed
            self.current_status = WorkflowStatus(
                status="completed",
                progress=100,
                phase=WorkflowPhase.FINAL_COMPILATION,
                started_at=self.current_status.started_at,
                completed_at=datetime.now(),
            )

            return results

        except Exception as e:
            # Mark as failed
            self.current_status = WorkflowStatus(
                status="failed",
                progress=self.current_status.progress,
                phase=self.current_status.phase,
                error=str(e),
                started_at=self.current_status.started_at,
                completed_at=datetime.now(),
            )
            raise

    async def _execute_resilient_evaluation(
        self,
        evaluation_input: EvaluationInput,
        mode: str,
        availability_status: Dict[str, bool],
    ) -> Dict[str, Any]:
        """
        Execute evaluation with LLM resilience handling.

        Args:
            evaluation_input: The evaluation input
            mode: Execution mode
            availability_status: Current LLM availability status

        Returns:
            Evaluation results with resilience information
        """
        # Add availability information to results
        results = {
            "llm_availability": availability_status,
            "resilience_info": {
                "partial_evaluation": not all(availability_status.values()),
                "available_llms": [
                    llm for llm, status in availability_status.items() if status
                ],
                "unavailable_llms": [
                    llm for llm, status in availability_status.items() if not status
                ],
            },
        }

        # Execute evaluation based on mode
        if mode == "parallel":
            evaluation_results = self.crew.execute_parallel_evaluation(evaluation_input)
        else:
            evaluation_results = self.crew.execute_complete_evaluation(evaluation_input)

        # Merge results
        results.update(evaluation_results)

        return results

    def _update_progress(self, progress: int, phase: WorkflowPhase):
        """Update workflow progress and phase"""
        self.current_status.progress = progress
        self.current_status.phase = phase

    def estimate_completion_time(self, evaluation_input: EvaluationInput) -> int:
        """
        Estimate completion time in minutes based on input complexity.

        Args:
            evaluation_input: The evaluation input

        Returns:
            Estimated completion time in minutes
        """
        # Base time for evaluation workflow
        base_time = 5  # minutes

        # Scale based on number of plans
        plan_count = len(evaluation_input.remediation_plans)
        scaled_time = base_time + (plan_count * 2)  # 2 minutes per plan

        # Add time for audit report complexity
        audit_pages = evaluation_input.audit_report.page_count
        scaled_time += max(0, (audit_pages - 5) * 0.5)  # 0.5 minutes per page over 5

        return int(scaled_time)
