# Test-Driven Development Strategy
*LLM as a Judge - Accessibility Remediation Plan Evaluator*

**← [Master Plan](./master-plan.md)** | **Referenced in all phases**

## Overview

This document outlines the comprehensive Test-Driven Development (TDD) strategy for the LLM as a Judge system. TDD will be implemented throughout all phases to ensure robust, reliable, and maintainable code while catching issues early in the development cycle.

## TDD Philosophy & Approach

### Core TDD Principles
1. **Red-Green-Refactor Cycle**: Write failing tests first, implement minimal code to pass, then refactor
2. **Test First**: No production code without a failing test
3. **Incremental Development**: Small, focused tests that drive design decisions
4. **Living Documentation**: Tests serve as executable specifications

### Project-Specific TDD Benefits
- **LLM Reliability**: Validate AI agent outputs with deterministic tests
- **Complex Workflows**: Break down multi-agent orchestration into testable units
- **Data Processing**: Ensure PDF parsing and content extraction accuracy
- **Integration Confidence**: Validate API connections and external dependencies
- **Regression Prevention**: Catch issues when modifying agent prompts or logic

## Testing Architecture

### Test Pyramid Structure
```
                    ┌─────────────────┐
                    │   E2E Tests     │ 10%
                    │  (Streamlit UI) │
                    └─────────────────┘
                   ┌─────────────────────┐
                   │  Integration Tests  │ 20%
                   │ (Agents + Workflow) │
                   └─────────────────────┘
                  ┌─────────────────────────┐
                  │     Unit Tests          │ 70%
                  │ (Models, Tools, Utils)  │
                  └─────────────────────────┘
```

### Test Categories

#### 1. Unit Tests (70% of tests)
- **Models**: Pydantic validation, data structures
- **Tools**: PDF parsing, prompt management, scoring
- **Utils**: Helper functions, configuration management
- **Components**: Individual functions and classes

#### 2. Integration Tests (20% of tests)
- **Agent Interactions**: Multi-agent workflows
- **LLM Connections**: API integrations with mocks and real calls
- **Workflow Orchestration**: CrewAI task execution
- **Data Pipeline**: End-to-end data processing

#### 3. End-to-End Tests (10% of tests)
- **Complete Workflows**: Full evaluation pipeline
- **UI Interactions**: Streamlit interface functionality
- **Performance**: Response times and resource usage
- **User Scenarios**: Real-world usage patterns

## Phase-by-Phase TDD Implementation

### Phase 1: Foundation & Setup - TDD Strategy

#### 1.1 Environment Setup - Test Configuration

**Test Setup (`tests/conftest.py`)**
```python
"""
PyTest configuration and fixtures for TDD implementation
"""
import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch
from src.models.evaluation_models import DocumentContent, EvaluationInput
from src.config.llm_config import LLMConfig

@pytest.fixture
def project_root():
    """Project root directory fixture"""
    return Path(__file__).parent.parent

@pytest.fixture
def sample_audit_content():
    """Sample audit report content for testing"""
    return DocumentContent(
        title="Test Accessibility Audit",
        content="Sample audit content for testing...",
        page_count=5,
        metadata={"author": "Test Author", "date": "2025-01-01"}
    )

@pytest.fixture
def sample_remediation_plans():
    """Sample remediation plans for testing"""
    plans = {}
    for plan in ['PlanA', 'PlanB', 'PlanC']:
        plans[plan] = DocumentContent(
            title=f"Test {plan}",
            content=f"Sample content for {plan}...",
            page_count=3,
            metadata={"plan_type": plan}
        )
    return plans

@pytest.fixture
def mock_llm_config():
    """Mock LLM configuration for testing"""
    return LLMConfig(
        gemini_api_key="test_gemini_key",
        openai_api_key="test_openai_key"
    )

@pytest.fixture
def mock_pdf_files(tmp_path):
    """Create mock PDF files for testing"""
    audit_pdf = tmp_path / "test_audit.pdf"
    audit_pdf.write_text("Mock PDF content")
    
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir()
    
    for plan in ['PlanA', 'PlanB', 'PlanC']:
        plan_pdf = plans_dir / f"{plan}.pdf"
        plan_pdf.write_text(f"Mock {plan} content")
    
    return {
        'audit': audit_pdf,
        'plans_dir': plans_dir
    }
```

