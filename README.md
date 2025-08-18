# LLM as a Judge - Accessibility Evaluation System

*Enterprise-ready AI system for evaluating accessibility remediation plans using advanced multi-agent LLM workflows with comprehensive error resilience*

[![Tests](https://img.shields.io/badge/tests-351%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)]()
[![Phase](https://img.shields.io/badge/phase-5%20complete-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## 🎯 Overview

This system leverages **Large Language Models as Judges** to provide comprehensive, unbiased evaluation of accessibility remediation plans. Using CrewAI for multi-agent orchestration, it combines the expertise of Gemini Pro and GPT-4 to deliver professional-grade accessibility assessments through a command-line interface with automated PDF report generation and robust error resilience.

**Status: All 5 Phases Complete** - Enterprise-ready system with advanced consensus mechanisms, batch processing, performance monitoring, and comprehensive LLM error resilience. All quality gates passing with 93.23% test coverage (August 2025).

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
- 💻 **Command-Line Interface**: Full-featured CLI with automated file discovery
- 📊 **Automated PDF Reports**: Professional reports generated automatically after evaluation
- 📁 **Automated File Discovery**: Automatic detection of audit reports and remediation plans
- 🎯 **WCAG Aligned**: Evaluation framework based on accessibility best practices
- 🚀 **Advanced Consensus**: Multi-level conflict resolution with expert judge coordination
- ⚡ **Batch Processing**: Parallel evaluation of multiple reports with progress tracking
- 📈 **Performance Monitoring**: Real-time metrics, intelligent caching, and optimization recommendations
- 🛡️ **LLM Error Resilience**: Graceful degradation when one LLM fails, partial results with NA reporting
- 🔄 **Workflow Integration**: Seamless integration of resilience manager into evaluation workflow
- 📊 **Availability Monitoring**: Real-time LLM health tracking and status reporting
- 🎛️ **Partial Evaluation**: System continues operating with reduced capability when some LLMs are unavailable
- 📋 **Enhanced Reporting**: Professional reports with NA sections, availability status, and completion statistics
- 📈 **Completion Tracking**: Detailed completion rate and status tracking in all reports

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

# Configure environment variables (REQUIRED)
cp .env.example .env
# Edit .env with your API keys:
# GOOGLE_API_KEY=your_gemini_api_key
# OPENAI_API_KEY=your_openai_api_key
```

### Launch the Application
```bash
# Run accessibility evaluation with default settings
python main.py

# Custom evaluation with specific options
python main.py --mode parallel --consensus --reports executive,detailed

# View all available options
python main.py --help

# Dry run to validate configuration
python main.py --dry-run --verbose
```

**🔒 Environment-Only Configuration**: This application requires both `GOOGLE_API_KEY` and `OPENAI_API_KEY` environment variables to be set before running. The application will validate environment configuration and provide clear error messages if keys are missing.

**🛡️ Error Resilience**: The system includes robust error handling that ensures you get partial results even when one AI service is temporarily unavailable. Failed evaluations are clearly marked as "NA" in reports with detailed completion statistics.

**CLI Interface**: The application provides a command-line interface suitable for automation, batch processing, and integration with CI/CD pipelines. All evaluation results are generated as professional PDF reports in the `output/reports/` directory.

### Usage Examples
```bash
# Basic evaluation with sample data
python main.py

# Evaluation with custom input directories
python main.py --audit-dir /path/to/audits --plans-dir /path/to/plans

# Parallel execution with consensus building
python main.py --mode parallel --consensus --output results/evaluation-$(date +%Y%m%d)

# Generate specific report types
python main.py --reports comprehensive,executive,judge_agreement

# Dry run to validate setup without running evaluation
python main.py --dry-run --verbose
```

## 🛡️ LLM Error Resilience

The system includes comprehensive error handling that ensures reliable operation:

### Automatic Fallback
- If one LLM fails, the system automatically uses the other
- Partial results are provided instead of complete failure
- Failed evaluations are clearly marked as "NA" in reports

### Enhanced Reporting
- Professional reports include NA sections for unavailable evaluations
- Availability status shows which LLMs were available during evaluation
- Completion statistics provide detailed success rates
- Troubleshooting guidance helps resolve issues

### Example Output
```
✅ LLM availability check complete:
   Gemini Pro: Available
   GPT-4: Unavailable (Rate limit exceeded)
⚠️  Operating with 1 available LLM(s)
📊 Partial evaluation completed: 8/10 plans evaluated (80.0%)
```

## 🏗️ Architecture

### Multi-Agent System
- **Primary Judge Agent (Gemini Pro)**: Main evaluation engine with accessibility expertise
- **Secondary Judge Agent (GPT-4)**: Cross-validation and consensus building
- **Scoring Agent**: Weighted scoring calculations and ranking
- **Analysis Agent**: Strategic insights and implementation guidance

### Error Resilience Components
- **LLM Resilience Manager**: Centralized failure management and fallback coordination
- **Enhanced Workflow Controller**: Integrated resilience with availability checking
- **Enhanced Report Generator**: Professional reports with NA handling and completion statistics
- **Custom Exception Handling**: Specialized error types for different failure scenarios

### Professional Reporting
- **PDF Reports**: Executive summary, detailed analysis, comparative analysis
- **CSV/JSON Exports**: Data export with NA status and resilience information
- **Completion Summary**: Dedicated reports showing evaluation completion statistics
- **Availability Status**: Real-time LLM health tracking in reports

## 📊 Quality Assurance

### Testing Coverage
- **359 Unit Tests**: Comprehensive test coverage across all components
- **93.23% Coverage**: Meeting enterprise quality standards
- **Error Scenarios**: All failure modes thoroughly tested
- **Integration Tests**: End-to-end workflow validation

### Quality Gates
- **26 Quality Gates**: Automated validation of all system components
- **Performance Metrics**: Real-time monitoring and optimization
- **Error Resilience**: Comprehensive testing of fallback scenarios
- **Report Generation**: Validation of all report formats and content

## 📚 Documentation

### User Documentation
- **[User Guide](docs/user-guide.md)**: Complete guide for accessibility professionals
- **[Setup Guide](docs/development/setup-guide.md)**: Installation and configuration
- **[Examples](docs/examples/)**: Practical usage examples and code patterns
- **[Troubleshooting](docs/troubleshooting/)**: Common issues and solutions

### Technical Documentation
- **[API Reference](docs/api-reference/)**: Complete component documentation
- **[Architecture](docs/architecture/)**: System design and data flow
- **[Features](docs/features/)**: Comprehensive feature documentation
- **[Development](docs/development/)**: Development guides and phase reports

### LLM Error Resilience
- **[Feature Documentation](docs/features/llm-error-resilience.md)**: Complete resilience feature guide
- **[Enhancement Plan](plans/llm-error-handling-enhancement-plan.md)**: Detailed implementation plan
- **[API Reference](docs/api-reference/report-generator.md)**: Enhanced report generation with NA handling

## 🚀 Advanced Features

### Batch Processing
- Parallel evaluation of multiple audit reports and plan sets
- Progress monitoring and completion tracking
- Statistical analysis across multiple evaluations
- Enterprise-scale processing capabilities

### Performance Optimization
- Real-time performance monitoring
- Intelligent caching with 85%+ hit rates
- Memory usage optimization
- Automatic performance recommendations

### Advanced Consensus
- Multi-level conflict resolution (75% auto-resolution)
- Evidence quality assessment
- Judge reliability tracking
- Bias pattern identification

## 🔧 Development

### Quick Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd accessibility-eval-crew-two
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest

# Validate quality gates
python scripts/validate_phase5_quality_gates.py
```

### Development Standards
- **Test-Driven Development**: Write tests before implementation
- **90%+ Test Coverage**: Maintain high quality standards
- **Type Safety**: Comprehensive Pydantic models and type hints
- **Documentation**: Every component thoroughly documented

## 📞 Support & Contributing

- **Issues**: Use GitHub Issues for bug reports
- **Development**: Follow [Copilot Instructions](../.github/copilot-instructions.md)
- **Documentation**: Update docs with any changes
- **Testing**: Maintain 90%+ test coverage

---

**Ready for production use with comprehensive error resilience and professional reporting!** 🎯

**Last Updated**: January 2025  
**Version**: 5.0.0 (All Phases Complete + LLM Error Resilience Complete)  
**Status**: Production Ready with Enterprise-Grade Error Handling
