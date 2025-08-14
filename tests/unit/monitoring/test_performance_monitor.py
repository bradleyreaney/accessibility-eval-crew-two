"""
Test-Driven Development Tests for Performance Monitoring System
Tests for Phase 5: Advanced Features & Optimization - Performance Monitoring

Following TDD approach:
1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor and improve
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

from src.monitoring.performance_monitor import (
    CacheManager,
    PerformanceMetrics,
    PerformanceMonitor,
)


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass"""

    def test_performance_metrics_creation(self):
        """Test creating PerformanceMetrics instance"""
        timestamp = datetime.now()
        metrics = PerformanceMetrics(
            timestamp=timestamp,
            memory_usage_mb=1024.5,
            cpu_usage_percent=75.2,
            response_time_ms=2500.0,
            active_agents=3,
            queue_length=5,
            tokens_processed=1000,
            api_calls_made=25,
            cache_hit_rate=0.85,
        )

        assert metrics.timestamp == timestamp
        assert metrics.memory_usage_mb == 1024.5
        assert metrics.cpu_usage_percent == 75.2
        assert metrics.response_time_ms == 2500.0
        assert metrics.active_agents == 3
        assert metrics.queue_length == 5
        assert metrics.tokens_processed == 1000
        assert metrics.api_calls_made == 25
        assert metrics.cache_hit_rate == 0.85