#### 1.2 PDF Parser - TDD Implementation

**Test File (`tests/unit/test_pdf_parser.py`)**
```python
"""
TDD implementation for PDF parsing functionality
Red-Green-Refactor cycle for each feature
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.tools.pdf_parser import PDFParser, DocumentContent

class TestPDFParserTDD:
    """Test-driven development for PDF parser"""
    
    def test_parser_initialization_creates_supported_formats(self):
        """RED: Test parser initializes with supported formats"""
        # This test will fail initially - write it first
        parser = PDFParser()
        assert hasattr(parser, 'supported_formats')
        assert '.pdf' in parser.supported_formats
    
    def test_parse_audit_report_returns_document_content(self, tmp_path):
        """RED: Test audit report parsing returns DocumentContent"""
        parser = PDFParser()
        mock_pdf = tmp_path / "test_audit.pdf"
        mock_pdf.write_text("Mock content")
        
        # This will fail initially - drives implementation
        result = parser.parse_audit_report(mock_pdf)
        assert isinstance(result, DocumentContent)
        assert result.title is not None
        assert result.content is not None
        assert result.page_count > 0
    
    @patch('src.tools.pdf_parser.pdfplumber.open')
    def test_parse_audit_report_extracts_text_content(self, mock_pdf_open):
        """RED: Test text extraction from PDF"""
        # Setup mock
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample audit text"
        mock_pdf.__enter__.return_value.pages = [mock_page, mock_page]
        mock_pdf_open.return_value = mock_pdf
        
        parser = PDFParser()
        result = parser.parse_audit_report(Path("test.pdf"))
        
        assert "Sample audit text" in result.content
        assert result.page_count == 2
    
    def test_parse_audit_report_handles_corrupted_pdf(self, tmp_path):
        """RED: Test error handling for corrupted PDFs"""
        parser = PDFParser()
        corrupted_pdf = tmp_path / "corrupted.pdf"
        corrupted_pdf.write_bytes(b"corrupted content")
        
        with pytest.raises(ValueError, match="Unable to parse PDF"):
            parser.parse_audit_report(corrupted_pdf)
    
    def test_batch_parse_plans_processes_multiple_files(self, mock_pdf_files):
        """RED: Test batch processing of remediation plans"""
        parser = PDFParser()
        
        with patch.object(parser, 'parse_remediation_plan') as mock_parse:
            mock_parse.return_value = DocumentContent(
                title="Test Plan", content="Test", page_count=1, metadata={}
            )
            
            results = parser.batch_parse_plans(mock_pdf_files['plans_dir'])
            
            assert len(results) == 3
            assert 'PlanA' in results
            assert mock_parse.call_count == 3
    
    def test_extract_title_from_content_finds_document_title(self):
        """RED: Test title extraction logic"""
        parser = PDFParser()
        
        content_with_title = """
        ACCESSIBILITY AUDIT REPORT
        Company XYZ Website Evaluation
        
        This document contains...
        """
        
        title = parser._extract_title(content_with_title)
        assert "ACCESSIBILITY AUDIT REPORT" in title
    
    def test_extract_metadata_returns_pdf_info(self):
        """RED: Test metadata extraction"""
        parser = PDFParser()
        
        mock_pdf_info = {
            '/Title': 'Test Document',
            '/Author': 'Test Author',
            '/CreationDate': '2025-01-01'
        }
        
        metadata = parser._extract_metadata(mock_pdf_info)
        assert metadata['title'] == 'Test Document'
        assert metadata['author'] == 'Test Author'
```

