# Report Generator API Reference

*Professional PDF and data export functionality for evaluation results with LLM resilience support*

## 📄 EvaluationReportGenerator
    # CLI integration for command-line interface

Enhanced report generator providing professional PDF reports, CSV/JSON exports, and complete report packages with comprehensive LLM resilience support including NA handling, availability status reporting, and completion statistics.

### Class Definition
```python
class EvaluationReportGenerator:
    """
    Generator for comprehensive evaluation reports with LLM resilience support.
    
    Creates formatted reports from evaluation results including:
    - Executive summary with partial evaluation support
    - Detailed plan analysis with NA sections
    - Score comparisons with availability status
    - Synthesis recommendations
    - LLM availability status reporting
    - Completion statistics and resilience information
    """
```

### Initialization
```python
def __init__(self):
    """Initialize the report generator with default configuration"""
```

**Configuration:**
- Output directory: `output/reports/`
- ReportLab styles: Sample stylesheet initialization
- Template system: Professional PDF formatting
- NA handling: Standardized NA section generation
- Availability status: LLM health monitoring integration

## 📊 Core Report Generation

### PDF Report Generation
```python
def generate_pdf_report(
    self,
    evaluation_results: Dict[str, Any],
    evaluation_input: Optional[EvaluationInput] = None,
    output_path: Optional[Path] = None,
    report_type: str = "comprehensive"
) -> Path:
    """Generate a comprehensive PDF evaluation report with NA handling"""
```

**Parameters:**
- `evaluation_results`: Complete evaluation data structure with resilience information
- `evaluation_input`: Original input data for context
- `output_path`: Custom output location (optional)
- `report_type`: Report template type

**Report Types:**
- `"comprehensive"`: Complete analysis with all sections including NA handling
- `"executive"`: High-level summary for stakeholders with partial evaluation support
- `"detailed"`: In-depth technical analysis with availability status
- `"comparative"`: Side-by-side plan comparison with completion statistics
- `"synthesis"`: Strategic recommendations focus with resilience information

### CSV Export with NA Support
```python
def generate_csv_export(
    self,
    evaluation_results: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """Generate CSV export of evaluation scores and rankings with NA status"""
```

**Output Columns:**
- Plan Name
- Status (Completed/Not Available)
- Overall Score
- Strategic Prioritization
- Technical Specificity
- Comprehensiveness
- Long-Term Vision
- NA_Reason (for unavailable evaluations)
- LLM_Used (which LLM performed the evaluation)
- Overall Ranking

### JSON Export with Resilience Information
```python
def generate_json_export(
    self,
    evaluation_results: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """Generate JSON export of complete evaluation results with resilience data"""
```

**Output Structure:**
```json
{
    "metadata": {
        "exported_at": "ISO timestamp",
        "export_type": "evaluation_results",
        "version": "1.0",
        "plans_count": 7
    },
    "completion_statistics": {
        "total_plans": 7,
        "completed_evaluations": 5,
        "na_evaluations": 2,
        "failed_evaluations": 0,
        "available_llms": ["Gemini Pro"],
        "unavailable_llms": ["GPT-4"],
        "completion_percentage": 71.4
    },
    "resilience_info": {
        "partial_evaluation": true,
        "available_llms": ["Gemini Pro"],
        "unavailable_llms": ["GPT-4"],
        "na_evaluations_count": 2,
        "completion_percentage": 71.4,
        "resilience_timestamp": "2025-01-15T10:30:00Z"
    },
    "plans": {
        "plan_name": {
            "status": "completed",
            "scores": {
                "primary_score": 8.5,
                "secondary_score": null,
                "final_score": 8.5
            },
            "criteria_scores": {
                "strategic_prioritization": 8.0,
                "technical_specificity": 9.0,
                "comprehensiveness": 8.5,
                "long_term_vision": 8.0
            },
            "analysis": "Detailed analysis...",
            "recommendations": ["Recommendation 1", "Recommendation 2"],
            "llm_used": "Gemini Pro",
            "na_reason": null
        }
    }
}
```

