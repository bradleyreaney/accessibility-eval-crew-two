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

### Phase 1: Foundation Components

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

### Data Flow

1. **Input Processing**
   ```
   PDF Files → PDF Parser → DocumentContent Objects
   Eval Prompt → Prompt Manager → Structured Criteria
   ```

2. **LLM Integration**
   ```
   DocumentContent + Criteria → LLM Manager → Structured Evaluations
   ```

3. **Output Generation**
   ```
   Evaluations → Report Generator → PDF Reports
   ```

### Configuration Management

- **Environment Variables**: API keys, paths, and settings
- **LLM Configuration**: Model settings, timeouts, retry logic
- **Validation**: Input validation and error handling

### Testing Architecture

- **Unit Tests**: Individual component testing with mocks
- **Integration Tests**: End-to-end testing with real APIs/files
- **TDD Approach**: Test-driven development with Red-Green-Refactor

## Planned Architecture (Future Phases)

### Phase 2: Agent Layer
- **Primary Judge Agent**: Main evaluation agent using Gemini Pro
- **Secondary Judge Agent**: Validation agent using GPT-4
- **Comparison Agent**: Cross-plan analysis and ranking

### Phase 3: Workflow Orchestration
- **CrewAI Workflows**: Coordinated agent execution
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