**Implementation (`src/tools/pdf_parser.py`)**
```python
"""
GREEN: Minimal implementation to make tests pass
"""
import pdfplumber
import PyPDF2
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel
import re

class DocumentContent(BaseModel):
    """Structured representation of parsed document content"""
    title: str
    content: str
    page_count: int
    metadata: Dict[str, str]

class PDFParser:
    """
    Handles extraction of text content from PDF files
    Test-driven implementation following TDD principles
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def parse_audit_report(self, file_path: Path) -> DocumentContent:
        """Parse accessibility audit report"""
        try:
            with pdfplumber.open(file_path) as pdf:
                content = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
                
                title = self._extract_title(content)
                metadata = self._extract_metadata(pdf.metadata)
                
                return DocumentContent(
                    title=title,
                    content=content.strip(),
                    page_count=len(pdf.pages),
                    metadata=metadata
                )
        except Exception as e:
            raise ValueError(f"Unable to parse PDF: {str(e)}")
    
    def parse_remediation_plan(self, file_path: Path) -> DocumentContent:
        """Parse remediation plan document"""
        # Similar implementation to audit report
        return self.parse_audit_report(file_path)
    
    def batch_parse_plans(self, plans_directory: Path) -> Dict[str, DocumentContent]:
        """Parse all remediation plans in directory"""
        plans = {}
        for pdf_file in plans_directory.glob("*.pdf"):
            plan_name = pdf_file.stem
            plans[plan_name] = self.parse_remediation_plan(pdf_file)
        return plans
    
    def _extract_title(self, content: str) -> str:
        """Extract document title from content"""
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 10 and line.isupper():
                return line
        return "Untitled Document"
    
    def _extract_metadata(self, pdf_metadata) -> Dict[str, str]:
        """Extract PDF metadata"""
        metadata = {}
        if pdf_metadata:
            for key, value in pdf_metadata.items():
                clean_key = key.lstrip('/')
                metadata[clean_key.lower()] = str(value) if value else ""
        return metadata
```

#### 1.3 LLM Integration - TDD Implementation

**Test File (`tests/unit/test_llm_config.py`)**
```python
"""
TDD for LLM configuration and connection management
"""
import pytest
from unittest.mock import Mock, patch
from src.config.llm_config import LLMManager, LLMConfig

class TestLLMConfigTDD:
    """Test-driven development for LLM configuration"""
    
    def test_llm_config_validation_requires_api_keys(self):
        """RED: Test configuration validation"""
        with pytest.raises(ValueError):
            LLMConfig(gemini_api_key="", openai_api_key="")
    
    def test_llm_config_accepts_valid_keys(self):
        """RED: Test valid configuration creation"""
        config = LLMConfig(
            gemini_api_key="test_gemini_key",
            openai_api_key="test_openai_key"
        )
        assert config.gemini_api_key == "test_gemini_key"
        assert config.openai_api_key == "test_openai_key"
    
    @patch('src.config.llm_config.ChatGoogleGenerativeAI')
    @patch('src.config.llm_config.ChatOpenAI')
    def test_llm_manager_initializes_both_llms(self, mock_openai, mock_gemini):
        """RED: Test LLM manager initialization"""
        config = LLMConfig(
            gemini_api_key="test_gemini",
            openai_api_key="test_openai"
        )
        
        manager = LLMManager(config)
        
        mock_gemini.assert_called_once()
        mock_openai.assert_called_once()
        assert hasattr(manager, 'gemini')
        assert hasattr(manager, 'openai')
    
    @patch('src.config.llm_config.ChatGoogleGenerativeAI')
    @patch('src.config.llm_config.ChatOpenAI')
    def test_llm_manager_test_connections_success(self, mock_openai, mock_gemini):
        """RED: Test successful connection testing"""
        # Setup mocks
        mock_gemini_instance = Mock()
        mock_gemini_instance.invoke.return_value = "Gemini response"
        mock_gemini.return_value = mock_gemini_instance
        
        mock_openai_instance = Mock()
        mock_openai_instance.invoke.return_value = "OpenAI response"
        mock_openai.return_value = mock_openai_instance
        
        config = LLMConfig(gemini_api_key="test", openai_api_key="test")
        manager = LLMManager(config)
        
        results = manager.test_connections()
        
        assert results['gemini'] is True
        assert results['openai'] is True
    
    @patch('src.config.llm_config.ChatGoogleGenerativeAI')
    def test_llm_manager_handles_connection_failures(self, mock_gemini):
        """RED: Test connection failure handling"""
        mock_gemini_instance = Mock()
        mock_gemini_instance.invoke.side_effect = Exception("API Error")
        mock_gemini.return_value = mock_gemini_instance
        
        config = LLMConfig(gemini_api_key="invalid", openai_api_key="test")
        manager = LLMManager(config)
        
        results = manager.test_connections()
        assert results['gemini'] is False
```