### Completion Summary Report
```python
def generate_completion_summary_report(
    self,
    evaluation_results: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """Generate dedicated completion summary report with statistics"""
```

**Features:**
- Completion percentage and statistics
- LLM availability status
- NA evaluation details
- Troubleshooting guidance
- Performance metrics

### CLI Report Package
```python
def generate_cli_report_package(
    self,
    evaluation_results: Dict[str, Any],
    output_dir: Optional[Path] = None
) -> Dict[str, Path]:
    """Generate complete CLI report package with all report types"""
```

**Package Contents:**
- Comprehensive PDF report
- Executive summary
- Detailed analysis
- Comparative analysis
- Synthesis recommendations
- Completion summary report
- CSV export
- JSON export

## 🎨 PDF Report Components

### Title Page
```python
def _create_title_page(self, results: Dict[str, Any], report_type: str) -> List:
    """Create professional title page with branding and metadata"""
```

**Elements:**
- Report title and type
- Generation timestamp
- Evaluation summary with completion statistics
- Professional styling

### Executive Summary Section
```python
def _create_executive_summary(self, results: Dict[str, Any]) -> List:
    """Create executive summary with key findings and partial evaluation support"""
```

**Content:**
- Overall evaluation summary
- Top-ranked plans
- Key recommendations
- Decision support information
- Partial evaluation notes (if applicable)
- Completion percentage

### Availability Status Section
```python
def _create_availability_status_section(self, availability: Dict[str, bool]) -> List:
    """Create LLM availability status section with troubleshooting guidance"""
```

**Content:**
- Available LLMs list
- Unavailable LLMs list
- Last check timestamp
- Troubleshooting guidance
- System status information

### Scoring Overview
```python
def _create_scoring_overview(self, results: Dict[str, Any]) -> List:
    """Create comprehensive scoring tables and charts with status indicators"""
```

**Elements:**
- Overall rankings table with status column
- Criteria-based scoring
- Judge agreement analysis
- Visual score comparisons
- Color-coded status indicators (green for completed, red for NA)

### Detailed Analysis
```python
def _create_detailed_analysis(self, results: Dict[str, Any]) -> List:
    """Create detailed plan-by-plan analysis with NA section support"""
```

**Content:**
- Individual plan evaluations
- Strengths and weaknesses
- Improvement recommendations
- Technical details
- NA sections for unavailable evaluations

### NA Evaluation Section
```python
def _create_na_evaluation_section(self, plan_name: str, llm_type: str, reason: str) -> List:
    """Generate standardized NA section for unavailable evaluations"""
```

**Content:**
- Plan name and status
- LLM type that was unavailable
- Reason for unavailability
- Troubleshooting guidance
- Professional formatting

### Completed Evaluation Section
```python
def _create_completed_evaluation_section(self, plan_name: str, plan_data: Dict[str, Any]) -> List:
    """Generate standardized section for completed evaluations"""
```

**Content:**
- Plan name and status
- Complete evaluation results
- Scores and analysis
- Strengths and weaknesses
- Recommendations

### Synthesis Section
```python
def _create_synthesis_section(self, results: Dict[str, Any]) -> List:
    """Create synthesis recommendations and next steps with resilience context"""
```

**Elements:**
- Strategic recommendations
- Implementation guidance
- Risk considerations
- Success metrics
- Partial evaluation considerations

## 🎯 Styling and Formatting

### Professional Styling
- **ReportLab Styles**: Professional document formatting
- **Consistent Branding**: Unified visual identity
- **Table Styling**: Professional table layouts with proper formatting
- **Chart Integration**: High-quality embedded visualizations
- **Status Indicators**: Color-coded sections for NA vs completed evaluations

### Template System
- **Flexible Templates**: Customizable report structures
- **Consistent Layout**: Standardized page layouts and styling
- **Dynamic Content**: Adaptive content based on evaluation results
- **Professional Quality**: Enterprise-grade report appearance
- **NA Handling**: Standardized NA section templates

## 📈 Chart Integration

