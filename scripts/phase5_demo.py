#!/usr/bin/env python3
"""
Phase 5 Demonstration Script
Showcases Advanced Features & Optimization capabilities

This script demonstrates:
1. Advanced Consensus Mechanisms
2. Batch Processing System
3. Performance Monitoring
4. Integration between systems
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

import batch.batch_processor as batch_module

# Import directly using absolute imports once src is in path
import consensus.advanced_consensus as consensus_module
import models.evaluation_models as models_module
import monitoring.performance_monitor as monitor_module

# Get classes from modules
AdvancedConsensusEngine = consensus_module.AdvancedConsensusEngine
MetaEvaluationSystem = consensus_module.MetaEvaluationSystem
ConflictAnalysis = consensus_module.ConflictAnalysis
ConflictSeverity = consensus_module.ConflictSeverity

BatchProcessor = batch_module.BatchProcessor
HistoricalAnalysis = batch_module.HistoricalAnalysis

PerformanceMonitor = monitor_module.PerformanceMonitor
CacheManager = monitor_module.CacheManager

PlanEvaluation = models_module.PlanEvaluation
JudgmentScore = models_module.JudgmentScore


def create_sample_evaluations() -> List[PlanEvaluation]:
    """Create sample evaluations with realistic conflicts"""
    return [
        PlanEvaluation(
            plan_name="Comprehensive WCAG Plan",
            judge_id="gemini",
            scores=[
                JudgmentScore(
                    criterion="Strategic Prioritization",
                    score=7.5,
                    rationale="Well-structured strategic approach with clear prioritization of WCAG Level AA requirements",
                    confidence=0.9,
                ),
                JudgmentScore(
                    criterion="Technical Specificity",
                    score=6.5,
                    rationale="Good technical implementation details with code examples",
                    confidence=0.8,
                ),
                JudgmentScore(
                    criterion="Comprehensiveness",
                    score=8.0,
                    rationale="Covers most accessibility requirements comprehensively",
                    confidence=0.85,
                ),
            ],
            overall_score=7.3,
            detailed_analysis="Strong plan with good strategic approach and comprehensive coverage",
            pros=[
                "Clear prioritization",
                "Comprehensive coverage",
                "Good technical details",
            ],
            cons=["Could use more specific implementation examples"],
        ),
        PlanEvaluation(
            plan_name="Comprehensive WCAG Plan",
            judge_id="gpt4",
            scores=[
                JudgmentScore(
                    criterion="Strategic Prioritization",
                    score=6.8,
                    rationale="Adequate strategic framework but could benefit from clearer prioritization",
                    confidence=0.85,
                ),
                JudgmentScore(
                    criterion="Technical Specificity",
                    score=7.2,
                    rationale="Strong technical approach with specific ARIA implementations and CSS modifications",
                    confidence=0.9,
                ),
                JudgmentScore(
                    criterion="Comprehensiveness",
                    score=7.3,
                    rationale="Good coverage but missing some edge cases for screen reader compatibility",
                    confidence=0.88,
                ),
            ],
            overall_score=7.1,
            detailed_analysis="Solid plan with strong technical specificity but room for strategic improvement",
            pros=["Strong technical specificity", "Good ARIA implementation details"],
            cons=[
                "Strategic prioritization could be clearer",
                "Missing some edge cases",
            ],
        ),
    ]


def demonstrate_consensus_mechanisms():
    """Demonstrate advanced consensus building"""
    print("🔄 ADVANCED CONSENSUS MECHANISMS DEMO")
    print("=" * 50)

    # Initialize consensus engine
    consensus_engine = AdvancedConsensusEngine()

    # Create sample evaluations
    evaluations = create_sample_evaluations()

    print(f"📊 Analyzing conflicts between {len(evaluations)} judge evaluations...")

    # Analyze conflicts
    conflicts = consensus_engine.analyze_conflicts(evaluations)

    print(f"⚠️  Detected {len(conflicts)} conflicts:")
    for conflict in conflicts:
        print(f"   • {conflict.plan_name} - {conflict.criterion}")
        print(
            f"     Gemini: {conflict.primary_score} | GPT-4: {conflict.secondary_score}"
        )
        print(
            f"     Difference: {conflict.difference:.2f} (Severity: {conflict.severity.value})"
        )
        print()

    # Resolve conflicts
    print("🔧 Resolving conflicts using appropriate strategies...")
    resolutions = consensus_engine.resolve_conflicts(conflicts)

    print(f"✅ Resolved {len(resolutions)} plan evaluations:")
    for plan_name, criteria_scores in resolutions.items():
        print(f"   📋 {plan_name}:")
        for criterion, resolved_score in criteria_scores.items():
            print(f"      • {criterion}: {resolved_score}")

    # Generate consensus report
    print("\n📄 Generating consensus report...")
    report = consensus_engine.generate_consensus_report(conflicts, resolutions)
    print(report[:500] + "..." if len(report) > 500 else report)

    # Demonstrate evidence quality assessment
    print("\n🔍 EVIDENCE QUALITY ASSESSMENT")
    print("-" * 30)

    high_quality_rationale = "This plan provides specific examples of WCAG implementation with detailed code snippets, CSS modifications, and ARIA attributes for improved accessibility"
    low_quality_rationale = "Good approach"

    high_score = consensus_engine._score_evidence_quality(high_quality_rationale)
    low_score = consensus_engine._score_evidence_quality(low_quality_rationale)

    print(f"High-quality evidence score: {high_score:.3f}")
    print(f"Low-quality evidence score: {low_score:.3f}")
    print(f"Quality difference: {high_score - low_score:.3f}")

    return consensus_engine, conflicts, resolutions


async def demonstrate_batch_processing():
    """Demonstrate batch processing capabilities"""
    print("\n\n🔄 BATCH PROCESSING SYSTEM DEMO")
    print("=" * 50)

    # Initialize batch processor
    mock_crew_manager = Mock()
    batch_processor = BatchProcessor(mock_crew_manager, max_concurrent_jobs=2)

    # Submit multiple batch jobs
    print("📤 Submitting batch jobs...")

    job_ids = []
    audit_reports = [Path(f"sample_audit_{i}.pdf") for i in range(3)]
    plan_directories = [Path(f"plans_set_{i}/") for i in range(3)]

    job_id = batch_processor.submit_batch_job(
        name="Q4 Accessibility Evaluations",
        audit_reports=audit_reports,
        plan_directories=plan_directories,
    )
    job_ids.append(job_id)

    print(f"   ✅ Job submitted: {job_id}")

    # Check job status
    status = batch_processor.get_batch_status(job_id)
    if status:
        print(f"   📊 Status: {status['status']}")
        print(f"   📁 Audit reports: {status['audit_count']}")
        print(f"   📂 Plan sets: {status['plan_set_count']}")
    else:
        print("   📊 Status: Submitted and queued for processing")
        print(f"   📁 Audit reports: {len(audit_reports)}")
        print(f"   📂 Plan sets: {len(plan_directories)}")

    # Mock processing with sample results
    async def mock_process_audit_plan(audit_path, plan_dir, session_id):
        # Simulate processing time
        await asyncio.sleep(0.1)
        return {
            "plan_scores": {"Plan A": 7.5, "Plan B": 6.8, "Plan C": 8.2},
            "session_id": session_id,
            "processing_time": 2.5,
        }

    # Get the job and process it
    job = batch_processor.job_queue[0]

    # Mock the processing method
    original_method = batch_processor._process_audit_plan_combination
    batch_processor._process_audit_plan_combination = mock_process_audit_plan

    print("\n🔄 Processing batch job...")
    try:
        results = await batch_processor.process_batch_job(job)

        print(f"✅ Batch processing completed!")
        print(f"   📊 Individual results: {len(results['individual_results'])}")
        print(
            f"   📈 Total evaluations: {results['batch_summary']['total_evaluations']}"
        )

        # Display summary
        summary = results["batch_summary"]
        if summary["average_scores"]:
            print(
                f"   🏆 Best performing plan: {summary['best_performing_plans']['overall']['plan']}"
            )
            print(
                f"      Average score: {summary['best_performing_plans']['overall']['average_score']:.2f}"
            )

    finally:
        # Restore original method
        batch_processor._process_audit_plan_combination = original_method

    # Export results
    print("\n📤 Exporting results...")
    json_export = batch_processor.export_batch_results(job_id, "json")
    print(f"   📄 JSON export size: {len(json_export)} characters")

    csv_export = batch_processor.export_batch_results(job_id, "csv")
    newline_count = csv_export.count("\n")
    print(f"   📊 CSV export: {newline_count} rows")

    return batch_processor, results if "results" in locals() else {}


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring system"""
    print("\n\n📊 PERFORMANCE MONITORING DEMO")
    print("=" * 50)

    # Initialize performance monitor
    monitor = PerformanceMonitor()

    # Start monitoring session
    monitor.start_monitoring_session("phase5_demo")
    print("🚀 Started monitoring session: phase5_demo")

    # Simulate different system states
    print("\n📈 Recording performance metrics...")

    # Initial state
    initial_metrics = monitor.record_metrics(
        {
            "active_agents": 0,
            "queue_length": 0,
            "tokens_processed": 0,
            "api_calls_made": 0,
            "cache_hit_rate": 0,
        }
    )
    print(
        f"   📊 Initial: Memory: {initial_metrics.memory_usage_mb:.1f}MB, CPU: {initial_metrics.cpu_usage_percent:.1f}%"
    )

    # Processing state
    processing_metrics = monitor.record_metrics(
        {
            "active_agents": 3,
            "queue_length": 2,
            "tokens_processed": 1500,
            "api_calls_made": 25,
            "response_time_ms": 2500,
            "cache_hit_rate": 0.75,
        }
    )
    print(
        f"   🔄 Processing: Agents: {processing_metrics.active_agents}, Response: {processing_metrics.response_time_ms}ms"
    )

    # Completion state
    final_metrics = monitor.record_metrics(
        {
            "active_agents": 0,
            "queue_length": 0,
            "tokens_processed": 3000,
            "api_calls_made": 50,
            "response_time_ms": 800,
            "cache_hit_rate": 0.85,
        }
    )
    print(
        f"   ✅ Final: Cache hit rate: {final_metrics.cache_hit_rate:.2%}, Tokens: {final_metrics.tokens_processed}"
    )

    # Generate performance report
    print("\n📄 Generating performance report...")
    report = monitor.generate_performance_report()

    print(f"   ⏱️  Duration: {report['time_period']['duration_minutes']:.2f} minutes")
    print(
        f"   💾 Memory - Avg: {report['memory_analysis']['average_mb']:.1f}MB, Peak: {report['memory_analysis']['peak_mb']:.1f}MB"
    )
    print(
        f"   🖥️  CPU - Avg: {report['cpu_analysis']['average_percent']:.1f}%, Peak: {report['cpu_analysis']['peak_percent']:.1f}%"
    )
    print(
        f"   🚀 Throughput: {report['throughput_analysis']['tokens_per_minute']:.0f} tokens/min"
    )

    # Show optimization recommendations
    recommendations = report["optimization_recommendations"]
    if recommendations:
        print(f"   💡 Optimization recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"      {i}. {rec}")

    # Demonstrate cache manager
    print("\n🗄️  CACHE MANAGER DEMO")
    print("-" * 30)

    cache_manager = CacheManager(max_cache_size_mb=50)

    # Cache some results
    audit_content = "Sample audit report content..."
    plan_content = "Sample remediation plan content..."

    cache_key = cache_manager.get_cache_key(audit_content, plan_content, "primary")
    cache_manager.cache_result(cache_key, {"score": 7.5, "rationale": "Good plan"}, 2.0)

    # Test cache hit
    cached_result = cache_manager.get_cached_result(cache_key)
    print(f"   ✅ Cache hit: {cached_result is not None}")

    # Test cache miss
    miss_result = cache_manager.get_cached_result("nonexistent_key")
    print(f"   ❌ Cache miss: {miss_result is None}")

    # Show cache statistics
    stats = cache_manager.get_cache_statistics()
    print(
        f"   📊 Cache stats: Hit rate: {stats['hit_rate']:.2%}, Size: {stats['current_size_mb']:.1f}MB"
    )

    return monitor, cache_manager


def demonstrate_integration():
    """Demonstrate integration between all Phase 5 systems"""
    print("\n\n🔗 INTEGRATED SYSTEM DEMO")
    print("=" * 50)

    print("🔄 Running complete Phase 5 workflow...")

    # Initialize all systems
    consensus_engine = AdvancedConsensusEngine()
    meta_system = MetaEvaluationSystem()
    monitor = PerformanceMonitor()

    # Start monitoring
    monitor.start_monitoring_session("integrated_demo")

    # Create evaluation scenario
    evaluations = create_sample_evaluations()

    # Record initial metrics
    monitor.record_metrics({"active_agents": 2, "tokens_processed": 0})

    # Run consensus analysis
    conflicts = consensus_engine.analyze_conflicts(evaluations)
    resolutions = consensus_engine.resolve_conflicts(conflicts)

    # Track performance
    monitor.record_metrics(
        {
            "active_agents": 1,
            "tokens_processed": 2000,
            "response_time_ms": 1800,
            "cache_hit_rate": 0.80,
        }
    )

    # Add to meta-evaluation system
    session_data = {
        "session_id": "integrated_demo",
        "timestamp": datetime.now().isoformat(),
        "conflicts_detected": len(conflicts),
        "conflicts_resolved": len(resolutions),
        "judge_evaluations": {
            "gemini": {"consistency": 0.85, "avg_response_time": 1.2},
            "gpt4": {"consistency": 0.82, "avg_response_time": 1.5},
        },
    }
    meta_system.track_judge_performance(session_data)

    # Generate final reports
    performance_report = monitor.generate_performance_report()
    bias_patterns = meta_system.identify_bias_patterns()
    calibration_recs = meta_system.generate_calibration_recommendations()

    print(f"   ✅ Processed {len(evaluations)} evaluations")
    print(f"   ⚠️  Detected {len(conflicts)} conflicts")
    print(f"   🔧 Resolved {len(resolutions)} automatically")
    print(f"   📊 Generated performance insights")
    print(f"   🎯 Identified {len(calibration_recs)} calibration recommendations")

    # Show system health
    if performance_report["optimization_recommendations"]:
        print(
            f"   💡 System optimization opportunities: {len(performance_report['optimization_recommendations'])}"
        )
    else:
        print(f"   ✅ System performing optimally")

    print("\n🏆 Phase 5 integration demonstration completed successfully!")


async def main():
    """Main demonstration function"""
    print("🚀 PHASE 5: ADVANCED FEATURES & OPTIMIZATION DEMO")
    print("=" * 60)
    print("Demonstrating enterprise-grade enhancements to the")
    print("LLM as a Judge accessibility evaluation system")
    print("=" * 60)

    try:
        # Run individual component demos
        consensus_engine, conflicts, resolutions = demonstrate_consensus_mechanisms()
        batch_processor, batch_results = await demonstrate_batch_processing()
        monitor, cache_manager = demonstrate_performance_monitoring()

        # Run integration demo
        demonstrate_integration()

        print("\n" + "=" * 60)
        print("🎉 PHASE 5 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nPhase 5 Features Demonstrated:")
        print("✅ Advanced Consensus Mechanisms")
        print("   • Multi-level conflict resolution")
        print("   • Evidence quality assessment")
        print("   • Judge reliability scoring")
        print("   • Human escalation for critical conflicts")
        print("\n✅ Batch Processing System")
        print("   • Multi-audit parallel processing")
        print("   • Progress tracking and status management")
        print("   • Result aggregation and analysis")
        print("   • Multiple export formats")
        print("\n✅ Performance Monitoring")
        print("   • Real-time system metrics")
        print("   • Intelligent caching system")
        print("   • Optimization recommendations")
        print("   • Resource usage analysis")
        print("\n✅ System Integration")
        print("   • Seamless component interaction")
        print("   • End-to-end workflow optimization")
        print("   • Enterprise-ready architecture")
        print("\n🚀 System ready for production deployment!")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