### Phase 2: Core Agent Development - TDD Strategy

#### 2.1 Judge Agent - TDD Implementation

**Test File (`tests/unit/test_judge_agent.py`)**
```python
"""
TDD for CrewAI judge agents
"""
import pytest
from unittest.mock import Mock, patch
from src.agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from src.models.evaluation_models import PlanEvaluation, JudgmentScore

class TestJudgeAgentTDD:
    """Test-driven development for judge agents"""
    
    def test_primary_judge_agent_initialization(self):
        """RED: Test agent creation with proper configuration"""
        mock_llm = Mock()
        agent = PrimaryJudgeAgent(mock_llm)
        
        assert agent.llm == mock_llm
        assert hasattr(agent, 'agent')
        assert agent.agent.role == "Senior Accessibility Consultant"
    
    def test_primary_judge_evaluate_plan_returns_structured_output(self):
        """RED: Test plan evaluation returns proper structure"""
        mock_llm = Mock()
        agent = PrimaryJudgeAgent(mock_llm)
        
        # Mock agent response
        mock_response = """
        Strategic Prioritization: 8.5/10 - Well prioritized approach
        Technical Specificity: 7.0/10 - Good technical details
        Overall Score: 7.8/10
        Pros: Clear roadmap, good prioritization
        Cons: Lacks some technical depth
        """
        
        with patch.object(agent.agent, 'execute', return_value=mock_response):
            result = agent.evaluate_plan("PlanA", "Plan content", "Audit context")
        
        assert isinstance(result, dict)
        assert 'scores' in result
        assert 'overall_score' in result
        assert 'pros' in result
        assert 'cons' in result
    
    def test_judge_scores_validation_within_range(self):
        """RED: Test score validation logic"""
        mock_llm = Mock()
        agent = PrimaryJudgeAgent(mock_llm)
        
        # Test valid score parsing
        raw_result = "Strategic Prioritization: 8.5/10"
        score = agent._parse_score_line(raw_result)
        
        assert 0.0 <= score <= 10.0
        assert score == 8.5
    
    def test_judge_handles_invalid_llm_response(self):
        """RED: Test error handling for malformed responses"""
        mock_llm = Mock()
        agent = PrimaryJudgeAgent(mock_llm)
        
        with patch.object(agent.agent, 'execute', return_value="Invalid response"):
            with pytest.raises(ValueError, match="Unable to parse evaluation"):
                agent.evaluate_plan("PlanA", "content", "context")
    
    def test_secondary_judge_independent_evaluation(self):
        """RED: Test secondary judge independence"""
        mock_llm = Mock()
        secondary_agent = SecondaryJudgeAgent(mock_llm)
        
        # Ensure secondary judge doesn't see primary results
        with patch.object(secondary_agent.agent, 'execute') as mock_execute:
            secondary_agent.evaluate_plan("PlanA", "content", "context")
            
            # Verify primary results not in prompt
            call_args = mock_execute.call_args[0][0]
            assert "primary judge" not in call_args.lower()
            assert "gemini" not in call_args.lower()
```

#### 2.2 Custom Tools - TDD Implementation

