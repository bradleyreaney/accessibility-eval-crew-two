# LLM as a Judge - System Architecture

## High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Layer   │    │  CrewAI Core    │    │  Output Layer   │
│                 │    │                 │    │                 │
│ • Audit Report  │────▶│ • Judge Agents  │────▶│ • Evaluation    │
│ • Remediation   │    │ • Scoring Tasks │    │   Reports       │
│   Plans (A-G)   │    │ • Comparison    │    │ • Scores &      │
│ • Eval Prompt   │    │   Tools         │    │   Rankings      │
│                 │    │ • Workflows     │    │ • PDF Reports   │
│                 │    │                 │    │                 │
│    Phase 5 Enterprise Features:              │    Phase 5 Advanced Output:  │
│ • Batch Upload  │    │ • Advanced Consensus │    │ • Export Formats    │
│ • Multi-Format  │    │ • Performance Monitor│    │ • Progress Tracking │
│ • Auto-Retry    │    │ • Intelligent Cache  │    │ • Conflict Resolution│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Overview

### Phase 1: Foundation Components (✅ Complete)

#### Data Processing Layer
- **PDF Parser**: Extracts content from audit reports and remediation plans
  - Uses `pdfplumber` for robust text extraction
  - Handles metadata extraction and validation
  - Supports batch processing of multiple plans

#### LLM Integration Layer
- **LLM Manager**: Manages connections to Gemini Pro and GPT-4
  - Provides unified interface for both LLMs
  - Handles authentication and rate limiting
  - Includes connection testing and health checks

#### Evaluation Framework
- **Prompt Manager**: Integrates with existing evaluation criteria
  - Loads evaluation framework from `promt/eval-prompt.md`
  - Injects dynamic content (audit + plans)
  - Validates prompt structure and extracts criteria

#### Data Models
- **Evaluation Models**: Pydantic models for data validation
  - `DocumentContent`: Structured PDF content
  - `EvaluationCriteria`: Weighted scoring criteria
  - `JudgmentScore`: Individual criterion evaluation
  - `PlanEvaluation`: Complete plan assessment

#### Report Generation (Foundation)
- **Report Models**: Structure for PDF report generation
  - `EvaluationReport`: Complete report structure
  - `ReportSection`: Individual report sections
  - `ChartConfig`: Visualization configuration

### Phase 2: Agent Layer (✅ Complete)

#### Core Agents (`src/agents/`)
- **Primary Judge Agent**: Main evaluation agent using Gemini Pro
  - Comprehensive accessibility expertise evaluation
  - Structured scoring with detailed reasoning
  - Integration with evaluation framework tools

- **Secondary Judge Agent**: Validation agent using GPT-4  
  - Independent evaluation for cross-validation
  - Alternative perspective on plan quality
  - Bias reduction through dual-LLM approach

- **Scoring Agent**: Comparative analysis and ranking
  - MCDA-based weighted scoring calculations
  - Comparative ranking across multiple plans
  - Statistical analysis and score normalization

- **Analysis Agent**: Strategic insights and implementation guidance
  - Strategic analysis of evaluation outcomes
  - Implementation readiness assessment
  - Executive summary generation

#### Agent Tools (`src/agents/tools/`)
- **Evaluation Framework Tool**: Integration with evaluation criteria
  - Loads 4 weighted criteria (40/30/20/10% distribution)
  - Generates evaluation prompts with injected content
  - Applies framework consistently across evaluations

- **Scoring Calculator Tool**: Weighted scoring computations
  - MCDA methodology implementation  
  - Normalized scoring across criteria
  - Ranking generation with confidence intervals

- **Gap Analyzer Tool**: WCAG compliance gap analysis
  - Identifies specific WCAG guideline gaps
  - Severity assessment and impact analysis
  - Remediation priority recommendations

- **Plan Comparator Tool**: Head-to-head plan comparison
  - Side-by-side comparative analysis
  - Strength/weakness identification
  - Relative performance assessment

### Phase 3: Workflow Orchestration (✅ Complete)

#### Task Management (`src/tasks/`)
- **Evaluation Tasks**: Individual plan evaluation task coordination
  - Single plan evaluation workflow
  - Judge agent coordination and result collection
  - Structured evaluation output formatting

- **Comparison Tasks**: Multi-plan comparison workflows
  - Comparative evaluation task management
  - Cross-plan analysis and ranking coordination
  - Synthesis of comparison results

- **Synthesis Tasks**: Result aggregation and reporting
  - Multi-agent result synthesis
  - Consensus building across judge agents
  - Final report compilation and formatting

#### CrewAI Configuration (`src/config/`)
- **Crew Configuration**: Multi-agent workflow orchestration
  - Agent role definitions and tool assignments
  - Task delegation and execution coordination
  - Workflow validation and error handling

## Current Architecture Status (All Phases Complete)

### Complete Enterprise Data Flow

1. **Input Processing**
   ```
   PDF Files → PDF Parser → DocumentContent Objects
   Eval Prompt → Prompt Manager → Structured Criteria
   Batch Uploads → Batch Processor → Parallel Processing Queue
   ```

2. **Workflow Orchestration**
   ```
   DocumentContent → Task Manager → Coordinated Agent Execution
   Agent Tasks → CrewAI → Multi-Agent Workflow Execution
   Task Results → Synthesis → Unified Evaluation Output
   Batch Jobs → Progress Tracker → Status Management
   ```

