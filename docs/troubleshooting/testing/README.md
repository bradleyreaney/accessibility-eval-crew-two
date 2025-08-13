# Testing Troubleshooting

This directory contains troubleshooting guides for testing-related issues and warnings.

## Test Warnings & Analysis

### Unit Test Warnings
- **[UNIT_TEST_WARNINGS_ANALYSIS.md](./UNIT_TEST_WARNINGS_ANALYSIS.md)** - Comprehensive analysis of unit test warnings
  - 207 warnings breakdown and explanations
  - CrewAI framework deprecation warnings
  - Langchain/LangchainCore warnings
  - pytest-asyncio configuration issues
  - Resolution strategies and impact assessment

## Common Testing Issues

### Warning Categories
1. **pytest-asyncio Configuration** - Resolved with proper pytest.ini setup
2. **CrewAI Framework Deprecations** - Framework-level warnings, not code issues
3. **Langchain Dependencies** - Ecosystem evolution warnings
4. **Dependency Version Conflicts** - Version pinning solutions

### Test Coverage Challenges
- **Coverage Gaps**: Identification and resolution strategies
- **Mock Configuration**: Complex LLM integration testing
- **Agent Testing**: CrewAI agent testing patterns
- **Integration Tests**: API key management and environment setup

### Performance Issues
- **Test Execution Time**: Optimization for CI/CD pipelines
- **Memory Usage**: Large model and framework overhead
- **Parallel Testing**: Configuration for multi-Python environments

## Navigation

- **[← Back to Troubleshooting](../README.md)**
- **[CI/CD Issues →](../ci-cd/)**
- **[Development Docs →](../../development/)**
- **[Quality Assurance →](../../development/quality-assurance/)**

## Quick Reference

### Run Tests with Warnings Analysis
```bash
# Run tests with warning details
python -m pytest tests/ -v --tb=short

# Run with warning suppression
python -m pytest tests/ -v --disable-warnings

# Coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

### Warning Management
```bash
# Check specific warning categories
python -m pytest tests/ -W error::DeprecationWarning
python -m pytest tests/ -W ignore::pytest.PytestUnraisableExceptionWarning
```

### Test Debugging
```bash
# Run single test with full output  
python -m pytest tests/unit/agents/test_agents.py::TestAnalysisAgent::test_generate_strategic_analysis -v -s

# Run with pdb debugging
python -m pytest tests/unit/agents/test_agents.py --pdb

# Test specific module
python -m pytest tests/unit/agents/ -v
python -m pytest tests/unit/tools/ -v
python -m pytest tests/unit/config/ -v
```

## Best Practices

- **Warning Suppression**: Only suppress framework-level warnings, not code warnings
- **Test Isolation**: Ensure tests don't affect each other
- **Mock Strategy**: Use appropriate mocking for external dependencies
- **Coverage Goals**: Maintain 90%+ coverage while focusing on meaningful tests
- **CI Integration**: Configure tests for reliable CI/CD execution