**Test File (`tests/unit/test_evaluation_tools.py`)**
```python
"""
TDD for custom CrewAI tools
"""
import pytest
from unittest.mock import Mock
from src.tools.evaluation_framework import EvaluationFrameworkTool
from src.tools.scoring_calculator import ScoringCalculatorTool

class TestEvaluationToolsTDD:
    """Test-driven development for evaluation tools"""
    
    def test_evaluation_framework_tool_initialization(self):
        """RED: Test tool initialization"""
        tool = EvaluationFrameworkTool()
        
        assert tool.name == "evaluation_framework"
        assert hasattr(tool, 'description')
        assert callable(tool._run)
    
    def test_scoring_calculator_weighted_average(self):
        """RED: Test weighted scoring calculation"""
        tool = ScoringCalculatorTool()
        
        scores = {
            'strategic_prioritization': 8.0,
            'technical_specificity': 7.5,
            'comprehensiveness': 6.0,
            'long_term_vision': 9.0
        }
        
        weights = {
            'strategic_prioritization': 0.40,
            'technical_specificity': 0.30,
            'comprehensiveness': 0.20,
            'long_term_vision': 0.10
        }
        
        result = tool.calculate_weighted_score(scores, weights)
        expected = (8.0*0.40 + 7.5*0.30 + 6.0*0.20 + 9.0*0.10)
        
        assert abs(result - expected) < 0.01
    
    def test_scoring_calculator_validates_weights_sum_to_one(self):
        """RED: Test weight validation"""
        tool = ScoringCalculatorTool()
        
        invalid_weights = {
            'strategic_prioritization': 0.50,
            'technical_specificity': 0.30,
            'comprehensiveness': 0.30,  # Total = 1.10
            'long_term_vision': 0.10
        }
        
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            tool.validate_weights(invalid_weights)
```

### Phase 3: Workflow Integration - TDD Strategy

#### 3.1 Task Management - TDD Implementation

**Test File (`tests/integration/test_workflow.py`)**
```python
"""
TDD for CrewAI workflow integration
"""
import pytest
from unittest.mock import Mock, AsyncMock
from src.tasks.evaluation_tasks import EvaluationTaskManager
from src.config.crew_config import AccessibilityEvaluationCrew

class TestWorkflowTDD:
    """Test-driven development for workflow orchestration"""
    
    def test_evaluation_task_manager_creates_primary_task(self):
        """RED: Test primary evaluation task creation"""
        primary_judge = Mock()
        secondary_judge = Mock()
        task_manager = EvaluationTaskManager(primary_judge, secondary_judge)
        
        task = task_manager.create_primary_evaluation_task(
            "PlanA", "Plan content", "Audit context"
        )
        
        assert task.description is not None
        assert "PlanA" in task.description
        assert task.agent == primary_judge.agent
    
    def test_crew_executes_complete_evaluation_workflow(self):
        """RED: Test end-to-end workflow execution"""
        mock_llm_manager = Mock()
        crew = AccessibilityEvaluationCrew(mock_llm_manager)
        
        mock_evaluation_input = Mock()
        mock_evaluation_input.remediation_plans = {
            'PlanA': Mock(), 'PlanB': Mock()
        }
        
        with patch.object(crew, '_execute_evaluation_tasks') as mock_execute:
            mock_execute.return_value = [Mock(), Mock()]  # Mock results
            
            result = crew.execute_complete_evaluation(mock_evaluation_input)
            
            assert result is not None
            mock_execute.assert_called_once()
    
    def test_parallel_evaluation_improves_performance(self):
        """RED: Test parallel execution optimization"""
        mock_llm_manager = Mock()
        crew = AccessibilityEvaluationCrew(mock_llm_manager)
        
        # Test that parallel execution is faster than sequential
        # This drives the implementation of parallel task execution
        start_time = time.time()
        
        with patch.object(crew, '_execute_parallel_tasks') as mock_parallel:
            mock_parallel.return_value = [Mock(), Mock()]
            
            crew.execute_parallel_evaluation(Mock())
            
        execution_time = time.time() - start_time
        
        # Verify parallel execution was called
        mock_parallel.assert_called_once()
        assert execution_time < 1.0  # Should be fast with mocks
    
    def test_conflict_detection_identifies_judge_disagreements(self):
        """RED: Test judge conflict detection"""
        crew = AccessibilityEvaluationCrew(Mock())
        
        evaluations = [
            Mock(judge_id="gemini", overall_score=8.0, plan_name="PlanA"),
            Mock(judge_id="gpt4", overall_score=6.0, plan_name="PlanA")  # 2.0 difference
        ]
        
        conflicts = crew._identify_judge_conflicts(evaluations)
        
        assert len(conflicts) > 0
        assert any(c.plan_name == "PlanA" for c in conflicts)
```

