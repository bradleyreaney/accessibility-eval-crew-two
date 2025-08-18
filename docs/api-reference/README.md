# API Reference

Complete API documentation for all system components.

## 🎯 Component Documentation

### Core Applications
- **[report-generator.md](./report-generator.md)** - PDF generation and export functionality

### Agents & Tools
- **[agents-api.md](./agents-api.md)** - CrewAI agent implementations
- **[agent-tools.md](./agent-tools.md)** - Specialized agent tools
- **[workflow-controller.md](./workflow-controller.md)** - Task orchestration

### Core Components  
- **[pdf-parser.md](./pdf-parser.md)** - Document processing pipeline
- **[llm-config.md](./llm-config.md)** - LLM integration and configuration
- **[evaluation-models.md](./evaluation-models.md)** - Pydantic data structures

### Advanced Features (Phase 5)
- **[consensus-engine.md](./consensus-engine.md)** - Advanced consensus mechanisms
- **[batch-processor.md](./batch-processor.md)** - Batch processing system
- **[performance-monitor.md](./performance-monitor.md)** - Performance monitoring

## 🔧 Usage Patterns

### Basic Usage
```python
from src.tools.pdf_parser import PDFParser
from src.config.llm_config import LLMManager

# Initialize components
parser = PDFParser()
llm_manager = LLMManager.from_env()
```

### Advanced Integration
```python
from src.agents.judge_agent import PrimaryJudgeAgent
from src.utils.workflow_controller import WorkflowController

# Complete evaluation pipeline
controller = WorkflowController()
result = await controller.evaluate_plans(audit_report, plans)
```

## 📊 Quick Reference

### Return Types
- **EvaluationResult**: Agent evaluation output
- **DocumentContent**: Parsed PDF content  
- **EvaluationReport**: Complete assessment report
- **BatchResult**: Batch processing output

### Status Codes
- `SUCCESS`: Operation completed successfully
- `ERROR`: Processing error occurred
- `TIMEOUT`: Operation exceeded time limit
- `CONFLICT`: Judge disagreement requiring resolution

## 🔗 Navigation

- **[← Back to Documentation Hub](../README.md)**
- **[Examples →](../examples/)**
- **[Architecture →](../architecture/)**
