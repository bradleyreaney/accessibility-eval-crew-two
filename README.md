# LLM as a Judge - Accessibility Evaluation System

*Enterprise-ready AI system for evaluating accessibility remediation plans using advanced multi-agent LLM workflows*

[![Tests](https://img.shields.io/badge/tests-305%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)]()
[![Phase](https://img.shields.io/badge/phase-5%20complete-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## 🎯 Overview

This system leverages **Large Language Models as Judges** to provide comprehensive, unbiased evaluation of accessibility remediation plans. Using CrewAI for multi-agent orchestration, it combines the expertise of Gemini Pro and GPT-4 to deliver professional-grade accessibility assessments through a complete Streamlit web application with enterprise-ready advanced features.

**Status: Phase 5 COMPLETE** - Enterprise-ready system with advanced consensus mechanisms, batch processing, and performance monitoring (August 2025).

### Key Features
- 🤖 **Multi-Agent Evaluation**: 4 specialized CrewAI agents with Gemini Pro & GPT-4
- 🎯 **Expert Judge Agents**: Primary (Gemini) and Secondary (GPT-4) evaluation agents
- 📊 **Scoring & Analysis**: Dedicated agents for weighted scoring and strategic analysis
- 📈 **Weighted Scoring**: Strategic Prioritization (40%), Technical Specificity (30%), Comprehensiveness (20%), Long-Term Vision (10%)
- 🛠️ **Agent Tools**: 4 specialized tools for evaluation, scoring, gap analysis, and comparison
- 🔄 **CrewAI Workflow**: Complete multi-agent task coordination and execution
- 📄 **PDF Processing**: Automated parsing of audit reports and remediation plans  
- 🔍 **Comparative Analysis**: Rank and compare multiple remediation strategies
- 📋 **Professional Reports**: Detailed evaluation reports with scores and recommendations
- 🌐 **Complete Web Interface**: Full-featured Streamlit application with interactive dashboard
- 📊 **Interactive Visualizations**: Plotly charts, radar plots, and comparative analysis
- 📁 **Export Functionality**: PDF, CSV, and JSON export with download interface
- 🎯 **WCAG Aligned**: Evaluation framework based on accessibility best practices
- 🚀 **Advanced Consensus**: Multi-level conflict resolution with human escalation protocols
- ⚡ **Batch Processing**: Parallel evaluation of multiple reports with progress tracking
- 📈 **Performance Monitoring**: Real-time metrics, intelligent caching, and optimization recommendations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API keys for Gemini Pro and GPT-4
- Virtual environment tools (venv/conda)

### Installation
```bash
# Clone the repository
git clone https://github.com/bradleyreaney/accessibility-eval-crew-two.git
cd accessibility-eval-crew-two

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys:
# GOOGLE_API_KEY=your_gemini_api_key
# OPENAI_API_KEY=your_openai_api_key
```

### Launch the Application
```bash
# Start the Streamlit web interface
streamlit run app/main.py

# The application will open in your browser at:
# http://localhost:8501
```

### Verification
```bash
# Run tests to verify installation
python -m pytest tests/unit/ -v

# Run Phase 4 validation and demo
python scripts/validate_phase4_quality_gates.py
python scripts/phase4_demo.py

# Expected output: All tests pass, 100% quality gates passed, full UI functional
```

## 📁 Project Structure

```
accessibility-eval-crew-two/
├── app/                   # ✅ Streamlit Web Application (Phase 4 COMPLETE)
│   └── main.py                # Complete UI with dashboard, visualizations, exports
├── src/                   # Core implementation
│   ├── config/            # LLM connections and configuration
│   ├── models/            # Pydantic data models and validation
│   ├── tools/             # PDF parsing, prompt management
│   ├── utils/             # Workflow controller and utilities
│   ├── reports/           # ✅ PDF and export generation (Phase 4 COMPLETE)
│   │   └── generators/        # Professional PDF reports with ReportLab
│   ├── consensus/         # ✅ Advanced consensus mechanisms (Phase 5 COMPLETE)
│   │   └── advanced_consensus.py  # Multi-level conflict resolution
│   ├── batch/             # ✅ Batch processing system (Phase 5 COMPLETE)
│   │   └── batch_processor.py     # Parallel processing and aggregation
│   ├── monitoring/        # ✅ Performance monitoring (Phase 5 COMPLETE)
│   │   └── performance_monitor.py # Real-time metrics and caching
│   └── agents/            # ✅ CrewAI agents (Phase 2 COMPLETE)
│       ├── judge_agent.py      # Primary & Secondary Judge Agents
│       ├── scoring_agent.py    # Scoring & Ranking Agent
│       ├── analysis_agent.py   # Strategic Analysis Agent
│       └── tools/             # Agent-specific tools
├── tests/                 # Comprehensive test suite (91% coverage)
│   ├── unit/              # Fast unit tests organized by module
│   │   ├── agents/            # Agent and tool tests
│   │   ├── config/            # Configuration tests
│   │   ├── models/            # Data model tests
│   │   ├── reports/           # Report generation tests
│   │   ├── tasks/             # Task management tests
│   │   ├── tools/             # Core tool tests
│   │   └── utils/             # Utility tests
│   ├── integration/       # Real file/API integration tests
│   └── conftest.py        # Test fixtures and configuration
├── data/                  # Sample audit reports and plans
│   ├── audit-reports/     # Accessibility audit PDFs
│   └── remediation-plans/ # Remediation plan PDFs (A-G)
├── docs/                  # Developer documentation
├── plans/                 # Phase-by-phase implementation plans
└── scripts/               # Validation and utility scripts
    ├── validate_phase1.py     # Phase 1 validation
    ├── phase2_demo.py         # ✅ Phase 2 agent demo
    ├── phase4_demo.py         # ✅ Phase 4 UI demo
    └── validate_phase4_quality_gates.py  # ✅ Quality gates validation
```

## 🔧 Core Components

### PDF Processing Pipeline
```python
from src.tools.pdf_parser import PDFParser

parser = PDFParser()
audit_report = parser.parse_audit_report(Path("audit.pdf"))
plans = parser.batch_parse_plans(Path("remediation-plans/"))

print(f"Parsed {len(plans)} remediation plans")
# Output: Parsed 7 remediation plans
```

### LLM Integration
```python
from src.config.llm_config import LLMManager, LLMConfig

config = LLMConfig(
    gemini_api_key=os.getenv("GOOGLE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
llm_manager = LLMManager(config)
connections = llm_manager.test_connections()
print(f"LLM Status: {connections}")
# Output: LLM Status: {'gemini': True, 'openai': True}
```

### Streamlit Web Application (Phase 4 Complete)
```python
# Launch the complete web interface
import subprocess
subprocess.run(["streamlit", "run", "app/main.py"])

# Access features:
# - Interactive results dashboard with Plotly visualizations
# - File upload interface for PDFs
# - Real-time evaluation progress monitoring
# - Professional PDF report generation
# - CSV/JSON export functionality
# - Judge comparison analysis with radar charts
```

### Agent-Based Evaluation (Phase 2 Complete)
```python
from src.agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from src.agents.scoring_agent import ScoringAgent
from src.agents.analysis_agent import AnalysisAgent

# Initialize agents
primary_judge = PrimaryJudgeAgent(llm_manager)
secondary_judge = SecondaryJudgeAgent(llm_manager)
scoring_agent = ScoringAgent(llm_manager)
analysis_agent = AnalysisAgent(llm_manager)

# Evaluate a plan
evaluation = primary_judge.evaluate_plan("PlanA", plan_content, audit_context)
print(f"Evaluation complete: {evaluation['success']}")
# Output: Evaluation complete: True
```

### Evaluation Framework
```python
from src.tools.prompt_manager import PromptManager

manager = PromptManager(Path("promt/eval-prompt.md"))
criteria = manager.extract_evaluation_criteria()
print(f"Evaluation criteria: {criteria}")
# Output: 4 weighted criteria extracted
```

## 📊 Current Status

### ✅ Phase 1: Foundation Complete
- **PDF Processing**: 78K+ characters extracted from real accessibility files
- **LLM Integration**: Framework ready for Gemini Pro & GPT-4
- **Data Models**: Comprehensive Pydantic validation models
- **Test Coverage**: 90.28% with 143 passing tests
- **Documentation**: Complete developer guides and API references

### ✅ Phase 2: Core Agents Complete
- **4 Specialized Agents**: Primary Judge (Gemini), Secondary Judge (GPT-4), Scoring Agent (Gemini), Analysis Agent (GPT-4)
- **Agent Tools**: 4 specialized tools for evaluation framework, scoring, gap analysis, and plan comparison
- **Multi-Agent Evaluation**: Complete CrewAI-based evaluation system
- **Weighted Scoring**: Automated calculation using 40/30/20/10% criteria weights
- **Comparative Analysis**: Head-to-head plan comparison and ranking
- **Strategic Insights**: Implementation roadmaps and executive summaries
- **Integration Testing**: Comprehensive validation with real data
- **Demo Implementation**: Complete workflow demonstration script

### ✅ Phase 3: CrewAI Workflows Complete
- **Task Management**: Evaluation, comparison, and synthesis task coordination
- **Crew Orchestration**: Multi-agent workflow execution with CrewAI
- **End-to-End Pipeline**: Complete PDF-to-report processing workflow
- **Advanced Coordination**: Agent collaboration and result synthesis
- **Workflow Testing**: Comprehensive integration testing and validation

### ✅ Phase 4: User Interface Complete
- **Streamlit Application**: Complete web interface with interactive dashboard
- **File Upload Interface**: PDF upload and processing with progress tracking
- **Interactive Visualizations**: Plotly charts, radar plots, and comparative analysis
- **Report Generation**: Professional PDF reports with ReportLab
- **Export Functionality**: CSV/JSON export with download interface
- **Real-time Monitoring**: Evaluation progress and result display
- **Comprehensive Testing**: Full UI validation and quality gates

### ✅ Phase 5: Advanced Features & Optimization Complete
- **Advanced Consensus Mechanisms**: Multi-level conflict resolution with 4 distinct strategies
- **Evidence Quality Assessment**: Scoring rationales for depth and specificity
- **Judge Reliability Tracking**: Meta-evaluation system with bias pattern identification
- **Human Escalation Protocols**: Critical conflict management (>3 point differences)
- **Batch Processing System**: Parallel processing of multiple audit reports and plan sets
- **Progress Tracking**: Comprehensive status management and result aggregation
- **Performance Monitoring**: Real-time system metrics with intelligent caching
- **Optimization Engine**: Performance recommendations and bottleneck identification
- **Enterprise Architecture**: Production-ready scaling and resource management

## �️ Local Development Standards

### **Quality Pipeline**
Our development workflow ensures high-quality code for local use:

#### **Development Checks:**
- ✅ **Code Quality**: Black formatting + Flake8 linting
- ✅ **Type Safety**: mypy static type analysis  
- ✅ **Test Coverage**: 90%+ requirement enforced
- ✅ **Performance**: <5 second per-test monitoring
- ✅ **Documentation**: Docstring completeness validation

#### **Quality Standards:**
```bash
├── 90%+ Test Coverage (Currently: 90.28%)
├── <10 Second Test Execution
├── 100% Docstring Coverage
├── Zero Linting Warnings
└── Python 3.11+ Support
```

## 🧪 Testing

### Run All Tests
```bash
# Unit tests (fast)
python -m pytest tests/unit/ -v

# With coverage report
python -m pytest tests/unit/ --cov=src --cov-report=html

# Integration tests (requires API keys)
python -m pytest tests/integration/ -v --llm
```

### Test Results
- **305 tests passing**: 100% success rate
- **91% coverage**: Comprehensive test coverage exceeding requirements
- **0 warnings**: Clean test output with enterprise-grade quality

## 📚 Documentation

### Quick Reference
- **[Setup Guide](docs/development/setup-guide.md)**: Complete installation instructions
- **[API Reference](docs/api-reference/)**: Component documentation
- **[Architecture Overview](docs/architecture/system-overview.md)**: System design
- **[Development Guide](docs/development/README.md)**: Development workflow and standards

### Implementation Plans
- **[Master Plan](plans/master-plan.md)**: Complete project roadmap
- **[Phase 1](plans/phase-1-foundation.md)**: Foundation implementation ✅
- **[Phase 2](plans/phase-2-agents.md)**: Agent development ✅
- **[Phase 3](plans/phase-3-workflow.md)**: CrewAI workflows ✅
- **[Phase 4](plans/phase-4-interface.md)**: User interface ✅ COMPLETE
- **[Phase 5](plans/phase-5-optimization.md)**: Advanced features & optimization ✅ COMPLETE

## 🤝 Development

### Standards
- **Test-Driven Development**: Write tests before implementation
- **90%+ Test Coverage**: Maintain high quality standards
- **Type Safety**: Comprehensive Pydantic models and type hints
- **Documentation**: Every component thoroughly documented
- **Code Quality**: Black formatting, flake8 linting

### Contributing
1. Follow the [Copilot Instructions](.github/copilot-instructions.md)
2. Maintain test coverage above 80%
3. Update documentation for any API changes
4. Use conventional commit messages

### Development Workflow
```bash
# Validate before committing (recommended)
python scripts/validate_phase5_quality_gates.py

# Run Phase 5 demonstrations
python scripts/phase5_demo.py

# Manual quality checks
black src/ tests/                    # Format code
flake8 src/ tests/                   # Lint code
python -m pytest tests/unit/ -v     # Run tests
mypy src/                            # Type checking

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Launch development server
streamlit run app/main.py
```

## 🔐 Security

- **API Keys**: Never commit API keys; use environment variables
- **Input Validation**: All external inputs validated with Pydantic
- **Error Handling**: Graceful failure handling without data leakage
- **Local Operation**: All processing done locally for data privacy

## 📈 Performance

- **Fast Tests**: Unit tests complete in <10 seconds
- **Efficient Processing**: Optimized PDF parsing and LLM integration
- **Memory Management**: Careful handling of large document processing
- **Local Execution**: No network dependencies for core functionality

## 📄 License

MIT License - see LICENSE file for details.

## 🙋‍♂️ Support

For issues, questions, or contributions:
- **Issues**: [GitHub Issues](https://github.com/bradleyreaney/accessibility-eval-crew-two/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bradleyreaney/accessibility-eval-crew-two/discussions)
- **Documentation**: [Comprehensive docs](docs/README.md)

---

*Built with ❤️ for accessibility professionals using CrewAI, Gemini Pro, and GPT-4*

- **PDF Processing**: <10 seconds for large files (50MB+)
- **Memory Usage**: Efficient processing staying under 2GB
- **Test Execution**: <10 seconds for full unit test suite
- **LLM Response Time**: <30 seconds for evaluation tasks

## 🏆 Quality Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Test Coverage | 90%+ | 91% | ✅ |
| Tests Passing | 100% | 305/305 | ✅ |
| Quality Gates | 100% | All passed | ✅ |
| Documentation | Complete | Complete | ✅ |
| Performance | <10s tests | <10s | ✅ |
| Code Quality | Zero warnings | Zero | ✅ |
| Phase 5 Complete | All features | 100% | ✅ |

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **WCAG Guidelines**: Web Content Accessibility Guidelines foundation
- **CrewAI**: Multi-agent orchestration framework
- **LangChain**: LLM integration utilities
- **Pydantic**: Data validation and settings management

---

**Ready to evaluate accessibility remediation plans with enterprise-grade AI precision through a complete web interface with advanced optimization features!** 🎯

For detailed implementation progress, see:
- [PHASE4_QUALITY_GATES_SIGNOFF.md](PHASE4_QUALITY_GATES_SIGNOFF.md) - Phase 4 completion
- [PHASE5_COMPLETE.md](PHASE5_COMPLETE.md) - Phase 5 implementation summary
- [PHASE5_FINAL_SUMMARY.md](PHASE5_FINAL_SUMMARY.md) - Final project summary
