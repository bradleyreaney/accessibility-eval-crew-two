"""
LLM Resilience Manager for handling LLM failures and fallback strategies.

This module provides centralized LLM failure management, availability testing,
and graceful degradation when one or more LLMs become unavailable.

References:
    - LLM Error Handling Enhancement Plan - Phase 1.1
    - Master Plan: Error handling and resilience patterns
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..config.llm_config import LLMManager
from ..models.evaluation_models import EvaluationInput
from .llm_exceptions import (
    LLMConnectionError,
    LLMError,
    NoLLMAvailableError,
    PartialEvaluationError,
    classify_llm_error,
)

logger = logging.getLogger(__name__)


class ResilienceConfig(BaseModel):
    """Configuration for LLM resilience features"""

    max_retries: int = 3
    retry_delay_seconds: int = 2
    exponential_backoff: bool = True
    timeout_seconds: int = 30
    enable_partial_evaluation: bool = True
    minimum_llm_requirement: int = 1  # Minimum LLMs required to start evaluation
    na_reporting_enabled: bool = True
    availability_check_timeout: int = 10  # Timeout for availability checks


class LLMStatus(BaseModel):
    """Status information for an LLM"""

    llm_type: str
    available: bool
    last_check: datetime
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    last_failure_reason: Optional[str] = None
    consecutive_failures: int = 0


class LLMResilienceManager:
    """
    Centralized LLM failure management and fallback coordination.

    This class manages LLM availability, handles failures gracefully,
    and provides fallback strategies for partial evaluation scenarios.
    """

    def __init__(
        self, llm_manager: LLMManager, config: Optional[ResilienceConfig] = None
    ):
        """
        Initialize the LLM resilience manager.

        Args:
            llm_manager: LLM configuration manager
            config: Optional resilience configuration
        """
        self.llm_manager = llm_manager
        self.config = config or ResilienceConfig()

        # Initialize status tracking
        self.llm_status: Dict[str, LLMStatus] = {
            "gemini": LLMStatus(
                llm_type="Gemini Pro", available=True, last_check=datetime.now()
            ),
            "openai": LLMStatus(
                llm_type="GPT-4", available=True, last_check=datetime.now()
            ),
        }

        # Track evaluation statistics
        self.evaluation_stats = {
            "total_evaluations": 0,
            "successful_evaluations": 0,
            "failed_evaluations": 0,
            "na_evaluations": 0,
            "partial_evaluations": 0,
        }

    def check_llm_availability(self) -> Dict[str, bool]:
        """
        Test both LLMs and return availability status.

        Returns:
            Dictionary mapping LLM types to availability status
        """
        logger.info("Checking LLM availability...")

        availability = {}

        # Test Gemini Pro
        try:
            gemini_available = self._test_llm_connection("gemini")
            availability["gemini"] = gemini_available
            self._update_llm_status("gemini", gemini_available)
        except Exception as e:
            logger.error(f"Error checking Gemini availability: {e}")
            availability["gemini"] = False
            self._update_llm_status("gemini", False, str(e))

        # Test OpenAI
        try:
            openai_available = self._test_llm_connection("openai")
            availability["openai"] = openai_available
            self._update_llm_status("openai", openai_available)
        except Exception as e:
            logger.error(f"Error checking OpenAI availability: {e}")
            availability["openai"] = False
            self._update_llm_status("openai", False, str(e))

        available_count = sum(availability.values())
        logger.info(f"LLM availability check complete: {available_count}/2 available")

        if available_count < self.config.minimum_llm_requirement:
            logger.warning(
                f"Only {available_count} LLM(s) available, minimum required: {self.config.minimum_llm_requirement}"
            )

        return availability

    def _test_llm_connection(self, llm_type: str) -> bool:
        """
        Test connection to a specific LLM.

        Args:
            llm_type: Type of LLM to test ("gemini" or "openai")

        Returns:
            True if LLM is available, False otherwise
        """
        if llm_type == "gemini":
            llm = self.llm_manager.gemini
            test_prompt = "Hello, this is a connection test. Please respond with 'Connection successful.'"
        elif llm_type == "openai":
            llm = self.llm_manager.openai
            test_prompt = "Hello, this is a connection test. Please respond with 'Connection successful.'"
        else:
            raise ValueError(f"Unknown LLM type: {llm_type}")

        try:
            # Test with timeout
            llm.invoke(test_prompt)
            return True

        except Exception as e:
            logger.debug(f"LLM connection test failed for {llm_type}: {e}")
            return False

    def _update_llm_status(
        self, llm_type: str, available: bool, failure_reason: Optional[str] = None
    ):
        """Update the status of an LLM"""
        status = self.llm_status[llm_type]
        status.last_check = datetime.now()

        if available:
            status.available = True
            status.consecutive_failures = 0
            status.last_failure_reason = None
        else:
            status.available = False
            status.failure_count += 1
            status.consecutive_failures += 1
            status.last_failure = datetime.now()
            status.last_failure_reason = failure_reason

    def safe_llm_invoke(self, llm, prompt: str, llm_type: str) -> Dict[str, Any]:
        """
        Safely invoke LLM with retry logic and error handling.

        Args:
            llm: LLM instance to invoke
            prompt: Prompt to send to LLM
            llm_type: Type of LLM for error classification

        Returns:
            Dictionary with success status and content or error information
        """
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                result = llm.invoke(prompt)
                duration = time.time() - start_time

                logger.debug(
                    f"LLM invocation successful for {llm_type} (attempt {attempt + 1}, {duration:.2f}s)"
                )

                return {
                    "success": True,
                    "content": (
                        result.content if hasattr(result, "content") else str(result)
                    ),
                    "llm_type": llm_type,
                    "attempt": attempt + 1,
                    "duration": duration,
                }

            except Exception as e:
                logger.warning(
                    f"LLM invocation failed for {llm_type} (attempt {attempt + 1}): {e}"
                )

                # Classify the error
                llm_error = classify_llm_error(e, llm_type)

                # If not retryable, fail immediately
                if not llm_error.retryable:
                    logger.error(f"Non-retryable error for {llm_type}: {llm_error}")
                    return {
                        "success": False,
                        "error": str(llm_error),
                        "error_type": llm_error.__class__.__name__,
                        "llm_type": llm_type,
                        "retryable": False,
                        "attempt": attempt + 1,
                    }

                # If this is the last attempt, fail
                if attempt == self.config.max_retries - 1:
                    logger.error(
                        f"All retry attempts failed for {llm_type}: {llm_error}"
                    )
                    return {
                        "success": False,
                        "error": str(llm_error),
                        "error_type": llm_error.__class__.__name__,
                        "llm_type": llm_type,
                        "retryable": True,
                        "attempt": attempt + 1,
                    }

                # Wait before retrying
                if self.config.exponential_backoff:
                    delay = self.config.retry_delay_seconds * (2**attempt)
                else:
                    delay = self.config.retry_delay_seconds

                logger.debug(f"Retrying {llm_type} in {delay} seconds...")
                time.sleep(delay)

        # This should never be reached, but just in case
        return {
            "success": False,
            "error": "Unexpected error in safe_llm_invoke",
            "error_type": "UnknownError",
            "llm_type": llm_type,
            "retryable": False,
            "attempt": self.config.max_retries,
        }

    def mark_evaluation_as_na(
        self, plan_name: str, llm_type: str, reason: Optional[str]
    ) -> Dict[str, Any]:
        """
        Create standardized NA evaluation result.

        Args:
            plan_name: Name of the plan that couldn't be evaluated
            llm_type: Type of LLM that failed
            reason: Reason for the failure (can be None)

        Returns:
            Standardized NA evaluation result
        """
        self.evaluation_stats["na_evaluations"] += 1

        # Handle None reason
        if reason is None:
            reason = "Unknown error"

        # Truncate very long reasons
        if len(reason) > 500:
            reason = reason[:497] + "..."

        return {
            "plan_name": plan_name,
            "evaluator": f"{llm_type.title()} Judge",
            "evaluation_content": None,
            "status": "NA",
            "na_reason": reason,
            "llm_used": llm_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": False,
            "error": reason,
        }

    def execute_with_fallback(
        self, evaluation_input: EvaluationInput
    ) -> Dict[str, Any]:
        """
        Execute evaluation with automatic fallback handling.

        Args:
            evaluation_input: Input data for evaluation

        Returns:
            Evaluation results with fallback handling
        """
        logger.info("Starting evaluation with fallback handling...")

        # Check availability before starting
        availability = self.check_llm_availability()

        if not any(availability.values()):
            raise NoLLMAvailableError(list(availability.keys()))

        # Track evaluation progress
        self.evaluation_stats["total_evaluations"] += len(
            evaluation_input.remediation_plans
        )

        results = {
            "evaluations": [],
            "availability_status": availability,
            "partial_evaluation": False,
            "completion_stats": {
                "total_plans": len(evaluation_input.remediation_plans),
                "completed": 0,
                "na_count": 0,
                "failed_count": 0,
            },
        }

        # Process each plan with available LLMs
        for plan_name, plan_content in evaluation_input.remediation_plans.items():
            plan_result = self._evaluate_plan_with_fallback(
                plan_name, plan_content.content, evaluation_input.audit_report.content
            )
            results["evaluations"].append(plan_result)

            # Update completion stats
            if plan_result.get("status") == "NA":
                results["completion_stats"]["na_count"] += 1
            elif plan_result.get("success"):
                results["completion_stats"]["completed"] += 1
            else:
                results["completion_stats"]["failed_count"] += 1

        # Determine if this was a partial evaluation
        completed = results["completion_stats"]["completed"]
        total = results["completion_stats"]["total_plans"]

        if completed < total:
            results["partial_evaluation"] = True
            self.evaluation_stats["partial_evaluations"] += 1

            completion_rate = (completed / total) * 100
            logger.info(
                f"Partial evaluation completed: {completed}/{total} ({completion_rate:.1f}%)"
            )

        self.evaluation_stats["successful_evaluations"] += completed

        return results

    def evaluate_plan_with_fallback(
        self, plan_name: str, plan_content: str, audit_context: str
    ) -> Dict[str, Any]:
        """
        Public interface for plan evaluation with fallback.

        This is a public alias for _evaluate_plan_with_fallback.
        """
        return self._evaluate_plan_with_fallback(plan_name, plan_content, audit_context)

    def _evaluate_plan_with_fallback(
        self, plan_name: str, plan_content: str, audit_context: str
    ) -> Dict[str, Any]:
        """
        Evaluate a single plan with fallback handling for LLM failures.

        Args:
            plan_name: Name of the plan to evaluate
            plan_content: Content of the remediation plan
            audit_context: Context from the audit report

        Returns:
            Evaluation result with fallback handling
        """
        logger.debug(f"Evaluating plan {plan_name} with fallback handling...")

        # Try primary LLM (Gemini Pro) if available
        if self.llm_status["gemini"].available:
            try:
                result = self.safe_llm_invoke(
                    self.llm_manager.gemini,
                    self._create_evaluation_prompt(
                        plan_name, plan_content, audit_context
                    ),
                    "gemini",
                )

                if result["success"]:
                    return {
                        "plan_name": plan_name,
                        "evaluator": "Primary Judge (Gemini Pro)",
                        "evaluation_content": result["content"],
                        "status": "completed",
                        "llm_used": "gemini",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "success": True,
                    }
                else:
                    logger.warning(
                        f"Primary LLM failed for {plan_name}: {result['error']}"
                    )

            except Exception as e:
                logger.error(f"Unexpected error with primary LLM for {plan_name}: {e}")

        # Try secondary LLM (GPT-4) if available
        if self.llm_status["openai"].available:
            try:
                result = self.safe_llm_invoke(
                    self.llm_manager.openai,
                    self._create_evaluation_prompt(
                        plan_name, plan_content, audit_context
                    ),
                    "openai",
                )

                if result["success"]:
                    return {
                        "plan_name": plan_name,
                        "evaluator": "Secondary Judge (GPT-4)",
                        "evaluation_content": result["content"],
                        "status": "completed",
                        "llm_used": "openai",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "success": True,
                    }
                else:
                    logger.warning(
                        f"Secondary LLM failed for {plan_name}: {result['error']}"
                    )

            except Exception as e:
                logger.error(
                    f"Unexpected error with secondary LLM for {plan_name}: {e}"
                )

        # Both LLMs failed, mark as NA
        logger.warning(f"Both LLMs failed for {plan_name}, marking as NA")
        return self.mark_evaluation_as_na(
            plan_name, "both", "Both primary and secondary LLMs unavailable"
        )

    def _create_evaluation_prompt(
        self, plan_name: str, plan_content: str, audit_context: str
    ) -> str:
        """Create evaluation prompt for LLM"""
        return f"""
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

    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        return {
            "llm_status": {
                llm_type: status.dict() for llm_type, status in self.llm_status.items()
            },
            "evaluation_stats": self.evaluation_stats.copy(),
            "config": self.config.dict(),
            "timestamp": datetime.now().isoformat(),
        }

    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """
        Get evaluation statistics for reporting.

        Returns:
            Dictionary containing evaluation statistics
        """
        return {
            "evaluation_stats": self.evaluation_stats.copy(),
            "llm_availability": {
                llm_type: status.available
                for llm_type, status in self.llm_status.items()
            },
            "failure_counts": {
                llm_type: status.failure_count
                for llm_type, status in self.llm_status.items()
            },
            "consecutive_failures": {
                llm_type: status.consecutive_failures
                for llm_type, status in self.llm_status.items()
            },
            "last_check": {
                llm_type: status.last_check.isoformat()
                for llm_type, status in self.llm_status.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

    def reset_failure_counts(self):
        """Reset failure counts for all LLMs"""
        for status in self.llm_status.values():
            status.failure_count = 0
            status.consecutive_failures = 0
            status.last_failure = None
            status.last_failure_reason = None
        logger.info("LLM failure counts reset")
