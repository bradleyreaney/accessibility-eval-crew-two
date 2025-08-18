# Code Examples & Usage Patterns

Practical examples for using the accessibility evaluation system.

## 📁 Example Categories

### 🚀 Getting Started Examples
- **[basic-usage.md](./basic-usage.md)** - Simple evaluation workflow
- **[quick-start.md](./quick-start.md)** - 5-minute setup and first evaluation

### 🤖 Agent Examples  
- **[agent-examples.md](./agent-examples.md)** - Working with individual agents
- **[multi-agent-workflow.md](./multi-agent-workflow.md)** - Complete multi-agent evaluation
- **[custom-agent-tools.md](./custom-agent-tools.md)** - Creating custom tools

### 📄 PDF Processing Examples
- **[pdf-processing.md](./pdf-processing.md)** - Document parsing and extraction
- **[batch-processing.md](./batch-processing.md)** - Processing multiple documents

### 📊 Report Generation Examples
- **[report-generation.md](./report-generation.md)** - Creating professional PDF reports
- **[export-examples.md](./export-examples.md)** - CSV, JSON, and multi-format exports



- **[custom-visualizations.md](./custom-visualizations.md)** - Creating custom charts

### 🏗️ Advanced Examples
- **[consensus-resolution.md](./consensus-resolution.md)** - Handling judge disagreements
- **[performance-optimization.md](./performance-optimization.md)** - System optimization
- **[integration-patterns.md](./integration-patterns.md)** - Integrating with other systems

## 🎯 Common Use Cases

### Basic Evaluation
```python
# Simple plan evaluation
from src.tools.pdf_parser import PDFParser
from src.agents.judge_agent import PrimaryJudgeAgent
from src.config.llm_config import LLMManager

# Setup
parser = PDFParser()
llm_manager = LLMManager.from_env()
judge = PrimaryJudgeAgent(llm_manager)

# Process documents
audit = parser.parse_audit_report("audit.pdf")
plan = parser.parse_remediation_plan("plan-a.pdf")

# Evaluate
result = judge.evaluate_plan("Plan A", plan.content, audit.content)
print(f"Score: {result['weighted_score']}")
```

### Complete Web Application
```python

import subprocess

```

### Batch Processing
```python
# Process multiple plans at once
from src.batch.batch_processor import BatchProcessor

processor = BatchProcessor()
results = processor.process_multiple_plans(
    audit_path="audit.pdf",
    plans_directory="remediation-plans/"
)
```

## 🔧 Configuration Examples

### Environment Setup
```bash
# .env file configuration
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
LOG_LEVEL=INFO
CACHE_ENABLED=true
```

### Custom Agent Configuration
```python
# Custom agent setup with specific parameters
agent = PrimaryJudgeAgent(
    llm_manager=llm_manager,
    temperature=0.2,  # More deterministic responses
    max_tokens=2000,  # Longer responses
    verbose=True      # Detailed logging
)
```

## 🧪 Testing Examples

### Unit Testing
```python
# Testing agent functionality
import pytest
from src.agents.judge_agent import PrimaryJudgeAgent

def test_agent_evaluation():
    agent = PrimaryJudgeAgent(mock_llm_manager)
    result = agent.evaluate_plan("Test Plan", "content", "context")
    assert result['success'] is True
    assert 'weighted_score' in result
```

### Integration Testing
```python
# End-to-end workflow testing
def test_complete_workflow():
    # Test complete evaluation pipeline
    workflow = WorkflowController()
    result = workflow.evaluate_plans(audit_data, plan_data)
    assert len(result['ranked_plans']) > 0
```

## 🔗 Navigation

- **[← Back to Documentation Hub](../README.md)**
- **[API Reference →](../api-reference/)**
- **[Development Guide →](../development/README.md)**

## 📋 Quick Links

- **[Setup Guide](../development/setup-guide.md)** - Initial setup
- **[Architecture](../architecture/system-overview.md)** - System design
- **[Troubleshooting](../troubleshooting/)** - Common issues
