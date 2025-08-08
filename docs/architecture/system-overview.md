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

## Current Architecture Status (Phase 2 Complete)

### Data Flow (Updated)

1. **Input Processing**
   ```
   PDF Files → PDF Parser → DocumentContent Objects
   Eval Prompt → Prompt Manager → Structured Criteria
   ```

2. **Agent Processing (NEW)**
   ```
   DocumentContent + Criteria → Agent Tools → Formatted Evaluations
   Evaluation Prompts → Judge Agents → Structured Assessments
   Raw Scores → Scoring Agent → Weighted Rankings
   ```

3. **LLM Integration**
   ```
   Agent Prompts → LLM Manager → Multi-LLM Responses
   Gemini Pro (Primary + Scoring) + GPT-4 (Secondary + Analysis)
   ```

4. **Output Generation**
   ```
   Agent Evaluations → Report Generator → PDF Reports (Ready for Phase 3)
   ```

### Configuration Management

- **Environment Variables**: API keys, paths, and settings
- **LLM Configuration**: Model settings, timeouts, retry logic  
- **Agent Configuration**: Role definitions, tool assignments
- **Validation**: Input validation and error handling

### Testing Architecture (Updated)

- **Unit Tests**: Individual component + agent testing with mocks
- **Agent Tests**: Specialized agent initialization and tool validation
- **Integration Tests**: End-to-end testing with real APIs/files
- **Demo Scripts**: Complete workflow demonstrations (`scripts/phase2_demo.py`)
- **TDD Approach**: Test-driven development with Red-Green-Refactor

## Next Phase Architecture

### Phase 3: Workflow Orchestration (Ready to Begin)
- **CrewAI Crews**: Coordinated multi-agent workflows
- **Task Orchestration**: Sequential and parallel agent execution
- **Consensus Mechanisms**: Multi-judge agreement protocols
- **Quality Assurance**: Evaluation validation and consistency

### Phase 4: Interface Layer
- **Streamlit Interface**: Web UI for evaluation management
- **FastAPI Backend**: REST API for programmatic access
- **Report Management**: Generated report storage and retrieval

## Security Considerations

- **API Key Management**: Secure storage and rotation
- **Input Validation**: PDF security scanning and content validation
- **Data Privacy**: Sensitive content handling and anonymization

## Performance Considerations

- **Async Processing**: Non-blocking LLM calls
- **Caching**: Response caching for repeated evaluations
- **Rate Limiting**: API quota management and backoff strategies

## Scalability

- **Horizontal Scaling**: Multiple agent instances
- **Load Balancing**: Request distribution across LLM providers
- **Queue Management**: Background task processing
