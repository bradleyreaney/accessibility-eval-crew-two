"""
Test-Driven Development Tests for Batch Processing System
Tests for Phase 5: Advanced Features & Optimization - Batch Processing

Following TDD approach:
1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor and improve
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.batch.batch_processor import BatchJob, BatchProcessor, HistoricalAnalysis


class TestBatchJob:
    """Test BatchJob dataclass"""

    def test_batch_job_creation(self):
        """Test creating BatchJob instance"""
        audit_reports = [Path("audit1.pdf"), Path("audit2.pdf")]
        plan_directories = [Path("plans1/"), Path("plans2/")]

        job = BatchJob(
            job_id="batch_test_001",
            name="Test Batch",
            audit_reports=audit_reports,
            plan_directories=plan_directories,
        )

        assert job.job_id == "batch_test_001"
        assert job.name == "Test Batch"
        assert job.audit_reports == audit_reports
        assert job.plan_directories == plan_directories
        assert job.status == "pending"
        assert job.created_at is None
        assert job.started_at is None
        assert job.completed_at is None
        assert job.results is None
        assert job.error is None

    def test_batch_job_with_timestamps(self):
        """Test BatchJob with timestamps"""
        now = datetime.now()
        job = BatchJob(
            job_id="batch_test_002",
            name="Test Batch with Time",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
            created_at=now,
        )

        assert job.created_at == now


class TestBatchProcessor:
    """Test Batch Processing Engine functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_crew_manager = Mock()
        self.processor = BatchProcessor(self.mock_crew_manager, max_concurrent_jobs=2)

    def test_processor_initialization(self):
        """Test batch processor initializes correctly"""
        processor = BatchProcessor(Mock(), max_concurrent_jobs=3)

        assert processor is not None
        assert processor.max_concurrent_jobs == 3
        assert hasattr(processor, "active_jobs")
        assert hasattr(processor, "job_queue")
        assert hasattr(processor, "completed_jobs")
        assert isinstance(processor.active_jobs, dict)
        assert isinstance(processor.job_queue, list)
        assert isinstance(processor.completed_jobs, dict)

    def test_submit_batch_job(self):
        """Test submitting a new batch job"""
        audit_reports = [Path("audit1.pdf"), Path("audit2.pdf")]
        plan_directories = [Path("plans1/"), Path("plans2/")]

        job_id = self.processor.submit_batch_job(
            name="Test Batch Job",
            audit_reports=audit_reports,
            plan_directories=plan_directories,
        )

        assert isinstance(job_id, str)
        assert job_id.startswith("batch_")
        assert len(self.processor.job_queue) == 1

        submitted_job = self.processor.job_queue[0]
        assert submitted_job.name == "Test Batch Job"
        assert submitted_job.audit_reports == audit_reports
        assert submitted_job.plan_directories == plan_directories

    @pytest.mark.asyncio
    async def test_process_batch_job_success(self):
        """Test successful batch job processing"""
        # Create test job
        job = BatchJob(
            job_id="test_job_001",
            name="Test Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
        )

        # Mock the audit/plan combination processing
        with patch.object(
            self.processor, "_process_audit_plan_combination"
        ) as mock_process:
            mock_process.return_value = {"plan_scores": {"Plan A": 7.5, "Plan B": 6.0}}

            results = await self.processor.process_batch_job(job)

        assert job.status == "completed"
        assert job.started_at is not None
        assert job.completed_at is not None
        assert results is not None
        assert "individual_results" in results
        assert "batch_summary" in results

    @pytest.mark.asyncio
    async def test_process_batch_job_failure(self):
        """Test batch job processing with error"""
        # Create test job
        job = BatchJob(
            job_id="test_job_002",
            name="Failing Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
        )

        # Mock the audit/plan combination processing to raise an error
        with patch.object(
            self.processor, "_process_audit_plan_combination"
        ) as mock_process:
            mock_process.side_effect = Exception("Processing failed")

            with pytest.raises(Exception):
                await self.processor.process_batch_job(job)

        assert job.status == "failed"
        assert job.error == "Processing failed"
        assert job.completed_at is not None

    def test_get_batch_status_active_job(self):
        """Test getting status of active batch job"""
        # Add job to active jobs
        job = BatchJob(
            job_id="active_job_001",
            name="Active Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
            status="running",
            created_at=datetime.now(),
        )
        self.processor.active_jobs["active_job_001"] = job

        status = self.processor.get_batch_status("active_job_001")

        assert status is not None
        assert status["job_id"] == "active_job_001"
        assert status["name"] == "Active Job"
        assert status["status"] == "running"
        assert status["audit_count"] == 1
        assert status["plan_set_count"] == 1

    def test_get_batch_status_completed_job(self):
        """Test getting status of completed batch job"""
        # Add job to completed jobs
        job = BatchJob(
            job_id="completed_job_001",
            name="Completed Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
            status="completed",
            created_at=datetime.now(),
            completed_at=datetime.now(),
        )
        self.processor.completed_jobs["completed_job_001"] = job

        status = self.processor.get_batch_status("completed_job_001")

        assert status is not None
        assert status["status"] == "completed"
        assert status["completed_at"] is not None

    def test_get_batch_status_nonexistent_job(self):
        """Test getting status of non-existent job"""
        status = self.processor.get_batch_status("nonexistent_job")
        assert status is None

    def test_list_all_jobs_empty(self):
        """Test listing jobs when no jobs exist"""
        jobs = self.processor.list_all_jobs()
        assert isinstance(jobs, list)
        assert len(jobs) == 0

    def test_list_all_jobs_with_jobs(self):
        """Test listing jobs when jobs exist"""
        # Add jobs to different states
        queued_job = BatchJob(
            job_id="queued_001",
            name="Queued Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
            created_at=datetime.now(),
        )
        self.processor.job_queue.append(queued_job)

        active_job = BatchJob(
            job_id="active_001",
            name="Active Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
            status="running",
            created_at=datetime.now(),
        )
        self.processor.active_jobs["active_001"] = active_job

        completed_job = BatchJob(
            job_id="completed_001",
            name="Completed Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
            status="completed",
            created_at=datetime.now(),
            completed_at=datetime.now(),
        )
        self.processor.completed_jobs["completed_001"] = completed_job

        jobs = self.processor.list_all_jobs()

        assert len(jobs) == 3

        # Check that queued job has queue position
        queued_info = next((j for j in jobs if j["job_id"] == "queued_001"), None)
        assert queued_info is not None
        assert "queue_position" in queued_info

    def test_generate_batch_summary(self):
        """Test batch summary generation"""
        # Mock batch results
        batch_results = {
            "audit1": Mock(plan_scores={"Plan A": 7.5, "Plan B": 6.0}),
            "audit2": Mock(plan_scores={"Plan A": 8.0, "Plan B": 7.0}),
        }

        summary = self.processor._generate_batch_summary(batch_results)

        assert isinstance(summary, dict)
        assert "total_evaluations" in summary
        assert summary["total_evaluations"] == 2
        assert "average_scores" in summary
        assert "best_performing_plans" in summary
        assert "consistency_metrics" in summary
        assert "recommendations" in summary

    def test_calculate_std_dev(self):
        """Test standard deviation calculation"""
        scores = [7.0, 8.0, 6.0, 9.0, 7.5]
        std_dev = self.processor._calculate_std_dev(scores)

        assert isinstance(std_dev, float)
        assert std_dev >= 0

    def test_calculate_std_dev_edge_cases(self):
        """Test standard deviation calculation with edge cases"""
        # Test with empty list
        std_dev = self.processor._calculate_std_dev([])
        assert std_dev == 0.0

        # Test with single value (should return 0.0 per line 269)
        std_dev = self.processor._calculate_std_dev([7.5])
        assert std_dev == 0.0

    def test_export_batch_results_json(self):
        """Test exporting batch results in JSON format"""
        # Create completed job with results
        job = BatchJob(
            job_id="export_test_001",
            name="Export Test",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
            status="completed",
            results={"test": "data"},
        )
        self.processor.completed_jobs["export_test_001"] = job

        exported_data = self.processor.export_batch_results("export_test_001", "json")

        assert isinstance(exported_data, str)
        assert "test" in exported_data
        assert "data" in exported_data

    def test_export_batch_results_unsupported_format(self):
        """Test exporting batch results in unsupported format"""
        # Create completed job with results
        job = BatchJob(
            job_id="export_test_002",
            name="Export Test",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
            status="completed",
            results={"test": "data"},
        )
        self.processor.completed_jobs["export_test_002"] = job

        with pytest.raises(ValueError, match="Unsupported export format"):
            self.processor.export_batch_results("export_test_002", "xml")

    def test_export_batch_results_no_results(self):
        """Test exporting when no results exist"""
        with pytest.raises(ValueError, match="No completed results found"):
            self.processor.export_batch_results("nonexistent_job", "json")