### Matplotlib Integration
```python
# Chart generation for PDF embedding
import matplotlib.pyplot as plt

def _create_score_chart(self, data: Dict) -> plt.Figure:
    """Create score comparison chart for PDF with NA handling"""
```

### Chart Types
- **Bar Charts**: Score comparisons with NA indicators
- **Radar Charts**: Multi-criteria analysis
- **Scatter Plots**: Judge agreement visualization
- **Tables**: Detailed scoring breakdowns with status columns
- **Completion Charts**: Visual representation of completion statistics

## 🔧 Configuration Options

### PDF Settings
```python
# Document configuration
doc = SimpleDocTemplate(
    str(output_path),
    pagesize=letter,
    rightMargin=72,
    leftMargin=72,
    topMargin=72,
    bottomMargin=18
)
```

## 🚀 Usage Examples

### Basic PDF Generation
```python
generator = EvaluationReportGenerator()
pdf_path = generator.generate_pdf_report(
    evaluation_results,
    report_type="comprehensive"
)
```

### CSV Export with NA Support
```python
csv_path = generator.generate_csv_export(evaluation_results)
```

### Complete Package
```python
package_paths = generator.generate_cli_report_package(
    evaluation_results,
    output_dir=Path("output/complete_reports")
)
```

### Completion Summary Report
```python
summary_path = generator.generate_completion_summary_report(
    evaluation_results,
    output_path=Path("completion_summary.pdf")
)
```

### NA Section Generation
```python
na_section = generator._create_na_evaluation_section(
    "Plan A",
    "GPT-4",
    "Rate limit exceeded"
)
```

### Availability Status Section
```python
availability_section = generator._create_availability_status_section({
    "Gemini Pro": True,
    "GPT-4": False
})
```

## 📊 Data Requirements

### Input Data Structure
```python
evaluation_results = {
    "metadata": {
        "evaluation_id": str,
        "timestamp": datetime,
        "plans_evaluated": int
    },
    "completion_statistics": {
        "total_plans": int,
        "completed_evaluations": int,
        "na_evaluations": int,
        "failed_evaluations": int,
        "available_llms": List[str],
        "unavailable_llms": List[str],
        "completion_percentage": float
    },
    "resilience_info": {
        "partial_evaluation": bool,
        "available_llms": List[str],
        "unavailable_llms": List[str],
        "na_evaluations_count": int,
        "completion_percentage": float,
        "resilience_timestamp": str
    },
    "plans": {
        "plan_name": {
            "status": "completed" | "NA" | "failed",
            "scores": {
                "primary_score": float,
                "secondary_score": float | None, 
                "final_score": float
            },
            "criteria_scores": Dict[str, float],
            "analysis": str,
            "recommendations": List[str],
            "llm_used": str,
            "na_reason": str | None
        }
    },
    "comparative_analysis": {
        "rankings": List[Dict],
        "judge_agreement": float,
        "synthesis": str
    }
}
```

## 🛠️ Error Handling

### File Operations
- **Directory Creation**: Automatic output directory creation
- **Path Validation**: Robust file path handling
- **Permission Checks**: File write permission validation

### Data Validation
- **Input Validation**: Comprehensive input data checking
- **Format Verification**: Data structure validation
- **Error Recovery**: Graceful error handling with informative messages
- **NA Handling**: Proper handling of missing or unavailable data

### Resilience Support
- **Partial Data**: Handle incomplete evaluation results
- **NA Values**: Proper formatting of unavailable evaluations
- **Status Tracking**: Maintain evaluation status throughout processing

## 📚 Dependencies

### Required Libraries
- **ReportLab**: Professional PDF generation
- **Pandas**: Data manipulation and CSV export
- **Matplotlib**: Chart generation for PDF embedding
- **Plotly**: Interactive chart generation
- **Pathlib**: Modern file path handling

---

For complete implementation examples, see the [Phase 4 Implementation Guide](../development/phase4-complete.md) and [LLM Error Resilience Feature](../features/llm-error-resilience.md).
