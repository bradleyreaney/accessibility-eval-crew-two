# Judge Disagreement & Consensus Strategy
*Enhanced Multi-Judge Resolution for LLM as a Judge System*

**← [Master Plan](./master-plan.md)** | **References: [Phase 5](./phase-5-optimization.md)**

## Overview

This document outlines the comprehensive strategy for handling disagreements between the Gemini Pro and GPT-4 judges, including escalation procedures, resolution mechanisms, and quality assurance measures.

## Disagreement Classification System

### Conflict Severity Levels

#### 1. Low Severity (Score Difference: 0.1 - 0.5)
- **Definition**: Minor scoring variations within acceptable range
- **Frequency**: Expected in 40-60% of evaluations
- **Resolution**: Weighted average based on judge reliability metrics
- **Action**: Automatic resolution, no manual intervention required

#### 2. Medium Severity (Score Difference: 0.6 - 1.0)
- **Definition**: Moderate disagreement requiring analysis
- **Frequency**: Expected in 25-35% of evaluations
- **Resolution**: Evidence-based analysis of judge rationales
- **Action**: Automated analysis with quality scoring, possible re-evaluation

#### 3. High Severity (Score Difference: 1.1 - 2.0)
- **Definition**: Significant disagreement indicating fundamental differences
- **Frequency**: Expected in 10-20% of evaluations
- **Resolution**: Expert mediation algorithm with multiple validation factors
- **Action**: Advanced algorithmic resolution with confidence scoring

#### 4. Critical Severity (Score Difference: > 2.0)
- **Definition**: Extreme disagreement suggesting evaluation issues
- **Frequency**: Expected in 1-5% of evaluations
- **Resolution**: Human expert escalation required
- **Action**: Immediate escalation to accessibility expert review

## Multi-Stage Resolution Process

### Stage 1: Automatic Weighted Resolution (Low Severity)

```python
class WeightedResolution:
    """
    Resolve minor disagreements using judge performance weights
    """
    
    def __init__(self):
        self.judge_weights = {
            'gemini': {
                'strategic_prioritization': 0.52,  # Slightly stronger in strategic thinking
                'technical_specificity': 0.48,    # Slightly weaker in technical details
                'comprehensiveness': 0.50,        # Equal performance
                'long_term_vision': 0.53          # Stronger in future planning
            },
            'gpt4': {
                'strategic_prioritization': 0.48,  # Slightly weaker in strategic thinking
                'technical_specificity': 0.52,    # Stronger in technical details
                'comprehensiveness': 0.50,        # Equal performance
                'long_term_vision': 0.47          # Weaker in future planning
            }
        }
    
    def resolve_conflict(self, conflict: ConflictAnalysis) -> ResolutionResult:
        """
        Resolve conflict using criterion-specific weights
        """
        criterion = conflict.criterion.lower().replace(' ', '_')
        
        gemini_weight = self.judge_weights['gemini'].get(criterion, 0.50)
        gpt4_weight = self.judge_weights['gpt4'].get(criterion, 0.50)
        
        # Weighted average
        resolved_score = (
            conflict.primary_score * gemini_weight +
            conflict.secondary_score * gpt4_weight
        ) / (gemini_weight + gpt4_weight)
        
        return ResolutionResult(
            resolved_score=round(resolved_score, 2),
            resolution_method="weighted_average",
            confidence=self._calculate_confidence(conflict, gemini_weight, gpt4_weight),
            rationale=f"Weighted average using criterion-specific judge strengths"
        )
```

### Stage 2: Evidence-Based Analysis (Medium Severity)

```python
class EvidenceBasedResolution:
    """
    Resolve disagreements by analyzing the quality of judge rationales
    """
    
    def __init__(self):
        self.evidence_analyzer = EvidenceQualityAnalyzer()
        self.consistency_checker = ConsistencyChecker()
        self.bias_detector = BiasDetector()
    
    def resolve_conflict(self, conflict: ConflictAnalysis) -> ResolutionResult:
        """
        Resolve conflict based on evidence quality analysis
        """
        # Analyze evidence quality in each judge's rationale
        primary_evidence = self.evidence_analyzer.score_evidence(
            conflict.primary_rationale, conflict.criterion
        )
        secondary_evidence = self.evidence_analyzer.score_evidence(
            conflict.secondary_rationale, conflict.criterion
        )
        
        # Check consistency with other evaluations
        primary_consistency = self.consistency_checker.check_consistency(
            conflict.primary_score, conflict.plan_name, conflict.criterion
        )
        secondary_consistency = self.consistency_checker.check_consistency(
            conflict.secondary_score, conflict.plan_name, conflict.criterion
        )
        
        # Detect potential bias
        primary_bias = self.bias_detector.detect_bias(
            conflict.primary_rationale, conflict.judge_id
        )
        secondary_bias = self.bias_detector.detect_bias(
            conflict.secondary_rationale, conflict.judge_id
        )
        
        # Calculate composite quality scores
        primary_quality = self._calculate_quality_score(
            primary_evidence, primary_consistency, primary_bias
        )
        secondary_quality = self._calculate_quality_score(
            secondary_evidence, secondary_consistency, secondary_bias
        )
        
        # Resolution logic
        if primary_quality > secondary_quality * 1.2:
            # Primary judge has significantly better evidence
            return self._create_resolution_result(
                conflict.primary_score, "evidence_favors_primary", primary_quality
            )
        elif secondary_quality > primary_quality * 1.2:
            # Secondary judge has significantly better evidence
            return self._create_resolution_result(
                conflict.secondary_score, "evidence_favors_secondary", secondary_quality
            )
        else:
            # Evidence quality is similar, use confidence-weighted average
            return self._confidence_weighted_resolution(conflict, primary_quality, secondary_quality)
```

