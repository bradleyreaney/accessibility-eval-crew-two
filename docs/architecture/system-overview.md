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

## Current Architecture Status (Phase 3 Complete)

### Complete Data Flow

1. **Input Processing**
   ```
   PDF Files → PDF Parser → DocumentContent Objects
   Eval Prompt → Prompt Manager → Structured Criteria
   ```

2. **Workflow Orchestration (NEW)**
   ```
   DocumentContent → Task Manager → Coordinated Agent Execution
   Agent Tasks → CrewAI → Multi-Agent Workflow Execution
   Task Results → Synthesis → Unified Evaluation Output
   ```

3. **Agent Processing**
   ```
   DocumentContent + Criteria → Agent Tools → Formatted Evaluations
   Evaluation Prompts → Judge Agents → Structured Assessments
   Raw Scores → Scoring Agent → Weighted Rankings
   ```

4. **LLM Integration**
   ```
   Agent Prompts → LLM Manager → Multi-LLM Responses
   Gemini Pro (Primary + Scoring) + GPT-4 (Secondary + Analysis)
   ```

5. **Output Generation**
   ```
   Workflow Results → Report Generator → Structured Reports
   Evaluation Data → Export Layer → PDF Reports (Phase 4)
   ```

### Configuration Management

- **Environment Variables**: API keys and local settings
- **LLM Configuration**: Model settings and retry logic  
- **Agent Configuration**: Role definitions and tool assignments
- **Workflow Configuration**: Task definitions and execution order
- **Local Storage**: File-based data persistence

### Testing Architecture (Complete)

- **Unit Tests**: Individual component testing with comprehensive mocks
- **Agent Tests**: Specialized agent and tool validation
- **Workflow Tests**: CrewAI task and crew integration testing
- **Integration Tests**: End-to-end testing with real APIs/files
- **Demo Scripts**: Complete workflow demonstrations
- **TDD Approach**: Test-driven development maintaining 90%+ coverage

## Next Phase Architecture

### Phase 4: User Interface (In Progress)
- **Streamlit Interface**: Local web UI for evaluation management
- **File Upload**: PDF document upload and processing
- **Progress Tracking**: Real-time workflow execution monitoring
- **Report Viewing**: Interactive report display and export

## Local Application Focus

### Security Considerations

- **API Key Management**: Secure local environment variable storage
- **Input Validation**: PDF security scanning and content validation
- **Data Privacy**: All processing done locally, no external data transmission

### Performance Considerations

- **Local Processing**: All evaluation done on local machine
- **Efficient Workflows**: Optimized CrewAI task execution
- **Memory Management**: Careful handling of large PDF documents
- **Caching**: Local result caching for repeated evaluations

### Local Execution Benefits

- **Data Privacy**: All sensitive documents processed locally
- **Network Independence**: No external dependencies after API key setup
- **Customization**: Easy modification of evaluation criteria and workflows
- **Control**: Complete control over evaluation process and data handling