### Phase 4: User Interface - TDD Strategy

#### 4.1 Streamlit Components - TDD Implementation

**Test File (`tests/ui/test_streamlit_app.py`)**
```python
"""
TDD for Streamlit user interface
"""
import pytest
from unittest.mock import Mock, patch
import streamlit as st
from streamlit.testing.v1 import AppTest

class TestStreamlitAppTDD:
    """Test-driven development for Streamlit interface"""
    
    def test_app_initializes_with_correct_title(self):
        """RED: Test app initialization"""
        app_test = AppTest.from_file("app/main.py")
        app_test.run()
        
        assert app_test.title[0].value == "⚖️ LLM as a Judge - Accessibility Remediation Plan Evaluator"
    
    def test_configuration_page_validates_api_keys(self):
        """RED: Test API key validation"""
        app_test = AppTest.from_file("app/main.py")
        app_test.run()
        
        # Simulate empty API key input
        app_test.text_input[0].input("")  # Gemini key
        app_test.text_input[1].input("")  # OpenAI key
        app_test.button[0].click()        # Configure button
        
        assert app_test.error[0].value.startswith("Please enter valid API keys")
    
    def test_file_upload_accepts_pdf_files(self):
        """RED: Test PDF file upload validation"""
        app_test = AppTest.from_file("app/main.py")
        app_test.run()
        
        # Mock file upload
        with patch('streamlit.file_uploader') as mock_upload:
            mock_file = Mock()
            mock_file.name = "test.pdf"
            mock_file.type = "application/pdf"
            mock_upload.return_value = mock_file
            
            # Test upload handling
            assert mock_file.name.endswith('.pdf')
    
    def test_progress_monitoring_updates_in_realtime(self):
        """RED: Test real-time progress updates"""
        app_test = AppTest.from_file("app/main.py")
        app_test.run()
        
        # Test progress bar updates
        with patch('streamlit.progress') as mock_progress:
            # Simulate evaluation progress
            for i in range(0, 101, 20):
                mock_progress(i)
            
            assert mock_progress.call_count == 6  # 0, 20, 40, 60, 80, 100
```

### Phase 5: Optimization - TDD Strategy

#### 5.1 Performance Testing

**Test File (`tests/performance/test_performance.py`)**
```python
"""
TDD for performance optimization
"""
import pytest
import time
from unittest.mock import Mock
from src.batch.batch_processor import BatchProcessor
from src.monitoring.performance_monitor import PerformanceMonitor

class TestPerformanceTDD:
    """Test-driven development for performance optimization"""
    
    def test_batch_processor_handles_multiple_audits(self):
        """RED: Test batch processing performance"""
        processor = BatchProcessor()
        
        # Create mock batch job
        mock_jobs = [Mock() for _ in range(5)]
        
        start_time = time.time()
        results = processor.process_batch(mock_jobs)
        execution_time = time.time() - start_time
        
        assert len(results) == 5
        assert execution_time < 10.0  # Should complete within 10 seconds
    
    def test_performance_monitor_tracks_metrics(self):
        """RED: Test performance monitoring"""
        monitor = PerformanceMonitor()
        
        with monitor.track_operation("test_operation"):
            time.sleep(0.1)  # Simulate work
        
        metrics = monitor.get_metrics()
        assert "test_operation" in metrics
        assert metrics["test_operation"]["duration"] >= 0.1
    
    def test_cache_improves_response_times(self):
        """RED: Test caching optimization"""
        from src.monitoring.performance_monitor import CacheManager
        
        cache = CacheManager()
        
        # First call - cache miss
        start_time = time.time()
        result1 = cache.get_or_compute("test_key", lambda: "expensive_operation")
        first_call_time = time.time() - start_time
        
        # Second call - cache hit
        start_time = time.time()
        result2 = cache.get_or_compute("test_key", lambda: "expensive_operation")
        second_call_time = time.time() - start_time
        
        assert result1 == result2
        assert second_call_time < first_call_time
        assert cache.get_hit_rate() > 0.0
```