### Stage 3: Expert Mediation Algorithm (High Severity)

```python
class ExpertMediationEngine:
    """
    Advanced algorithmic mediation for high-severity conflicts
    """
    
    def __init__(self):
        self.benchmark_database = BenchmarkDatabase()
        self.pattern_analyzer = PatternAnalyzer()
        self.domain_expert_simulator = DomainExpertSimulator()
    
    def resolve_conflict(self, conflict: ConflictAnalysis) -> ResolutionResult:
        """
        Resolve high-severity conflicts using expert mediation logic
        """
        # Multi-factor analysis
        analysis_factors = {
            'benchmark_comparison': self._compare_against_benchmarks(conflict),
            'pattern_analysis': self._analyze_scoring_patterns(conflict),
            'domain_expertise': self._simulate_expert_judgment(conflict),
            'historical_precedent': self._check_historical_precedents(conflict),
            'technical_validation': self._validate_technical_accuracy(conflict)
        }
        
        # Weighted decision matrix
        decision_matrix = self._build_decision_matrix(analysis_factors)
        
        # Calculate confidence-weighted resolution
        resolution = self._calculate_expert_mediation_result(decision_matrix, conflict)
        
        return resolution
    
    def _compare_against_benchmarks(self, conflict: ConflictAnalysis) -> Dict[str, float]:
        """
        Compare both scores against established benchmarks
        """
        benchmarks = self.benchmark_database.get_benchmarks(conflict.criterion)
        
        primary_deviation = abs(conflict.primary_score - benchmarks['expected_score'])
        secondary_deviation = abs(conflict.secondary_score - benchmarks['expected_score'])
        
        return {
            'primary_benchmark_alignment': 1.0 / (1.0 + primary_deviation),
            'secondary_benchmark_alignment': 1.0 / (1.0 + secondary_deviation),
            'benchmark_confidence': benchmarks['confidence']
        }
    
    def _simulate_expert_judgment(self, conflict: ConflictAnalysis) -> Dict[str, Any]:
        """
        Simulate how a domain expert would likely resolve this conflict
        """
        expert_factors = {
            'wcag_compliance_accuracy': self._assess_wcag_accuracy(conflict),
            'practical_implementation': self._assess_implementation_feasibility(conflict),
            'user_impact_assessment': self._assess_user_impact_accuracy(conflict),
            'industry_best_practices': self._assess_best_practices_alignment(conflict)
        }
        
        # Weighted expert judgment simulation
        expert_preference = self._calculate_expert_preference(expert_factors)
        
        return {
            'expert_factors': expert_factors,
            'expert_preference': expert_preference,
            'confidence': self._calculate_expert_confidence(expert_factors)
        }
```

### Stage 4: Human Expert Escalation (Critical Severity)

```python
class HumanEscalationSystem:
    """
    System for escalating critical disagreements to human experts
    """
    
    def __init__(self):
        self.expert_pool = AccessibilityExpertPool()
        self.escalation_queue = EscalationQueue()
        self.notification_system = NotificationSystem()
    
    def escalate_conflict(self, conflict: ConflictAnalysis) -> EscalationTicket:
        """
        Create escalation ticket for human expert review
        """
        # Create comprehensive escalation package
        escalation_package = self._create_escalation_package(conflict)
        
        # Assign to appropriate expert
        expert = self._assign_expert(conflict)
        
        # Create escalation ticket
        ticket = EscalationTicket(
            ticket_id=self._generate_ticket_id(),
            conflict=conflict,
            escalation_package=escalation_package,
            assigned_expert=expert,
            priority=self._calculate_priority(conflict),
            deadline=self._calculate_deadline(conflict),
            status="PENDING_REVIEW"
        )
        
        # Add to queue and notify
        self.escalation_queue.add_ticket(ticket)
        self.notification_system.notify_expert(expert, ticket)
        
        return ticket
    
    def _create_escalation_package(self, conflict: ConflictAnalysis) -> EscalationPackage:
        """
        Create comprehensive package for expert review
        """
        return EscalationPackage(
            conflict_summary=self._generate_conflict_summary(conflict),
            judge_rationales={
                'gemini': conflict.primary_rationale,
                'gpt4': conflict.secondary_rationale
            },
            plan_context=self._extract_relevant_plan_context(conflict),
            audit_context=self._extract_relevant_audit_context(conflict),
            automated_analysis=self._run_automated_analysis(conflict),
            similar_cases=self._find_similar_historical_cases(conflict),
            expert_questions=self._generate_expert_review_questions(conflict)
        )
```

