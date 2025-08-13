# Report Generator API Reference

*Professional PDF and data export functionality for evaluation results*

## 📄 EvaluationReportGenerator

Enhanced report generator providing professional PDF reports, CSV/JSON exports, and complete report packages.

### Class Definition
```python
class EvaluationReportGenerator:
    """
    Generator for comprehensive evaluation reports.
    
    Creates formatted reports from evaluation results including:
    - Executive summary
    - Detailed plan analysis
    - Score comparisons
    - Synthesis recommendations
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
    """Generate a comprehensive PDF evaluation report"""
```

**Parameters:**
- `evaluation_results`: Complete evaluation data structure
- `evaluation_input`: Original input data for context
- `output_path`: Custom output location (optional)
- `report_type`: Report template type

**Report Types:**
- `"comprehensive"`: Complete analysis with all sections
- `"executive"`: High-level summary for stakeholders
- `"detailed"`: In-depth technical analysis
- `"comparative"`: Side-by-side plan comparison
- `"synthesis"`: Strategic recommendations focus

### CSV Export
```python
def generate_csv_export(
    self,
    evaluation_results: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """Generate CSV export of evaluation scores and rankings"""
```

**Output Columns:**
- Plan Name
- Primary Score
- Secondary Score
- Final Score
- Strategic Prioritization
- Technical Specificity
- Comprehensiveness
- Long-Term Vision
- Overall Ranking

### JSON Export
```python
def generate_json_export(
    self,
    evaluation_results: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """Generate JSON export of complete evaluation results"""
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
    "evaluation_results": {
        // Complete evaluation data
    }
}
```

## 🎯 Specialized Report Types

### Executive Summary
```python
def _generate_executive_summary(
    self,
    evaluation_results: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """Generate executive summary report"""
```

**Features:**
- High-level findings and recommendations
- Key metrics and rankings
- Strategic overview for decision makers
- Concise 2-3 page format

### Detailed Analysis
```python
def _generate_detailed_analysis(
    self,
    evaluation_results: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """Generate detailed analysis report"""
```

**Features:**
- Comprehensive scoring breakdown
- Detailed criteria analysis
- Individual plan evaluations
- Technical implementation guidance

### Comparison Analysis
```python
def _generate_comparison_analysis(
    self,
    evaluation_results: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """Generate comparison analysis report"""
```

**Features:**
- Side-by-side plan comparison
- Ranking justification
- Strengths and weaknesses analysis
- Selection criteria guidance

### Synthesis Recommendations
```python
def _generate_synthesis_recommendations(
    self,
    evaluation_results: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """Generate synthesis recommendations report"""
```

**Features:**
- Strategic recommendations
- Implementation roadmap
- Risk assessment
- Next steps guidance

## 📦 Batch Report Generation

### Complete Report Package
```python
def generate_complete_report_package(
    self,
    evaluation_results: Dict[str, Any],
    output_dir: Optional[Path] = None
) -> Dict[str, Path]:
    """Generate complete report package with all report types"""
```

**Package Contents:**
- Executive Summary PDF
- Detailed Analysis PDF
- Comparison Analysis PDF
- Synthesis Recommendations PDF
- Complete Data CSV
- Complete Data JSON

**Return Value:**
```python
{
    "executive": Path("executive_summary.pdf"),
    "detailed": Path("detailed_analysis.pdf"),
    "comparative": Path("comparison_analysis.pdf"),
    "synthesis": Path("synthesis_recommendations.pdf"),
    "csv": Path("evaluation_data.csv"),
    "json": Path("evaluation_data.json")
}
```

## 🎨 PDF Report Components

### Title Page
```python
def _create_title_page(self, results: Dict[str, Any], report_type: str) -> List:
    """Create professional title page with branding and metadata"""
```

**Elements:**
- Report title and type
- Generation timestamp
- Evaluation summary
- Professional styling

### Executive Summary Section
```python
def _create_executive_summary(self, results: Dict[str, Any]) -> List:
    """Create executive summary with key findings"""
```

**Content:**
- Overall evaluation summary
- Top-ranked plans
- Key recommendations
- Decision support information

### Scoring Overview
```python
def _create_scoring_overview(self, results: Dict[str, Any]) -> List:
    """Create comprehensive scoring tables and charts"""
```

**Elements:**
- Overall rankings table
- Criteria-based scoring
- Judge agreement analysis
- Visual score comparisons

### Detailed Analysis
```python
def _create_detailed_analysis(self, results: Dict[str, Any]) -> List:
    """Create detailed plan-by-plan analysis"""
```

**Content:**
- Individual plan evaluations
- Strengths and weaknesses
- Improvement recommendations
- Technical details

### Synthesis Section
```python
def _create_synthesis_section(self, results: Dict[str, Any]) -> List:
    """Create synthesis recommendations and next steps"""
```

**Elements:**
- Strategic recommendations
- Implementation guidance
- Risk considerations
- Success metrics

## 🎯 Styling and Formatting

### Professional Styling
- **ReportLab Styles**: Professional document formatting
- **Consistent Branding**: Unified visual identity
- **Table Styling**: Professional table layouts with proper formatting
- **Chart Integration**: High-quality embedded visualizations

### Template System
- **Flexible Templates**: Customizable report structures
- **Consistent Layout**: Standardized page layouts and styling
- **Dynamic Content**: Adaptive content based on evaluation results
- **Professional Quality**: Enterprise-grade report appearance

## 📈 Chart Integration

### Matplotlib Integration
```python
# Chart generation for PDF embedding
import matplotlib.pyplot as plt

def _create_score_chart(self, data: Dict) -> plt.Figure:
    """Create score comparison chart for PDF"""
```

### Chart Types
- **Bar Charts**: Score comparisons
- **Radar Charts**: Multi-criteria analysis
- **Scatter Plots**: Judge agreement visualization
- **Tables**: Detailed scoring breakdowns

## 🔧 Configuration Options

### Output Settings
```python
# Default configuration
self.output_dir = Path("output/reports")
self.styles = getSampleStyleSheet()
```

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

### CSV Export
```python
csv_path = generator.generate_csv_export(evaluation_results)
```

### Complete Package
```python
package_paths = generator.generate_complete_report_package(
    evaluation_results,
    output_dir=Path("output/complete_reports")
)
```

### Custom Executive Summary
```python
exec_path = generator._generate_executive_summary(
    evaluation_results,
    output_path=Path("custom_executive.pdf")
)
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
    "plans": {
        "plan_name": {
            "scores": {
                "primary_score": float,
                "secondary_score": float, 
                "final_score": float
            },
            "criteria_scores": Dict[str, float],
            "analysis": str,
            "recommendations": List[str]
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

## 📚 Dependencies

### Required Libraries
- **ReportLab**: Professional PDF generation
- **Pandas**: Data manipulation and CSV export
- **Matplotlib**: Chart generation for PDF embedding
- **Plotly**: Interactive chart generation
- **Pathlib**: Modern file path handling

---

For complete implementation examples, see the [Phase 4 Implementation Guide](../development/phase4-complete.md).