## TDD Testing Matrix

### Test Coverage Requirements

| Component | Unit Tests | Integration Tests | E2E Tests | Coverage Target |
|-----------|------------|-------------------|-----------|-----------------|
| PDF Parser | ✅ Core logic | ✅ File handling | ❌ | 95% |
| LLM Config | ✅ Validation | ✅ API calls | ❌ | 90% |
| Judge Agents | ✅ Logic | ✅ Agent execution | ✅ Full workflow | 85% |
| Workflow | ✅ Task creation | ✅ Orchestration | ✅ Complete pipeline | 80% |
| UI Components | ✅ Logic | ✅ Streamlit widgets | ✅ User scenarios | 75% |
| Performance | ✅ Algorithms | ✅ Monitoring | ✅ Load testing | 70% |

### Test Automation Pipeline

```yaml
# .github/workflows/tdd-pipeline.yml
name: TDD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: pytest tests/integration/ -v
    
    - name: Run E2E tests
      run: pytest tests/e2e/ -v --slow
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## TDD Best Practices for This Project

### 1. Mock Strategy for LLM Calls
```python
# Always mock LLM API calls in unit tests
@patch('src.config.llm_config.ChatGoogleGenerativeAI')
def test_agent_behavior(mock_llm):
    mock_llm.return_value.invoke.return_value = "Expected response"
    # Test agent logic without API calls
```

### 2. Deterministic Testing for AI Components
```python
# Use fixed seeds and deterministic responses
def test_evaluation_consistency():
    """Ensure same input produces same output"""
    agent = PrimaryJudgeAgent(mock_llm)
    
    result1 = agent.evaluate_plan("PlanA", content, context)
    result2 = agent.evaluate_plan("PlanA", content, context)
    
    assert result1 == result2  # Deterministic output
```

### 3. Progressive Integration Testing
```python
# Start with simple integrations, build complexity
def test_single_agent_workflow():
    """Test one agent first"""
    
def test_two_agent_workflow():
    """Add second agent"""
    
def test_complete_workflow():
    """Full multi-agent orchestration"""
```

### 4. Performance Regression Prevention
```python
# Include performance assertions in tests
def test_evaluation_performance():
    start_time = time.time()
    run_evaluation()
    execution_time = time.time() - start_time
    
    assert execution_time < MAX_ACCEPTABLE_TIME
```

## Integration with Existing Plans

### Updated Requirements (`requirements-test.txt`)
```txt
# Testing Framework
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-xdist>=3.3.0  # Parallel test execution

# UI Testing
pytest-streamlit>=0.1.0
selenium>=4.15.0

# Performance Testing
pytest-benchmark>=4.0.0
locust>=2.17.0

# Code Quality
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.5.0

# Coverage and Reporting
coverage>=7.3.0
pytest-html>=3.2.0
```

This comprehensive TDD strategy ensures that every component of the LLM as a Judge system is thoroughly tested, reliable, and maintainable. The test-first approach will catch issues early and provide confidence for refactoring and optimization throughout development.

## Summary

The TDD strategy provides:
- **95%+ Code Coverage**: Comprehensive testing across all components
- **Early Issue Detection**: Catch problems before they become expensive
- **Design Guidance**: Tests drive better architecture decisions
- **Refactoring Confidence**: Safe to optimize and improve code
- **Documentation**: Tests serve as executable specifications
- **Quality Assurance**: Consistent, reliable system behavior

This approach is particularly valuable for an LLM-based system where deterministic testing of non-deterministic components requires careful strategy and robust mocking approaches.
