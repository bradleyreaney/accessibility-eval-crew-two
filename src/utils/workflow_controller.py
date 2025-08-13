"""
Workflow controller for managing evaluation execution and status tracking.

This module provides the WorkflowController class that orchestrates the
evaluation workflow, tracks progress, and manages status updates for the UI.

References:
    - Phase 4 Plan: Workflow Controller requirements
    - Master Plan: Workflow orchestration
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator

from ..config.crew_config import AccessibilityEvaluationCrew
from ..models.evaluation_models import EvaluationInput


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

    Attributes:
        crew: The AccessibilityEvaluationCrew instance
        current_status: Current workflow status
        current_task: Currently running asyncio task
    """

    def __init__(self, crew: AccessibilityEvaluationCrew):
        """
        Initialize the workflow controller.

        Args:
            crew: Configured AccessibilityEvaluationCrew instance
        """
        self.crew = crew
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
        Start an evaluation workflow asynchronously.

        Args:
            evaluation_input: The evaluation input with audit report and plans
            mode: Execution mode ("sequential" or "parallel")
            include_consensus: Whether to include consensus building

        Returns:
            Asyncio Task representing the running evaluation
        """
        # Update status to running
        self.current_status = WorkflowStatus(
            status="running",
            progress=10,
            phase=WorkflowPhase.INDIVIDUAL_EVALUATIONS,
            started_at=datetime.now(),
        )

        # Create and start the evaluation task
        self.current_task = asyncio.create_task(
            self._run_evaluation_workflow(evaluation_input, mode, include_consensus)
        )

        return self.current_task

    async def _run_evaluation_workflow(
        self, evaluation_input: EvaluationInput, mode: str, include_consensus: bool
    ) -> Dict[str, Any]:
        """
        Internal method to run the evaluation workflow with progress tracking.

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
            # Phase 1: Individual Evaluations (10-40%)
            self._update_progress(40, WorkflowPhase.INDIVIDUAL_EVALUATIONS)

            # Phase 2: Cross-Plan Comparison (40-60%)
            self._update_progress(60, WorkflowPhase.CROSS_PLAN_COMPARISON)

            # Phase 3: Consensus Building (60-75%) - if enabled
            if include_consensus:
                self._update_progress(75, WorkflowPhase.CONSENSUS_BUILDING)

            # Phase 4: Plan Synthesis (75-90%)
            self._update_progress(90, WorkflowPhase.PLAN_SYNTHESIS)

            # Run the actual evaluation
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
            )
            raise

    def _update_progress(self, progress: int, phase: WorkflowPhase) -> None:
        """
        Update the current workflow progress and phase.

        Args:
            progress: Progress percentage (0-100)
            phase: Current workflow phase
        """
        self.current_status = WorkflowStatus(
            status="running",
            progress=progress,
            phase=phase.value,
            started_at=self.current_status.started_at,
        )

    def stop_evaluation(self) -> None:
        """
        Stop the currently running evaluation.

        Cancels the current task if running and updates status.
        """
        if self.current_task and self.current_status.status == "running":
            self.current_task.cancel()
            self.current_status = WorkflowStatus(
                status="cancelled",
                progress=self.current_status.progress,
                phase=self.current_status.phase,
                started_at=self.current_status.started_at,
            )

    def estimate_time(self, evaluation_input: EvaluationInput) -> int:
        """
        Estimate the time required for evaluation in minutes.

        Args:
            evaluation_input: The evaluation input to estimate time for

        Returns:
            Estimated time in minutes
        """
        # Base time estimation logic
        base_time = 3  # Base 3 minutes

        # Add time based on number of plans (1 minute per additional plan)
        plan_count = len(evaluation_input.remediation_plans)
        plan_time = max(0, plan_count - 1) * 1

        # Add time based on total page count (0.1 minutes per page)
        total_pages = evaluation_input.audit_report.page_count
        total_pages += sum(
            plan.page_count for plan in evaluation_input.remediation_plans.values()
        )
        page_time = int(total_pages * 0.1)

        return base_time + plan_time + page_time
