# LLM as a Judge - Accessibility Evaluation System

*Enterprise-ready AI system for evaluating accessibility remediation plans using advanced multi-agent LLM workflows*

[![Tests](https://img.shields.io/badge/tests-377%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)]()
[![Phase](https://img.shields.io/badge/phase-5%20complete-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## 🎯 Overview

This system leverages **Large Language Models as Judges** to provide comprehensive, unbiased evaluation of accessibility remediation plans. Using CrewAI for multi-agent orchestration, it combines the expertise of Gemini Pro and GPT-4 to deliver professional-grade accessibility assessments through a complete Streamlit web application with enterprise-ready advanced features.

**Status: All 5 Phases Complete** - Enterprise-ready system with advanced consensus mechanisms, batch processing, and performance monitoring (August 2025).

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
├── app/main.py           # Streamlit Web Application
├── src/                  # Core implementation
│   ├── agents/           # CrewAI agents (judge, scoring, analysis)
│   ├── config/           # LLM connections and configuration  
│   ├── models/           # Pydantic data models and validation
│   ├── tools/            # PDF parsing, prompt management
│   ├── reports/          # PDF and export generation
│   ├── consensus/        # Advanced consensus mechanisms
│   ├── batch/            # Batch processing system
│   └── monitoring/       # Performance monitoring
├── tests/                # Comprehensive test suite (98% coverage)
│   ├── unit/             # Module-specific unit tests
│   └── integration/      # Real file/API integration tests
├── data/                 # Sample audit reports and plans
├── docs/                 # Developer documentation
└── scripts/              # Validation and demo scripts
```

*See [docs/development/setup-guide.md](docs/development/setup-guide.md) for detailed structure and setup information.*

## 🔧 Core Components

The system provides a complete evaluation pipeline:

- **PDF Processing**: Automated parsing of audit reports and remediation plans
- **Multi-Agent Evaluation**: 4 specialized CrewAI agents with dual LLM approach
- **Streamlit Web Interface**: Complete dashboard with interactive visualizations  
- **Professional Reports**: PDF generation with scoring and recommendations
- **Advanced Features**: Consensus mechanisms, batch processing, and performance monitoring

*See [docs/api-reference/](docs/api-reference/) for detailed API documentation and code examples.*

## 📊 Implementation Status

### ✅ All 5 Phases Complete

**Enterprise-ready system with comprehensive features:**

- **Phase 1**: Foundation (PDF processing, LLM integration, data models)
- **Phase 2**: Multi-agent system (4 specialized CrewAI agents with Gemini Pro & GPT-4)
- **Phase 3**: Workflow orchestration (complete task coordination and execution)
- **Phase 4**: Web interface (Streamlit application with interactive visualizations)
- **Phase 5**: Advanced features (consensus mechanisms, batch processing, performance monitoring)

**Current Metrics:**
- **377 tests passing** with **98% coverage**
- **4 specialized agents** with dual LLM integration
- **Complete web interface** with professional PDF reports
- **Enterprise features** including advanced consensus and batch processing

*See [docs/development/phase-reports/](docs/development/phase-reports/) for detailed completion documentation.*

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
├── 98% Test Coverage (Currently: 98%)
├── <10 Second Test Execution
├── 100% Docstring Coverage
├── Zero Linting Warnings
└── Python 3.11+ Support
```

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
- **377 tests passing**: 100% success rate
- **98% coverage**: Comprehensive test coverage exceeding requirements
- **0 warnings**: Clean test output with enterprise-grade quality

## 📚 Documentation

### Quick Reference
- **[Setup Guide](docs/development/setup-guide.md)**: Complete installation instructions
- **[API Reference](docs/api-reference/)**: Component documentation
- **[Architecture Overview](docs/architecture/system-overview.md)**: System design
- **[Development Guide](docs/development/README.md)**: Development workflow and standards

### Implementation Plans
- **[Master Plan](plans/master-plan.md)**: Complete project roadmap  
- **[Phase Reports](docs/development/phase-reports/)**: Detailed completion documentation ✅
- **[Quality Assurance](docs/development/quality-assurance/)**: Testing and validation reports ✅

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

## 🔐 Security & Performance

- **API Keys**: Environment variables only, never committed
- **Input Validation**: All external inputs validated with Pydantic  
- **Local Operation**: All processing done locally for data privacy
- **Efficient Processing**: <10 second test execution, optimized PDF parsing
- **Memory Management**: Careful handling of large document processing

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For issues, questions, or contributions:
- **Issues**: [GitHub Issues](https://github.com/bradleyreaney/accessibility-eval-crew-two/issues)
- **Documentation**: [Comprehensive docs](docs/README.md)
- **Development**: Follow [Copilot Instructions](.github/copilot-instructions.md)

---

**Ready to evaluate accessibility remediation plans with enterprise-grade AI precision!** 🎯

*Built with ❤️ for accessibility professionals using CrewAI, Gemini Pro, and GPT-4*