class TestPerformanceMonitor:
    """Test Performance Monitor functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.monitor = PerformanceMonitor()

    def test_monitor_initialization(self):
        """Test performance monitor initializes correctly"""
        monitor = PerformanceMonitor()

        assert monitor is not None
        assert hasattr(monitor, "metrics_history")
        assert hasattr(monitor, "performance_thresholds")
        assert isinstance(monitor.metrics_history, list)
        assert isinstance(monitor.performance_thresholds, dict)

        # Check that thresholds are set
        assert "max_memory_mb" in monitor.performance_thresholds
        assert "max_cpu_percent" in monitor.performance_thresholds
        assert "max_response_time_ms" in monitor.performance_thresholds
        assert "min_cache_hit_rate" in monitor.performance_thresholds

    def test_start_monitoring_session(self):
        """Test starting a monitoring session"""
        session_id = "test_session_001"
        self.monitor.start_monitoring_session(session_id)

        assert hasattr(self.monitor, "current_session")
        assert self.monitor.current_session["session_id"] == session_id
        assert "start_time" in self.monitor.current_session
        assert "metrics" in self.monitor.current_session

    @patch("src.monitoring.performance_monitor.psutil")
    def test_record_metrics_basic(self, mock_psutil):
        """Test recording basic system metrics"""
        # Mock psutil calls
        mock_psutil.virtual_memory.return_value.used = 2048 * 1024 * 1024  # 2GB
        mock_psutil.cpu_percent.return_value = 65.5

        custom_metrics = {
            "response_time_ms": 1500,
            "active_agents": 2,
            "tokens_processed": 500,
        }

        metrics = self.monitor.record_metrics(custom_metrics)

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.memory_usage_mb == 2048.0
        assert metrics.cpu_usage_percent == 65.5
        assert metrics.response_time_ms == 1500
        assert metrics.active_agents == 2
        assert metrics.tokens_processed == 500

        # Check that metrics were added to history
        assert len(self.monitor.metrics_history) == 1
        assert self.monitor.metrics_history[0] == metrics

    @patch("src.monitoring.performance_monitor.psutil")
    def test_record_metrics_without_custom(self, mock_psutil):
        """Test recording metrics without custom data"""
        # Mock psutil calls
        mock_psutil.virtual_memory.return_value.used = 1024 * 1024 * 1024  # 1GB
        mock_psutil.cpu_percent.return_value = 45.0

        metrics = self.monitor.record_metrics()

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.memory_usage_mb == 1024.0
        assert metrics.cpu_usage_percent == 45.0
        assert metrics.response_time_ms == 0
        assert metrics.active_agents == 0

    @patch("src.monitoring.performance_monitor.psutil")
    def test_performance_threshold_warnings(self, mock_psutil):
        """Test that performance threshold violations generate warnings"""
        # Mock high resource usage
        mock_psutil.virtual_memory.return_value.used = (
            5000 * 1024 * 1024
        )  # 5GB (over threshold)
        mock_psutil.cpu_percent.return_value = 95.0  # Over 80% threshold

        custom_metrics = {
            "response_time_ms": 35000,  # Over 30 second threshold
            "cache_hit_rate": 0.5,  # Under 0.7 threshold
        }

        with patch.object(self.monitor.logger, "warning") as mock_warning:
            self.monitor.record_metrics(custom_metrics)

            # Should have logged multiple warnings
            assert mock_warning.call_count >= 3

    def test_generate_performance_report_empty(self):
        """Test generating performance report with no data"""
        report = self.monitor.generate_performance_report()

        assert "error" in report
        assert "No metrics available" in report["error"]

    @patch("src.monitoring.performance_monitor.psutil")
    def test_generate_performance_report_with_data(self, mock_psutil):
        """Test generating performance report with metrics data"""
        # Mock psutil and record some metrics
        mock_psutil.virtual_memory.return_value.used = 2048 * 1024 * 1024
        mock_psutil.cpu_percent.return_value = 60.0

        # Record multiple metrics over time
        for i in range(3):
            custom_metrics = {
                "response_time_ms": 2000 + i * 500,
                "active_agents": 2 + i,
                "cache_hit_rate": 0.8 + i * 0.05,
            }
            self.monitor.record_metrics(custom_metrics)

        report = self.monitor.generate_performance_report()

        assert isinstance(report, dict)
        assert "time_period" in report
        assert "memory_analysis" in report
        assert "cpu_analysis" in report
        assert "response_time_analysis" in report
        assert "throughput_analysis" in report
        assert "optimization_recommendations" in report

    def test_generate_performance_report_time_window(self):
        """Test generating performance report with time window filter"""
        # Add some old metrics
        old_timestamp = datetime.now() - timedelta(hours=2)
        old_metrics = PerformanceMetrics(
            timestamp=old_timestamp,
            memory_usage_mb=1000,
            cpu_usage_percent=50,
            response_time_ms=1000,
            active_agents=1,
            queue_length=0,
            tokens_processed=100,
            api_calls_made=10,
            cache_hit_rate=0.7,
        )
        self.monitor.metrics_history.append(old_metrics)

        # Add recent metrics
        recent_timestamp = datetime.now() - timedelta(minutes=5)
        recent_metrics = PerformanceMetrics(
            timestamp=recent_timestamp,
            memory_usage_mb=2000,
            cpu_usage_percent=70,
            response_time_ms=2000,
            active_agents=2,
            queue_length=1,
            tokens_processed=200,
            api_calls_made=20,
            cache_hit_rate=0.8,
        )
        self.monitor.metrics_history.append(recent_metrics)

        # Generate report for last 30 minutes
        report = self.monitor.generate_performance_report(timedelta(minutes=30))

        assert isinstance(report, dict)
        # Should only include recent metrics
        assert report["time_period"]["duration_minutes"] < 1

    def test_analyze_memory_usage(self):
        """Test memory usage analysis"""
        # Create test metrics
        metrics = [
            PerformanceMetrics(datetime.now(), 1000, 50, 1000, 1, 0, 100, 10, 0.7),
            PerformanceMetrics(datetime.now(), 1500, 60, 1500, 2, 1, 150, 15, 0.75),
            PerformanceMetrics(datetime.now(), 2000, 70, 2000, 3, 2, 200, 20, 0.8),
        ]

        analysis = self.monitor._analyze_memory_usage(metrics)

        assert isinstance(analysis, dict)
        assert "average_mb" in analysis
        assert "peak_mb" in analysis
        assert "min_mb" in analysis
        assert "growth_rate_mb_per_hour" in analysis

        assert analysis["average_mb"] == 1500.0  # (1000 + 1500 + 2000) / 3
        assert analysis["peak_mb"] == 2000.0
        assert analysis["min_mb"] == 1000.0

    def test_generate_optimization_recommendations(self):
        """Test optimization recommendations generation"""
        # Create metrics that trigger various recommendations
        high_memory_metrics = [
            PerformanceMetrics(datetime.now(), 3000, 50, 1000, 1, 0, 100, 10, 0.9),
            PerformanceMetrics(datetime.now(), 3500, 55, 1200, 1, 0, 120, 12, 0.85),
        ]

        recommendations = self.monitor._generate_optimization_recommendations(
            high_memory_metrics
        )

        assert isinstance(recommendations, list)
        assert any("memory pooling" in rec for rec in recommendations)
        assert any("garbage collection" in rec for rec in recommendations)

    def test_optimization_recommendations_cpu(self):
        """Test CPU optimization recommendations"""
        high_cpu_metrics = [
            PerformanceMetrics(datetime.now(), 1000, 80, 1000, 1, 0, 100, 10, 0.9),
            PerformanceMetrics(datetime.now(), 1000, 85, 1000, 1, 0, 100, 10, 0.9),
        ]

        recommendations = self.monitor._generate_optimization_recommendations(
            high_cpu_metrics
        )

        assert any("parallel processing" in rec for rec in recommendations)
        assert any("asyncio" in rec for rec in recommendations)

    def test_optimization_recommendations_response_time(self):
        """Test response time optimization recommendations"""
        slow_response_metrics = [
            PerformanceMetrics(datetime.now(), 1000, 50, 20000, 1, 0, 100, 10, 0.9),
            PerformanceMetrics(datetime.now(), 1000, 50, 18000, 1, 0, 100, 10, 0.9),
        ]

        recommendations = self.monitor._generate_optimization_recommendations(
            slow_response_metrics
        )

        assert any("caching" in rec for rec in recommendations)
        assert any("streaming" in rec for rec in recommendations)

    def test_optimization_recommendations_cache(self):
        """Test cache optimization recommendations"""
        low_cache_metrics = [
            PerformanceMetrics(datetime.now(), 1000, 50, 1000, 1, 0, 100, 10, 0.3),
            PerformanceMetrics(datetime.now(), 1000, 50, 1000, 1, 0, 100, 10, 0.4),
        ]

        recommendations = self.monitor._generate_optimization_recommendations(
            low_cache_metrics
        )

        assert any("cache size" in rec for rec in recommendations)
        assert any("Pre-cache" in rec for rec in recommendations)


class TestCacheManager:
    """Test Cache Manager functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.cache_manager = CacheManager(max_cache_size_mb=100)

    def test_cache_manager_initialization(self):
        """Test cache manager initializes correctly"""
        cache_manager = CacheManager(max_cache_size_mb=256)

        assert cache_manager is not None
        assert cache_manager.max_cache_size_mb == 256
        assert isinstance(cache_manager.cache, dict)
        assert isinstance(cache_manager.cache_metadata, dict)
        assert cache_manager.current_cache_size_mb == 0
        assert cache_manager.hit_count == 0
        assert cache_manager.miss_count == 0

    def test_get_cache_key(self):
        """Test cache key generation"""
        audit_content = "Sample audit content"
        plan_content = "Sample plan content"
        evaluation_type = "primary"

        key1 = self.cache_manager.get_cache_key(
            audit_content, plan_content, evaluation_type
        )
        key2 = self.cache_manager.get_cache_key(
            audit_content, plan_content, evaluation_type
        )
        key3 = self.cache_manager.get_cache_key(
            "Different", plan_content, evaluation_type
        )

        assert isinstance(key1, str)
        assert len(key1) == 32  # MD5 hash length
        assert key1 == key2  # Same inputs should produce same key
        assert key1 != key3  # Different inputs should produce different keys

    def test_cache_result_and_get(self):
        """Test caching and retrieving results"""
        cache_key = "test_key_001"
        test_result = {"score": 7.5, "rationale": "Good plan"}

        # Cache the result
        self.cache_manager.cache_result(cache_key, test_result, size_estimate_mb=1.0)

        # Retrieve the result
        retrieved_result = self.cache_manager.get_cached_result(cache_key)

        assert retrieved_result == test_result
        assert self.cache_manager.hit_count == 1
        assert self.cache_manager.miss_count == 0
        assert self.cache_manager.current_cache_size_mb == 1.0

    def test_cache_miss(self):
        """Test cache miss scenario"""
        result = self.cache_manager.get_cached_result("nonexistent_key")

        assert result is None
        assert self.cache_manager.hit_count == 0
        assert self.cache_manager.miss_count == 1

    def test_cache_size_management(self):
        """Test cache size management and eviction"""
        # Fill cache to near capacity
        for i in range(8):  # Use 8 items of 12MB each = 96MB (under 100MB limit)
            key = f"test_key_{i:03d}"
            result = {"data": f"result_{i}"}
            self.cache_manager.cache_result(key, result, size_estimate_mb=12.0)

        # Should be near capacity
        assert self.cache_manager.current_cache_size_mb >= 90

        # Add one more item that should trigger eviction
        self.cache_manager.cache_result(
            "final_key", {"data": "final"}, size_estimate_mb=15.0
        )

        # Cache should have evicted some items to make room
        assert self.cache_manager.current_cache_size_mb <= 105  # Allow some overhead
        assert "final_key" in self.cache_manager.cache

    def test_cache_statistics(self):
        """Test cache statistics calculation"""
        # Cache some items and access them
        self.cache_manager.cache_result("key1", {"data": "test1"}, 5.0)
        self.cache_manager.cache_result("key2", {"data": "test2"}, 10.0)

        self.cache_manager.get_cached_result("key1")  # Hit
        self.cache_manager.get_cached_result("key2")  # Hit
        self.cache_manager.get_cached_result("key3")  # Miss

        stats = self.cache_manager.get_cache_statistics()

        assert isinstance(stats, dict)
        assert "hit_rate" in stats
        assert "total_entries" in stats
        assert "current_size_mb" in stats
        assert "max_size_mb" in stats
        assert "utilization_percent" in stats

        # Hit rate should be 2/3 = 0.667
        assert abs(stats["hit_rate"] - 0.667) < 0.01
        assert stats["total_entries"] == 2
        assert stats["current_size_mb"] == 15.0
        assert stats["max_size_mb"] == 100.0
        assert stats["utilization_percent"] == 15.0

    def test_cache_access_tracking(self):
        """Test that cache access is properly tracked"""
        cache_key = "access_test_key"
        test_result = {"data": "access_test"}

        # Cache the result
        self.cache_manager.cache_result(cache_key, test_result, 1.0)

        # Access it multiple times
        for i in range(3):
            self.cache_manager.get_cached_result(cache_key)

        # Check metadata
        metadata = self.cache_manager.cache_metadata[cache_key]
        assert metadata["access_count"] == 3
        assert "last_accessed" in metadata
        assert "created_at" in metadata

    def test_eviction_lru_strategy(self):
        """Test that least recently used items are evicted first"""
        # Fill cache with items
        for i in range(5):
            key = f"lru_test_{i}"
            self.cache_manager.cache_result(key, {"data": i}, 25.0)

        # Access some items to update their last_accessed time
        self.cache_manager.get_cached_result("lru_test_1")
        self.cache_manager.get_cached_result("lru_test_3")

        # Add item that should trigger eviction
        self.cache_manager.cache_result("new_item", {"data": "new"}, 30.0)

        # Items 1 and 3 should still be in cache (recently accessed)
        assert self.cache_manager.get_cached_result("lru_test_1") is not None
        assert self.cache_manager.get_cached_result("lru_test_3") is not None
        assert self.cache_manager.get_cached_result("new_item") is not None
