"""
Performance monitoring and optimization system
References: Master Plan - Performance Considerations

Phase 5: Advanced Features & Optimization - Performance Monitoring
"""

import hashlib
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil


@dataclass
class PerformanceMetrics:
    """Data structure for performance metrics"""

    timestamp: datetime
    memory_usage_mb: float
    cpu_usage_percent: float
    response_time_ms: float
    active_agents: int
    queue_length: int
    tokens_processed: int
    api_calls_made: int
    cache_hit_rate: float


class PerformanceMonitor:
    """
    Monitors system performance and provides optimization recommendations
    """

    def __init__(self):
        self.metrics_history = []
        self.performance_thresholds = {
            "max_memory_mb": 4096,
            "max_cpu_percent": 80,
            "max_response_time_ms": 30000,
            "min_cache_hit_rate": 0.7,
        }
        self.logger = logging.getLogger(__name__)

    def start_monitoring_session(self, session_id: str):
        """Start monitoring a specific evaluation session"""
        self.current_session = {
            "session_id": session_id,
            "start_time": datetime.now(),
            "metrics": [],
        }

    def record_metrics(self, custom_metrics: Optional[Dict[str, Any]] = None):
        """Record current system performance metrics"""
        current_metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            memory_usage_mb=psutil.virtual_memory().used / (1024 * 1024),
            cpu_usage_percent=psutil.cpu_percent(interval=1),
            response_time_ms=(
                custom_metrics.get("response_time_ms", 0) if custom_metrics else 0
            ),
            active_agents=(
                custom_metrics.get("active_agents", 0) if custom_metrics else 0
            ),
            queue_length=custom_metrics.get("queue_length", 0) if custom_metrics else 0,
            tokens_processed=(
                custom_metrics.get("tokens_processed", 0) if custom_metrics else 0
            ),
            api_calls_made=(
                custom_metrics.get("api_calls_made", 0) if custom_metrics else 0
            ),
            cache_hit_rate=(
                custom_metrics.get("cache_hit_rate", 0) if custom_metrics else 0
            ),
        )

        self.metrics_history.append(current_metrics)

        # Check for performance issues
        self._check_performance_thresholds(current_metrics)

        return current_metrics

    def _check_performance_thresholds(self, metrics: PerformanceMetrics):
        """Check if any performance thresholds are exceeded"""
        warnings = []

        if metrics.memory_usage_mb > self.performance_thresholds["max_memory_mb"]:
            warnings.append(f"High memory usage: {metrics.memory_usage_mb:.1f}MB")

        if metrics.cpu_usage_percent > self.performance_thresholds["max_cpu_percent"]:
            warnings.append(f"High CPU usage: {metrics.cpu_usage_percent:.1f}%")

        if (
            metrics.response_time_ms
            > self.performance_thresholds["max_response_time_ms"]
        ):
            warnings.append(f"Slow response time: {metrics.response_time_ms:.0f}ms")

        if (
            metrics.cache_hit_rate < self.performance_thresholds["min_cache_hit_rate"]
            and metrics.cache_hit_rate > 0
        ):
            warnings.append(f"Low cache hit rate: {metrics.cache_hit_rate:.2f}")

        for warning in warnings:
            self.logger.warning(f"Performance threshold exceeded: {warning}")

    def generate_performance_report(
        self, time_window: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive performance analysis report"""
        if time_window:
            cutoff_time = datetime.now() - time_window
            relevant_metrics = [
                m for m in self.metrics_history if m.timestamp >= cutoff_time
            ]
        else:
            relevant_metrics = self.metrics_history

        if not relevant_metrics:
            return {"error": "No metrics available for the specified time window"}

        return {
            "time_period": {
                "start": relevant_metrics[0].timestamp,
                "end": relevant_metrics[-1].timestamp,
                "duration_minutes": (
                    relevant_metrics[-1].timestamp - relevant_metrics[0].timestamp
                ).total_seconds()
                / 60,
            },
            "memory_analysis": self._analyze_memory_usage(relevant_metrics),
            "cpu_analysis": self._analyze_cpu_usage(relevant_metrics),
            "response_time_analysis": self._analyze_response_times(relevant_metrics),
            "throughput_analysis": self._analyze_throughput(relevant_metrics),
            "optimization_recommendations": self._generate_optimization_recommendations(
                relevant_metrics
            ),
        }

    def _analyze_memory_usage(
        self, metrics: List[PerformanceMetrics]
    ) -> Dict[str, float]:
        """Analyze memory usage patterns"""
        memory_values = [m.memory_usage_mb for m in metrics]

        return {
            "average_mb": sum(memory_values) / len(memory_values),
            "peak_mb": max(memory_values),
            "min_mb": min(memory_values),
            "growth_rate_mb_per_hour": self._calculate_growth_rate(
                metrics, "memory_usage_mb"
            ),
        }

    def _analyze_cpu_usage(self, metrics: List[PerformanceMetrics]) -> Dict[str, float]:
        """Analyze CPU usage patterns"""
        cpu_values = [m.cpu_usage_percent for m in metrics]

        return {
            "average_percent": sum(cpu_values) / len(cpu_values),
            "peak_percent": max(cpu_values),
            "min_percent": min(cpu_values),
        }

    def _analyze_response_times(
        self, metrics: List[PerformanceMetrics]
    ) -> Dict[str, float]:
        """Analyze response time patterns"""
        response_times = [m.response_time_ms for m in metrics if m.response_time_ms > 0]

        if not response_times:
            return {"average_ms": 0, "peak_ms": 0, "min_ms": 0}

        return {
            "average_ms": sum(response_times) / len(response_times),
            "peak_ms": max(response_times),
            "min_ms": min(response_times),
        }

    def _analyze_throughput(
        self, metrics: List[PerformanceMetrics]
    ) -> Dict[str, float]:
        """Analyze system throughput patterns"""
        if not metrics:
            return {"tokens_per_minute": 0, "api_calls_per_minute": 0}

        duration_minutes = (
            metrics[-1].timestamp - metrics[0].timestamp
        ).total_seconds() / 60
        if duration_minutes == 0:
            duration_minutes = 1  # Avoid division by zero

        total_tokens = sum(m.tokens_processed for m in metrics)
        total_api_calls = sum(m.api_calls_made for m in metrics)

        return {
            "tokens_per_minute": total_tokens / duration_minutes,
            "api_calls_per_minute": total_api_calls / duration_minutes,
        }

    def _generate_optimization_recommendations(
        self, metrics: List[PerformanceMetrics]
    ) -> List[str]:
        """Generate specific optimization recommendations based on performance data"""
        recommendations = []

        # Memory optimization
        avg_memory = sum(m.memory_usage_mb for m in metrics) / len(metrics)
        if avg_memory > 2048:
            recommendations.append(
                "Consider implementing memory pooling for agent instances"
            )
            recommendations.append(
                "Enable garbage collection optimization for long-running evaluations"
            )

        # CPU optimization
        avg_cpu = sum(m.cpu_usage_percent for m in metrics) / len(metrics)
        if avg_cpu > 60:
            recommendations.append(
                "Implement parallel processing for independent evaluation tasks"
            )
            recommendations.append("Consider CPU-bound task optimization with asyncio")

        # Response time optimization
        response_times = [m.response_time_ms for m in metrics if m.response_time_ms > 0]
        if response_times and sum(response_times) / len(response_times) > 15000:
            recommendations.append(
                "Implement request caching for similar evaluation inputs"
            )
            recommendations.append(
                "Consider using streaming responses for long evaluations"
            )

        # Cache optimization
        cache_rates = [m.cache_hit_rate for m in metrics if m.cache_hit_rate > 0]
        if cache_rates and sum(cache_rates) / len(cache_rates) < 0.5:
            recommendations.append(
                "Expand cache size and implement smarter cache invalidation"
            )
            recommendations.append("Pre-cache common evaluation patterns and templates")

        return recommendations

    def _calculate_growth_rate(
        self, metrics: List[PerformanceMetrics], attribute: str
    ) -> float:
        """Calculate growth rate for a specific metric attribute"""
        if len(metrics) < 2:
            return 0.0

        values = [getattr(m, attribute) for m in metrics]
        time_span_hours = (
            metrics[-1].timestamp - metrics[0].timestamp
        ).total_seconds() / 3600

        if time_span_hours == 0:
            return 0.0

        growth = values[-1] - values[0]
        return growth / time_span_hours


class CacheManager:
    """
    Intelligent caching system for evaluation results and intermediate data
    """

    def __init__(self, max_cache_size_mb: int = 512):
        self.cache = {}
        self.cache_metadata = {}
        self.max_cache_size_mb = max_cache_size_mb
        self.current_cache_size_mb = 0
        self.hit_count = 0
        self.miss_count = 0

    def get_cache_key(
        self, audit_content: str, plan_content: str, evaluation_type: str
    ) -> str:
        """Generate unique cache key for evaluation input"""
        combined_content = f"{audit_content}:{plan_content}:{evaluation_type}"
        return hashlib.md5(combined_content.encode()).hexdigest()

    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Retrieve cached evaluation result"""
        if cache_key in self.cache:
            # Update access time
            self.cache_metadata[cache_key]["last_accessed"] = datetime.now()
            self.cache_metadata[cache_key]["access_count"] += 1
            self.hit_count += 1

            return self.cache[cache_key]

        self.miss_count += 1
        return None

    def cache_result(self, cache_key: str, result: Any, size_estimate_mb: float = 1.0):
        """Cache evaluation result with size management"""
        # Check if we need to free up space
        if self.current_cache_size_mb + size_estimate_mb > self.max_cache_size_mb:
            self._evict_old_entries(size_estimate_mb)

        # Store result and metadata
        self.cache[cache_key] = result
        self.cache_metadata[cache_key] = {
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "access_count": 0,
            "size_mb": size_estimate_mb,
        }

        self.current_cache_size_mb += size_estimate_mb

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0

        return {
            "hit_rate": hit_rate,
            "total_entries": len(self.cache),
            "current_size_mb": self.current_cache_size_mb,
            "max_size_mb": self.max_cache_size_mb,
            "utilization_percent": (self.current_cache_size_mb / self.max_cache_size_mb)
            * 100,
        }

    def _evict_old_entries(self, space_needed_mb: float):
        """Evict least recently used entries to free up space"""
        # Sort by last accessed time
        sorted_entries = sorted(
            self.cache_metadata.items(), key=lambda x: x[1]["last_accessed"]
        )

        space_freed = 0
        for cache_key, metadata in sorted_entries:
            if space_freed >= space_needed_mb:
                break

            # Remove entry
            del self.cache[cache_key]
            space_freed += metadata["size_mb"]
            self.current_cache_size_mb -= metadata["size_mb"]
            del self.cache_metadata[cache_key]