## Third Judge Integration (Optional Enhancement)

### Claude-3 as Tie-Breaker Judge

```python
class ThirdJudgeSystem:
    """
    Optional third judge for ultimate tie-breaking in critical cases
    """
    
    def __init__(self, anthropic_api_key: str):
        self.claude_client = AnthropicClient(anthropic_api_key)
        self.activation_threshold = 2.0  # Score difference threshold
        self.confidence_threshold = 0.3  # Low confidence threshold
    
    def should_activate_third_judge(self, conflict: ConflictAnalysis) -> bool:
        """
        Determine if third judge should be activated
        """
        return (
            conflict.severity == ConflictSeverity.CRITICAL or
            conflict.difference >= self.activation_threshold or
            conflict.confidence_delta <= self.confidence_threshold
        )
    
    def invoke_third_judge(self, conflict: ConflictAnalysis, 
                          original_context: EvaluationInput) -> ThirdJudgeResult:
        """
        Invoke Claude-3 as independent third judge
        """
        # Create independent evaluation prompt
        third_judge_prompt = self._create_independent_prompt(
            original_context, conflict.plan_name, blind_evaluation=True
        )
        
        # Get third judge evaluation
        third_evaluation = self.claude_client.evaluate(third_judge_prompt)
        
        # Parse third judge result
        third_score = self._parse_score(third_evaluation)
        third_rationale = self._parse_rationale(third_evaluation)
        
        # Analyze all three scores
        resolution = self._analyze_three_judge_scores(
            conflict.primary_score,
            conflict.secondary_score,
            third_score,
            [conflict.primary_rationale, conflict.secondary_rationale, third_rationale]
        )
        
        return ThirdJudgeResult(
            third_judge_score=third_score,
            third_judge_rationale=third_rationale,
            final_resolution=resolution,
            consensus_level=self._calculate_three_judge_consensus(
                conflict.primary_score, conflict.secondary_score, third_score
            )
        )
```

## Quality Assurance & Validation

### Consensus Quality Metrics

```python
class ConsensusQualityAssurance:
    """
    Monitor and ensure quality of consensus mechanisms
    """
    
    def __init__(self):
        self.quality_metrics = {
            'resolution_accuracy': 0.0,
            'expert_agreement_rate': 0.0,
            'consistency_score': 0.0,
            'bias_detection_rate': 0.0
        }
    
    def validate_resolution(self, resolution: ResolutionResult, 
                          original_conflict: ConflictAnalysis) -> ValidationResult:
        """
        Validate the quality of a consensus resolution
        """
        validation_checks = {
            'score_reasonableness': self._check_score_reasonableness(resolution),
            'rationale_quality': self._assess_rationale_quality(resolution),
            'consistency_check': self._check_consistency(resolution, original_conflict),
            'bias_check': self._check_for_bias(resolution),
            'technical_accuracy': self._validate_technical_accuracy(resolution)
        }
        
        overall_quality = self._calculate_overall_quality(validation_checks)
        
        return ValidationResult(
            validation_checks=validation_checks,
            overall_quality=overall_quality,
            passed=overall_quality >= 0.8,
            recommendations=self._generate_quality_recommendations(validation_checks)
        )
```

## Implementation Timeline

### Phase 3 Integration (Week 3)
- [ ] **Basic Consensus**: Implement weighted averaging for low-severity conflicts
- [ ] **Conflict Detection**: Automatic identification of disagreement levels
- [ ] **Resolution Logging**: Track all consensus decisions for analysis

### Phase 4 Integration (Week 4)
- [ ] **UI Indicators**: Show consensus confidence in results dashboard
- [ ] **Manual Override**: Allow manual review of consensus decisions
- [ ] **Escalation Interface**: UI for handling escalated conflicts

### Phase 5 Enhancement (Week 5)
- [ ] **Advanced Algorithms**: Full evidence-based and expert mediation systems
- [ ] **Third Judge Option**: Optional Claude-3 integration for tie-breaking
- [ ] **Quality Monitoring**: Comprehensive consensus quality assurance
- [ ] **Expert Escalation**: Human expert review system for critical conflicts

## Consensus Decision Transparency

### Decision Audit Trail
Every consensus decision includes:
- **Input Data**: Original judge scores and rationales
- **Resolution Method**: Which algorithm was used and why
- **Confidence Level**: How confident the system is in the resolution
- **Alternative Scenarios**: What other resolutions were considered
- **Quality Metrics**: Validation scores and quality assessments

### User Communication
Clear communication to users about consensus decisions:
- **Agreement Level**: Visual indicators of judge agreement
- **Resolution Explanation**: Plain-language explanation of how conflicts were resolved
- **Confidence Display**: Clear indication of system confidence in final scores
- **Review Options**: Ability to request human review for important decisions

This comprehensive consensus strategy ensures robust handling of judge disagreements while maintaining transparency and quality assurance.