class TestHistoricalAnalysis:
    """Test Historical Analysis functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.analysis = HistoricalAnalysis()

    def test_historical_analysis_initialization(self):
        """Test historical analysis system initializes correctly"""
        analysis = HistoricalAnalysis()

        assert analysis is not None
        assert hasattr(analysis, "evaluation_database")
        assert isinstance(analysis.evaluation_database, list)
        assert len(analysis.evaluation_database) == 0

    def test_add_batch_results(self):
        """Test adding batch results to historical database"""
        batch_results = {
            "audit1": {"plan_scores": {"Plan A": 7.5}},
            "audit2": {"plan_scores": {"Plan B": 6.0}},
        }

        initial_count = len(self.analysis.evaluation_database)
        self.analysis.add_batch_results(batch_results)

        assert len(self.analysis.evaluation_database) == initial_count + 1

        added_entry = self.analysis.evaluation_database[-1]
        assert "timestamp" in added_entry
        assert "results" in added_entry
        assert added_entry["results"] == batch_results

    def test_analyze_trends_all_time(self):
        """Test analyzing trends for all time"""
        # Add some sample data
        self.analysis.evaluation_database = [
            {
                "timestamp": datetime.now() - timedelta(days=30),
                "results": {
                    "individual_results": {"audit1": Mock(plan_scores={"Plan A": 7.0})}
                },
            },
            {
                "timestamp": datetime.now() - timedelta(days=15),
                "results": {
                    "individual_results": {"audit2": Mock(plan_scores={"Plan A": 8.0})}
                },
            },
        ]

        trends = self.analysis.analyze_trends("all")

        assert isinstance(trends, dict)
        assert "plan_performance_trends" in trends
        assert "judge_consistency_trends" in trends
        assert "improvement_opportunities" in trends

    def test_analyze_trends_time_period_filtering(self):
        """Test analyzing trends with time period filtering"""
        # Add data with different timestamps
        old_data = {
            "timestamp": datetime.now() - timedelta(days=60),
            "results": {
                "individual_results": {"audit1": Mock(plan_scores={"Plan A": 5.0})}
            },
        }
        recent_data = {
            "timestamp": datetime.now() - timedelta(days=5),
            "results": {
                "individual_results": {"audit2": Mock(plan_scores={"Plan A": 8.0})}
            },
        }

        self.analysis.evaluation_database = [old_data, recent_data]

        # Test that filtering works
        recent_trends = self.analysis.analyze_trends("last_week")
        all_trends = self.analysis.analyze_trends("all")

        assert isinstance(recent_trends, dict)
        assert isinstance(all_trends, dict)

    def test_generate_benchmark_scores_empty_data(self):
        """Test generating benchmark scores with no data"""
        benchmarks = self.analysis.generate_benchmark_scores()

        assert isinstance(benchmarks, dict)
        assert len(benchmarks) == 0

    def test_generate_benchmark_scores_with_data(self):
        """Test generating benchmark scores with evaluation data"""
        # Add sample evaluation data
        mock_audit_result = Mock()
        mock_audit_result.plan_scores = {"Plan A": 7.0, "Plan B": 8.0, "Plan C": 6.0}

        self.analysis.evaluation_database = [
            {
                "timestamp": datetime.now(),
                "results": {"individual_results": {"audit1": mock_audit_result}},
            }
        ]

        benchmarks = self.analysis.generate_benchmark_scores()

        assert isinstance(benchmarks, dict)
        assert "excellent_threshold" in benchmarks
        assert "good_threshold" in benchmarks
        assert "average_threshold" in benchmarks
        assert "below_average_threshold" in benchmarks

        # Check that thresholds are in logical order
        if benchmarks:
            assert benchmarks["excellent_threshold"] >= benchmarks["good_threshold"]
            assert benchmarks["good_threshold"] >= benchmarks["average_threshold"]
            assert (
                benchmarks["average_threshold"] >= benchmarks["below_average_threshold"]
            )

    def test_percentile_calculation(self):
        """Test percentile calculation method"""
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

        p50 = self.analysis._percentile(values, 50)
        p90 = self.analysis._percentile(values, 90)

        assert p50 == 5.5  # Median of 1-10
        assert p90 == 9.1  # 90th percentile of 1-10 (calculated correctly)


class TestBatchProcessorIntegration:
    """Integration tests for batch processing system"""

    @pytest.mark.asyncio
    async def test_complete_batch_workflow(self):
        """Test complete batch processing workflow"""
        mock_crew_manager = Mock()
        processor = BatchProcessor(mock_crew_manager, max_concurrent_jobs=1)

        # Submit a batch job
        audit_reports = [Path("audit1.pdf")]
        plan_directories = [Path("plans1/")]

        job_id = processor.submit_batch_job(
            name="Integration Test Batch",
            audit_reports=audit_reports,
            plan_directories=plan_directories,
        )

        # Verify job was queued
        assert len(processor.job_queue) == 1

        # Get the job and process it
        job = processor.job_queue[0]

        with patch.object(processor, "_process_audit_plan_combination") as mock_process:
            mock_process.return_value = {"plan_scores": {"Plan A": 7.5}}

            results = await processor.process_batch_job(job)

        # Verify results
        assert job.status == "completed"
        assert results is not None
        assert "individual_results" in results
        assert "batch_summary" in results

        # Test status retrieval
        status = processor.get_batch_status(job_id)
        assert status is not None
        assert status["status"] == "completed"

    def test_batch_processor_error_handling(self):
        """Test error handling in batch processor"""
        mock_crew_manager = Mock()
        processor = BatchProcessor(mock_crew_manager)

        # Test invalid export format
        with pytest.raises(ValueError):
            processor.export_batch_results("fake_job", "invalid_format")

        # Test non-existent job status
        status = processor.get_batch_status("non_existent_job")
        assert status is None

    def test_concurrent_job_limits(self):
        """Test that concurrent job limits are respected"""
        mock_crew_manager = Mock()
        processor = BatchProcessor(mock_crew_manager, max_concurrent_jobs=2)

        assert processor.max_concurrent_jobs == 2
        assert hasattr(processor, "executor")

        # Verify executor was created with correct max workers
        assert processor.executor._max_workers == 2


class TestBatchProcessorAdditionalCoverage:
    """Additional tests to improve batch processor coverage"""

    def test_export_batch_results_markdown(self):
        """Test markdown export format"""
        processor = BatchProcessor(Mock())

        # Create a job with results including batch_summary
        job = BatchJob(
            job_id="test_job",
            name="Test Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
        )
        job.results = {
            "batch_summary": {
                "total_evaluations": 5,
                "average_scores": {
                    "Plan A": {"mean": 8.5, "std_dev": 0.3},
                    "Plan B": {"mean": 7.2, "std_dev": 0.8},
                },
            },
            "individual_results": {},
        }
        processor.completed_jobs["test_job"] = job

        result = processor.export_batch_results("test_job", "markdown")

        assert "# Batch Evaluation Results" in result
        assert "Total Evaluations: 5" in result
        assert "Plan A**: 8.50" in result
        assert "Plan B**: 7.20" in result

    def test_export_batch_results_csv_with_plan_scores(self):
        """Test CSV export with plan scores"""
        processor = BatchProcessor(Mock())

        # Create mock audit result with plan_scores attribute
        mock_audit_result = Mock()
        mock_audit_result.plan_scores = {"Plan A": 8.5, "Plan B": 7.2}

        job = BatchJob(
            job_id="test_job",
            name="Test Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
        )
        job.results = {"individual_results": {"audit1": mock_audit_result}}
        processor.completed_jobs["test_job"] = job

        result = processor.export_batch_results("test_job", "csv")

        assert "Plan,Score,Audit" in result
        assert "Plan A,8.5,audit1" in result
        assert "Plan B,7.2,audit1" in result

    def test_generate_batch_recommendations(self):
        """Test batch recommendation generation"""
        processor = BatchProcessor(Mock())

        batch_results = {"test": "data"}
        summary = {
            "total_evaluations": 5,
            "average_scores": {"Plan A": {"mean": 8.5}, "Plan B": {"mean": 6.0}},
            "consistency_metrics": {
                "Plan A_consistency": 0.9,
                "Plan B_consistency": 0.5,
            },
        }

        recommendations = processor._generate_batch_recommendations(
            batch_results, summary
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_calculate_consistency_metrics_single_score(self):
        """Test consistency calculation with single scores"""
        processor = BatchProcessor(Mock())

        all_plan_scores = {
            "Plan A": [8.5],  # Single score
            "Plan B": [7.0, 7.5, 6.5],  # Multiple scores
        }

        metrics = processor._calculate_consistency_metrics(all_plan_scores)

        assert "Plan A_consistency" in metrics
        assert "Plan B_consistency" in metrics
        assert (
            metrics["Plan A_consistency"] == 1.0
        )  # Single score = perfect consistency

    def test_calculate_consistency_metrics_multiple_scores(self):
        """Test consistency calculation with multiple scores"""
        processor = BatchProcessor(Mock())

        all_plan_scores = {
            "Plan A": [8.0, 8.0, 8.0],  # Very consistent
            "Plan B": [5.0, 9.0, 6.0],  # Less consistent
        }

        metrics = processor._calculate_consistency_metrics(all_plan_scores)

        assert metrics["Plan A_consistency"] > metrics["Plan B_consistency"]


class TestHistoricalAnalysisAdditionalCoverage:
    """Additional tests for HistoricalAnalysis coverage"""

    def test_analyze_trends_time_period_edge_cases(self):
        """Test time period filtering edge cases"""
        analyzer = HistoricalAnalysis()

        # Add some old data by directly adding to the database
        # (since add_batch_results always uses current timestamp)
        old_timestamp = datetime.now() - timedelta(days=400)
        analyzer.evaluation_database.append(
            {
                "timestamp": old_timestamp,
                "results": {
                    "batch_summary": {"average_scores": {"Plan A": {"mean": 6.0}}}
                },
            }
        )

        # Test last_week filtering
        week_data = analyzer._filter_by_time_period("last_week")
        assert len(week_data) == 0  # No recent data

        # Test last_month filtering
        month_data = analyzer._filter_by_time_period("last_month")
        assert len(month_data) == 0  # No recent data

        # Test default case (last year)
        year_data = analyzer._filter_by_time_period("unknown_period")
        assert len(year_data) == 0  # Data too old

    def test_analyze_plan_trends_with_data(self):
        """Test plan trend analysis with actual data"""
        analyzer = HistoricalAnalysis()

        # Add multiple batch results
        for i in range(3):
            analyzer.add_batch_results(
                {
                    "timestamp": datetime.now() - timedelta(days=i),
                    "batch_summary": {
                        "average_scores": {
                            "Plan A": {"mean": 8.0 + i * 0.1},
                            "Plan B": {"mean": 7.0 - i * 0.1},
                        }
                    },
                }
            )

        data = analyzer.evaluation_database
        trends = analyzer._analyze_plan_trends(data)

        assert isinstance(trends, dict)

    def test_percentile_calculation_edge_cases(self):
        """Test percentile calculation with edge cases"""
        analyzer = HistoricalAnalysis()

        # Test empty list
        result = analyzer._percentile([], 50)
        assert result == 0.0

        # Test single value
        result = analyzer._percentile([5.0], 50)
        assert result == 5.0

        # Test exact percentile index
        result = analyzer._percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50)
        assert result == 3.0

        # Test interpolated percentile
        result = analyzer._percentile([1.0, 2.0, 3.0, 4.0], 25)
        assert result == 1.75

        # Test upper bound edge case
        result = analyzer._percentile([1.0, 2.0], 100)
        assert result == 2.0

    def test_generate_benchmark_scores_edge_cases(self):
        """Test benchmark score generation edge cases"""
        analyzer = HistoricalAnalysis()

        # Test with no data
        benchmarks = analyzer.generate_benchmark_scores()
        assert benchmarks == {}

        # Add data with individual results containing plan_scores
        mock_audit_result = Mock()
        mock_audit_result.plan_scores = {"Plan A": 8.0, "Plan B": 7.5}

        analyzer.evaluation_database.append(
            {
                "timestamp": datetime.now(),
                "results": {"individual_results": {"audit1": mock_audit_result}},
            }
        )

        benchmarks = analyzer.generate_benchmark_scores()
        assert "excellent_threshold" in benchmarks
        assert "good_threshold" in benchmarks
        assert "average_threshold" in benchmarks


class TestAdditionalEdgeCases:
    """Additional tests to cover remaining edge cases"""

    def test_std_dev_with_multiple_scores(self):
        """Test standard deviation calculation with multiple scores"""
        processor = BatchProcessor(Mock())

        # Test with multiple scores (should call statistics.stdev)
        scores = [7.0, 8.0, 9.0, 6.0, 8.5]
        result = processor._calculate_std_dev(scores)

        assert result > 0  # Should have non-zero standard deviation
        assert isinstance(result, float)

    def test_percentile_upper_bound_edge_case(self):
        """Test percentile calculation with upper bound edge case"""
        analyzer = HistoricalAnalysis()

        # Test case where upper_index >= len(sorted_values)
        values = [1.0, 2.0]  # Small list
        result = analyzer._percentile(values, 95)  # High percentile

        # Should handle the upper bound case
        assert result >= 1.0
        assert result <= 2.0

    def test_percentile_exact_upper_bound_condition(self):
        """Test percentile calculation where upper_index exactly equals len(sorted_values)"""
        analyzer = HistoricalAnalysis()

        # Create condition where upper_index >= len(sorted_values) (line 444)
        values = [1.0]  # Single value
        result = analyzer._percentile(values, 100)  # 100th percentile

        # Should return the only value (line 444: return sorted_values[lower_index])
        assert result == 1.0

    def test_percentile_non_integer_index_upper_bound(self):
        """Test percentile with non-integer index that hits upper bound condition"""
        analyzer = HistoricalAnalysis()

        # Test with values that might trigger the edge case
        values = [1.0, 2.0]  # Two values
        result = analyzer._percentile(values, 99)  # High integer percentile

        assert isinstance(result, float)
        assert 1.0 <= result <= 2.0

    def test_export_csv_with_no_plan_scores(self):
        """Test CSV export when audit result has no plan_scores attribute"""
        processor = BatchProcessor(Mock())

        # Create mock audit result without plan_scores attribute
        mock_audit_result = Mock()
        del mock_audit_result.plan_scores  # Remove the attribute

        job = BatchJob(
            job_id="test_job",
            name="Test Job",
            audit_reports=[Path("audit.pdf")],
            plan_directories=[Path("plans/")],
        )
        job.results = {"individual_results": {"audit1": mock_audit_result}}
        processor.completed_jobs["test_job"] = job

        result = processor.export_batch_results("test_job", "csv")

        # Should handle gracefully - just return headers
        assert "Plan,Score,Audit" in result

    def test_calculate_std_dev_multiple_values_path(self):
        """Test standard deviation with multiple values to hit statistics.stdev path"""
        processor = BatchProcessor(Mock())

        # Test with exactly 2 values to ensure len(scores) > 1
        scores = [5.0, 7.0]
        result = processor._calculate_std_dev(scores)

        # Should call statistics.stdev and return non-zero value
        assert result > 0
        import statistics

        expected = statistics.stdev(scores)
        assert abs(result - expected) < 0.0001

    @pytest.mark.asyncio
    async def test_process_audit_plan_combination_async(self):
        """Test the async audit/plan combination processing"""
        processor = BatchProcessor(Mock())

        result = await processor._process_audit_plan_combination(
            audit_path=Path("test_audit.pdf"),
            plan_dir=Path("test_plans/"),
            session_id="test_session_123",
        )

        # Check the mock result structure
        assert "plan_scores" in result
        assert "session_id" in result
        assert "audit_path" in result
        assert "plan_directory" in result
        assert result["session_id"] == "test_session_123"
        assert "test_audit.pdf" in result["audit_path"]
        assert "test_plans" in result["plan_directory"]