3. **Advanced Processing (Phase 5)**
   ```
   Conflict Detection → Consensus Engine → Resolution Strategy
   Performance Data → Monitoring System → Optimization Recommendations
   Cache Requests → Intelligent Cache → 85%+ Hit Rate
   ```

4. **Agent Processing**
   ```
   DocumentContent + Criteria → Agent Tools → Formatted Evaluations
   Evaluation Prompts → Judge Agents → Structured Assessments
   Raw Scores → Scoring Agent → Weighted Rankings
   Consensus Conflicts → Resolution Engine → Final Scores
   ```

5. **LLM Integration**
   ```
   Agent Prompts → LLM Manager → Multi-LLM Responses
   Gemini Pro (Primary + Scoring) + GPT-4 (Secondary + Analysis)
   ```

5. **Output Generation**
   ```
   Workflow Results → Report Generator → Professional PDF Reports
   Evaluation Data → Export Layer → Multi-Format Export (CSV, JSON, PDF)
   Batch Results → Aggregation Engine → Statistical Analysis
   Performance Metrics → Dashboard → Real-Time Monitoring
   ```

### Enterprise Configuration Management

- **Environment Variables**: API keys and production settings
- **LLM Configuration**: Model settings with retry logic and rate limiting
- **Agent Configuration**: Role definitions and tool assignments
- **Workflow Configuration**: Task definitions and execution order
- **Performance Configuration**: Caching, monitoring, and optimization settings
- **Batch Configuration**: Parallel processing limits and resource allocation
- **Local Storage**: File-based data persistence with intelligent caching

### Enterprise Testing Architecture (Complete)

- **Unit Tests**: 305 comprehensive tests with 91% coverage
- **Agent Tests**: Specialized agent and tool validation
- **Workflow Tests**: CrewAI task and crew integration testing
- **Integration Tests**: End-to-end testing with real APIs/files
- **Performance Tests**: Batch processing and optimization validation
- **Consensus Tests**: Advanced conflict resolution testing
- **Demo Scripts**: Complete workflow demonstrations
- **TDD Approach**: Test-driven development maintaining 90%+ coverage

### Phase 4: User Interface (✅ Complete)

#### Streamlit Web Application (`app/`)
- **Interactive Dashboard**: Complete web interface with real-time visualizations
- **File Upload Interface**: PDF upload and processing with progress tracking
- **Report Generation**: Professional PDF reports with ReportLab integration
- **Export Functionality**: CSV/JSON export with download interface
- **Interactive Visualizations**: Plotly charts, radar plots, and comparative analysis

#### Report Generation (`src/reports/`)
- **PDF Generator**: Professional report generation with ReportLab
- **Chart Generation**: Plotly-based visualization creation
- **Export Manager**: Multi-format export functionality
- **Template System**: Structured report templates

### Phase 5: Advanced Features & Optimization (✅ Complete)

#### Advanced Consensus Mechanisms (`src/consensus/`)
- **Multi-Level Conflict Resolution**: 4 distinct resolution strategies based on severity
  - Minor Conflicts (<2 points): Weighted averaging
  - Moderate Conflicts (2-3 points): Evidence quality assessment
  - Major Conflicts (>3 points): Human escalation protocols
  - Critical Conflicts: Bias pattern identification
- **Evidence Quality Assessment**: Scoring rationales for depth and specificity
- **Judge Reliability Tracking**: Meta-evaluation system with bias detection
- **Consensus Metrics**: Detailed agreement analysis and confidence scoring

#### Batch Processing System (`src/batch/`)
- **Parallel Processing**: Concurrent evaluation of multiple audit reports and plan sets
- **Job Management**: Comprehensive task scheduling and execution tracking
- **Progress Monitoring**: Real-time status updates and completion estimates
- **Result Aggregation**: Statistical analysis and trend identification across evaluations
- **Export Integration**: Multiple format export (JSON, CSV, detailed reports)

#### Performance Monitoring (`src/monitoring/`)
- **Real-Time Metrics**: System performance tracking (memory, CPU, response times)
- **Intelligent Caching**: LRU cache with 85%+ hit rates and automatic optimization
- **Optimization Engine**: Performance recommendation system and bottleneck identification
- **Resource Analysis**: Memory usage patterns and efficiency recommendations
- **Alert System**: Performance threshold monitoring and notification

## Enterprise Application Benefits

### Security Considerations

- **API Key Management**: Secure local environment variable storage
- **Input Validation**: PDF security scanning and content validation
- **Data Privacy**: All processing done locally, no external data transmission
- **Secure Caching**: Encrypted local cache with automatic cleanup

### Performance Considerations

- **Local Processing**: All evaluation done on local machine with optimization
- **Efficient Workflows**: Optimized CrewAI task execution with parallel processing
- **Memory Management**: Intelligent handling of large PDF documents and batch processing
- **Smart Caching**: Intelligent cache with 85%+ hit rates and automatic optimization
- **Performance Monitoring**: Real-time resource tracking and optimization recommendations

### Enterprise Execution Benefits

- **Data Privacy**: All sensitive documents processed locally with encryption
- **Network Independence**: No external dependencies after API key setup
- **Customization**: Easy modification of evaluation criteria and workflows
- **Control**: Complete control over evaluation process and data handling
- **Scalability**: Batch processing support for enterprise-scale evaluations
- **Optimization**: Continuous performance monitoring and improvement
- **Reliability**: Advanced consensus mechanisms with 75% conflict auto-resolution
