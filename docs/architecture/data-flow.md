# Data Flow Documentation

Complete data flow architecture for the accessibility evaluation system.

## 🔄 End-to-End Data Flow

### Overview
```
[PDF Input] → [Parsing] → [Agent Processing] → [Consensus] → [Report Generation] → [Output]
```

## 📊 Detailed Data Flow Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Files     │    │   PDF Parser     │    │ Document Models │
│                 │────│                  │────│                 │
│ • Audit Report  │    │ • pdfplumber     │    │ • DocumentContent│
│ • Plan A-G      │    │ • Text extraction│    │ • Metadata      │
└─────────────────┘    │ • Metadata       │    │ • Validation    │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Processing Layer                       │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│ Primary Judge   │ Secondary Judge │ Scoring Agent   │ Analysis  │
│ (Gemini Pro)    │ (GPT-4)        │ (Gemini Pro)    │ Agent     │
│                 │                 │                 │ (GPT-4)   │
│ • Evaluation    │ • Independent   │ • Score Calc    │ • Strategic│
│ • Weighted      │   Assessment    │ • Ranking       │   Insights │
│   Scoring       │ • Cross-check   │ • Comparison    │ • Recommendations│
└─────────────────┴─────────────────┴─────────────────┴───────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Consensus Engine                             │
│                                                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│ │Minor Conflict│  │Moderate     │  │Major        │               │
│ │(<2 points)  │  │Conflict     │  │Conflict     │               │
│ │             │  │(2-3 points) │  │(>3 points)  │               │
│ │Auto Average │  │Evidence     │  │Human        │               │
│ │             │  │Assessment   │  │Escalation   │               │
│ └─────────────┘  └─────────────┘  └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Report Generation                            │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│ PDF Reports     │ CSV Export      │ JSON Export     │ Dashboard │
│ • Executive     │ • Score Matrix  │ • Full Results  │ • Plotly  │
│ • Detailed      │ • Rankings      │ • Metadata      │   Charts  │
│ • Comparative   │ • Raw Scores    │ • Timestamps    │ • Interactive│
│ • Summary       │                 │                 │   Viz     │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
```

## 🔄 Processing Stages

### Stage 1: Document Input & Parsing

#### Input Sources
```python
# Supported input formats
input_sources = {
    "audit_report": {
        "format": "PDF",
        "max_size": "50MB",
        "required": True,
        "validation": ["accessibility_audit", "findings_present"]
    },
    "remediation_plans": {
        "format": "PDF",
        "max_count": 10,
        "required": True,
        "validation": ["plan_structure", "implementation_details"]
    }
}
```

#### Parsing Process
```python
# PDF processing pipeline
def process_documents(audit_pdf, plan_pdfs):
    # 1. Document validation
    validate_pdf_format(audit_pdf)
    
    # 2. Text extraction
    audit_content = extract_text_content(audit_pdf)
    plan_contents = [extract_text_content(pdf) for pdf in plan_pdfs]
    
    # 3. Metadata extraction
    audit_metadata = extract_metadata(audit_pdf)
    
    # 4. Content validation
    validate_content_quality(audit_content)
    
    # 5. Data model creation
    return DocumentContent(
        title=audit_metadata.title,
        content=audit_content,
        metadata=audit_metadata
    )
```

### Stage 2: Agent Orchestration

#### Parallel Processing Flow
```python
async def agent_processing_flow(audit_content, plans):
    # Parallel agent initialization
    agents = await initialize_agents_parallel()
    
    # Primary evaluation (Gemini Pro)
    primary_tasks = [
        agents.primary_judge.evaluate_plan(plan.id, plan.content, audit_content)
        for plan in plans
    ]
    primary_results = await asyncio.gather(*primary_tasks)
    
    # Secondary evaluation (GPT-4) 
    secondary_tasks = [
        agents.secondary_judge.evaluate_plan(plan.id, plan.content, audit_content)
        for plan in plans
    ]
    secondary_results = await asyncio.gather(*secondary_tasks)
    
    # Scoring and analysis
    scoring_result = await agents.scoring_agent.process_evaluations(
        primary_results + secondary_results
    )
    
    analysis_result = await agents.analysis_agent.generate_insights(
        scoring_result
    )
    
    return {
        "primary": primary_results,
        "secondary": secondary_results,
        "scoring": scoring_result,
        "analysis": analysis_result
    }
```

#### Agent Communication Pattern
```
Primary Judge ────┐
                  ├─→ Consensus Engine ─→ Final Scores
Secondary Judge ──┘
                  ↓
Scoring Agent ────┤
                  ├─→ Strategic Analysis ─→ Recommendations
Analysis Agent ───┘
```

### Stage 3: Consensus Resolution

#### Conflict Detection Logic
```python
def detect_conflicts(primary_scores, secondary_scores):
    conflicts = []
    
    for i, (p_score, s_score) in enumerate(zip(primary_scores, secondary_scores)):
        difference = abs(p_score - s_score)
        
        if difference < 2.0:
            conflicts.append({
                "type": "minor",
                "difference": difference,
                "resolution": "auto_average"
            })
        elif difference < 3.0:
            conflicts.append({
                "type": "moderate", 
                "difference": difference,
                "resolution": "evidence_assessment"
            })
        else:
            conflicts.append({
                "type": "major",
                "difference": difference,
                "resolution": "human_escalation"
            })
    
    return conflicts
