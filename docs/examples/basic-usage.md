# Basic Usage Examples

Simple examples to get started with the accessibility evaluation system.

# Basic Usage Examples

Simple examples to get started with the accessibility evaluation system.

## 🎯 5-Minute Quick Start

### 1. Environment Setup
```bash
# Clone and setup
git clone https://github.com/bradleyreaney/accessibility-eval-crew-two.git
cd accessibility-eval-crew-two

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```


```bash


```



## 🔧 Core Component Usage

### PDF Processing
```python
from pathlib import Path
from src.tools.pdf_parser import PDFParser

# Initialize parser
parser = PDFParser()

# Parse audit report
audit_report = parser.parse_audit_report(Path("data/audit-reports/example-audit.pdf"))
print(f"Audit title: {audit_report.title}")
print(f"Content length: {len(audit_report.content)} characters")

# Parse remediation plans
plans_dir = Path("data/remediation-plans")
plans = parser.batch_parse_plans(plans_dir)
print(f"Found {len(plans)} remediation plans")

for plan in plans:
    print(f"- {plan.title}: {len(plan.content)} characters")
```

### LLM Configuration
```python
from src.config.llm_config import LLMManager, LLMConfig
import os

# Initialize LLM manager from environment
llm_manager = LLMManager.from_env()

# Test connections
connections = llm_manager.test_connections()
print(f"Gemini Pro: {'✅' if connections['gemini'] else '❌'}")
print(f"GPT-4: {'✅' if connections['openai'] else '❌'}")

# Manual configuration
config = LLMConfig(
    gemini_api_key=os.getenv("GOOGLE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    gemini_model="gemini-pro",
    openai_model="gpt-4"
)
llm_manager = LLMManager(config)
```

### Single Agent Evaluation
```python
from src.agents.judge_agent import PrimaryJudgeAgent

# Initialize primary judge
judge = PrimaryJudgeAgent(llm_manager)

# Evaluate a single plan
result = judge.evaluate_plan(
    plan_id="Plan A",
    plan_content=plans[0].content,
    audit_context=audit_report.content
)

# Display results
print(f"Plan: {result['plan_id']}")
print(f"Overall Score: {result['weighted_score']:.1f}/10")
print(f"Strategic Prioritization: {result['scores']['strategic_prioritization']}")
print(f"Technical Specificity: {result['scores']['technical_specificity']}")
print(f"Comprehensiveness: {result['scores']['comprehensiveness']}")
print(f"Long-term Vision: {result['scores']['long_term_vision']}")
print(f"Reasoning: {result['reasoning'][:200]}...")
```

### Multi-Agent Workflow
```python
from src.agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from src.agents.scoring_agent import ScoringAgent
from src.agents.analysis_agent import AnalysisAgent

# Initialize all agents
primary_judge = PrimaryJudgeAgent(llm_manager)
secondary_judge = SecondaryJudgeAgent(llm_manager)
scoring_agent = ScoringAgent(llm_manager)
analysis_agent = AnalysisAgent(llm_manager)

# Evaluate all plans with both judges
primary_results = []
secondary_results = []

for plan in plans:
    # Primary evaluation
    primary_result = primary_judge.evaluate_plan(
        plan.title, plan.content, audit_report.content
    )
    primary_results.append(primary_result)
    
    # Secondary evaluation  
    secondary_result = secondary_judge.evaluate_plan(
        plan.title, plan.content, audit_report.content
    )
    secondary_results.append(secondary_result)

# Calculate final scores and rankings
final_scores = scoring_agent.calculate_weighted_scores(
    primary_results + secondary_results
)

ranked_plans = scoring_agent.rank_plans(final_scores)

# Generate strategic analysis
analysis = analysis_agent.analyze_evaluation_results(ranked_plans)

# Display top recommendation
top_plan = ranked_plans[0]
print(f"🏆 Top Recommendation: {top_plan['plan_id']}")
print(f"Final Score: {top_plan['final_score']:.1f}/10")
print(f"Analysis: {analysis['executive_summary'][:300]}...")
```

### Report Generation
```python
from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator
from datetime import datetime

# Initialize report generator
report_generator = EvaluationReportGenerator()

# Generate comprehensive PDF report
report_data = {
    "audit_title": audit_report.title,
    "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
    "ranked_plans": ranked_plans,
    "analysis": analysis,
    "primary_evaluations": primary_results,
    "secondary_evaluations": secondary_results
}

# Generate PDF
pdf_path = report_generator.generate_comprehensive_report(
    report_data, 
    output_path="evaluation_report.pdf"
)
print(f"Report generated: {pdf_path}")

# Generate CSV export
csv_path = report_generator.export_to_csv(ranked_plans, "results.csv")
print(f"CSV exported: {csv_path}")
```



### File Upload and Processing

2. **Upload Files**: Use the sidebar to upload audit report and remediation plans
3. **Monitor Progress**: Watch real-time evaluation progress
4. **View Results**: Interactive dashboard with visualizations
5. **Download Reports**: PDF, CSV, and JSON exports available

### Dashboard Features
- **Radar Charts**: Visual comparison of evaluation criteria
- **Scatter Plots**: Score distribution analysis  
- **Bar Charts**: Plan rankings and comparisons
- **Progress Tracking**: Real-time evaluation status
- **Export Options**: Multiple format downloads

## 🧪 Testing Your Setup

### Quick Validation
```python
# Test script to validate installation
from src.tools.pdf_parser import PDFParser
from src.config.llm_config import LLMManager
from pathlib import Path

def test_setup():
    print("🔍 Testing setup...")
    
    # Test PDF parsing
    parser = PDFParser()
    print("✅ PDF parser initialized")
    
    # Test LLM connections
    try:
        llm_manager = LLMManager.from_env()
        connections = llm_manager.test_connections()
        print(f"✅ LLM connections: {connections}")
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
    
    # Test data directory
    data_dir = Path("data")
    if data_dir.exists():
        print(f"✅ Data directory found with {len(list(data_dir.glob('**/*.pdf')))} PDF files")
    else:
        print("⚠️ Data directory not found - using sample data")
    
    print("🎉 Setup validation complete!")

if __name__ == "__main__":
    test_setup()
```

### Run Official Validation
```bash
# Run comprehensive validation scripts
python scripts/validate_phase4_quality_gates.py
python scripts/phase4_demo.py

# Expected output: All quality gates passed, full functionality demonstrated
```

## 📋 Next Steps

1. **Explore Advanced Features**: Try batch processing and consensus mechanisms
2. **Customize Agents**: Modify agent parameters and tools
3. **Create Custom Reports**: Build custom report templates
4. **Integration**: Integrate with your existing workflows

## 🔗 Related Documentation

- **[Multi-Agent Workflow Examples](./multi-agent-workflow.md)**
- **[Report Generation Examples](./report-generation.md)**

- **[API Reference](../api-reference/)**