```

#### Resolution Strategies
```python
class ConflictResolution:
    def resolve_minor_conflict(self, scores):
        """Simple averaging for <2 point differences"""
        return sum(scores) / len(scores)
    
    def resolve_moderate_conflict(self, evaluations):
        """Evidence quality assessment for 2-3 point differences"""
        evidence_scores = [
            self.assess_evidence_quality(eval.reasoning)
            for eval in evaluations
        ]
        
        # Weight by evidence quality
        weighted_sum = sum(score * weight for score, weight in 
                          zip([e.score for e in evaluations], evidence_scores))
        total_weight = sum(evidence_scores)
        
        return weighted_sum / total_weight
    
    def resolve_major_conflict(self, evaluations):
        """Human escalation for >3 point differences"""
        return {
            "status": "escalated",
            "evaluations": evaluations,
            "required_action": "human_review",
            "escalation_timestamp": datetime.now()
        }
```

### Stage 4: Report Generation Pipeline

#### Multi-Format Output Flow
```python
def generate_outputs(evaluation_results):
    outputs = {}
    
    # PDF Reports (4 types)
    outputs["pdf"] = {
        "executive": generate_executive_summary(evaluation_results),
        "detailed": generate_detailed_report(evaluation_results),
        "comparative": generate_comparative_analysis(evaluation_results),
        "summary": generate_summary_report(evaluation_results)
    }
    
    # Data Exports
    outputs["csv"] = export_to_csv(evaluation_results)
    outputs["json"] = export_to_json(evaluation_results)
    
    # Interactive Visualizations
    outputs["dashboard"] = {
        "radar_charts": create_radar_charts(evaluation_results),
        "scatter_plots": create_scatter_plots(evaluation_results),
        "bar_charts": create_ranking_charts(evaluation_results)
    }
    
    return outputs
```

## 📊 Data Models & Structures

### Core Data Models
```python
# Input Models
class DocumentContent(BaseModel):
    title: str
    content: str
    page_count: int
    metadata: Dict[str, Any]
    
class AuditReport(DocumentContent):
    findings: List[AccessibilityIssue]
    severity_breakdown: Dict[str, int]

# Processing Models
class EvaluationResult(BaseModel):
    plan_id: str
    scores: EvaluationScores
    weighted_score: float
    reasoning: str
    timestamp: datetime
    agent_id: str

class EvaluationScores(BaseModel):
    strategic_prioritization: float
    technical_specificity: float  
    comprehensiveness: float
    long_term_vision: float

# Output Models
class FinalResults(BaseModel):
    ranked_plans: List[RankedPlan]
    consensus_summary: ConsensusSummary
    analysis: StrategicAnalysis
    metadata: ProcessingMetadata
```

### Data Validation Pipeline
```python
def validate_data_flow():
    """End-to-end data validation"""
    
    # Input validation
    validate_pdf_inputs()
    validate_content_extraction()
    
    # Processing validation
    validate_agent_responses()
    validate_scoring_calculations()
    validate_consensus_logic()
    
    # Output validation
    validate_report_generation()
    validate_export_formats()
    
    return ValidationReport(status="passed", details=validation_details)
```

## ⚡ Performance Optimization

### Caching Strategy
```python
# Multi-level caching
cache_strategy = {
    "pdf_parsing": "file_hash_based",    # Cache parsed content
    "llm_responses": "content_hash_based", # Cache LLM evaluations
    "report_generation": "result_based",   # Cache generated reports
    "consensus_decisions": "permanent"     # Cache consensus outcomes
}
```

### Parallel Processing
```python
# Concurrent execution patterns
async def optimized_processing():
    # Parallel document parsing
    parse_tasks = [parse_pdf(pdf) for pdf in input_pdfs]
    parsed_docs = await asyncio.gather(*parse_tasks)
    
    # Parallel agent evaluation
    eval_tasks = [
        agent.evaluate(plan, audit) 
        for agent in agents 
        for plan in plans
    ]
    evaluations = await asyncio.gather(*eval_tasks)
    
    # Parallel report generation
    report_tasks = [
        generate_pdf_report(results),
        generate_csv_export(results),
        generate_json_export(results)
    ]
    reports = await asyncio.gather(*report_tasks)
```

## 🔍 Error Handling & Recovery

### Error Propagation
```python
# Error handling at each stage
try:
    # PDF parsing errors
    documents = parse_documents(input_files)
except PDFParsingError as e:
    return handle_parsing_error(e)

try:
    # Agent processing errors
    evaluations = await process_with_agents(documents)
except LLMConnectionError as e:
    return handle_llm_error(e)

try:
    # Consensus resolution errors
    final_results = resolve_consensus(evaluations)
except ConflictResolutionError as e:
    return handle_consensus_error(e)
```

### Recovery Strategies
- **PDF Errors**: Retry with different parsing libraries
- **LLM Errors**: Fallback to alternative model or cached results
- **Consensus Errors**: Human escalation with detailed context
- **Report Errors**: Generate partial reports with error notifications

## 🔗 Integration Points

### External Systems
- **LLM APIs**: Gemini Pro, GPT-4 integration
- **PDF Libraries**: pdfplumber, PyPDF2 for parsing
- **Report Generation**: ReportLab for PDF creation
- **Web Interface**: Streamlit for user interaction

### Internal Modules
- **Configuration**: Centralized LLM and system settings
- **Monitoring**: Performance tracking and optimization
- **Logging**: Comprehensive audit trail and debugging
- **Testing**: End-to-end validation and quality assurance

## 🔗 Related Documentation

- **[System Overview](./system-overview.md)** - High-level architecture
- **[API Reference](../api-reference/)** - Detailed API documentation  
- **[Examples](../examples/)** - Implementation examples
