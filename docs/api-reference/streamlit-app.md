# Streamlit Application API Reference

*Complete reference for the enterprise-ready Phase 5 Streamlit web application*

## 📱 AccessibilityEvaluatorApp

Main application class providing the complete web interface for the LLM as a Judge system.

### Class Definition
```python
class AccessibilityEvaluatorApp:
    """Main application class for the Streamlit interface"""
```

### Initialization
```python
def __init__(self):
    """Initialize the application"""
```

**Components initialized:**
- PDF parser for document processing
- Report generator for PDF/CSV/JSON exports
- LLM manager and crew configuration
- Workflow controller for evaluation orchestration
- Session state management

### Core Methods

#### Application Management
```python
def run(self) -> None:
    """Main application entry point"""
```
Renders the complete application interface with tabbed navigation.

#### Configuration Interface
```python
def _render_configuration_page(self) -> None:
    """Render system configuration interface"""
```
Provides API key setup, connection testing, and system validation.

#### File Upload Interface
```python
def _render_upload_interface(self) -> None:
    """Render file upload and management interface"""
```
Handles PDF file uploads with validation and processing status.

#### Evaluation Interface
```python
def _render_evaluation_interface(self) -> None:
    """Render evaluation execution interface"""
```
Provides evaluation configuration and execution with progress monitoring.

#### Results Dashboard
```python
def _render_results_dashboard(self) -> None:
    """Render comprehensive results dashboard"""
```
Interactive visualization of evaluation results with charts and analysis.

#### Export Interface
```python
def _render_export_interface(self) -> None:
    """Render export and reporting interface"""
```
Professional report generation and download functionality.

### Visualization Methods

#### Score Overview
```python
def _render_score_overview(self, results: Dict[str, Any]) -> None:
    """Render scoring overview dashboard"""
```
Displays overall scores with bar charts and ranking tables.

#### Radar Chart
```python
def _render_radar_chart(self, plans_df: pd.DataFrame) -> None:
    """Render radar chart for plan comparison"""
```
Multi-criteria comparison visualization using Plotly.

#### Judge Comparison
```python
def _render_judge_comparison(self, results: Dict[str, Any]) -> None:
    """Render judge agreement analysis"""
```
Scatter plot analysis of judge score correlation.

#### Synthesis Recommendations
```python
def _render_synthesis_recommendations(self, results: Dict[str, Any]) -> None:
    """Render synthesis and recommendations"""
```
Strategic recommendations and next steps presentation.

### Export Methods

#### PDF Report Generation
```python
def _generate_pdf_report(self, results: Dict[str, Any], report_type: str) -> Path:
    """Generate professional PDF report"""
```
Creates formatted PDF reports using ReportLab with multiple templates.

#### Data Export
```python
def _export_data_as_json(self, results: Dict[str, Any]) -> None:
def _export_summary_as_csv(self, results: Dict[str, Any]) -> None:
def _export_charts_as_images(self, results: Dict[str, Any]) -> None:
```
Multiple export formats with download interface integration.

### Utility Methods

#### Session State Management
```python
def _initialize_session_state(self) -> None:
    """Initialize Streamlit session state"""
```
Sets up application state variables and defaults.

#### System Configuration
```python
def _configure_system(self, gemini_key: str, openai_key: str) -> bool:
    """Configure LLM systems with API keys"""
```
Initializes LLM connections and validates system setup.

#### Sample Data Generation
```python
def _generate_sample_results(self) -> Dict[str, Any]:
    """Generate sample evaluation results for demonstration"""
```
Creates realistic sample data for UI development and testing.

## 📊 Data Structures

### Evaluation Results Format
```python
{
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
            "criteria_scores": {
                "strategic_prioritization": float,
                "technical_specificity": float,
                "comprehensiveness": float,
                "long_term_vision": float
            },
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

### UI State Variables
```python
# Session state keys
"system_configured": bool
"uploaded_files": List[str] 
"evaluation_results": Dict[str, Any]
"current_evaluation": Optional[str]
"workflow_status": Optional[WorkflowStatus]
```

## 🎨 UI Components

### Navigation Tabs
- **🏠 Configuration**: System setup and API key configuration
- **📁 Upload**: File upload and document management
- **⚡ Evaluate**: Evaluation execution and monitoring
- **📊 Results Dashboard**: Interactive visualization and analysis
- **📋 Export & Reports**: Report generation and download

### Interactive Elements
- **File Uploaders**: PDF document input with validation
- **Progress Bars**: Real-time evaluation progress
- **Charts**: Interactive Plotly visualizations
- **Download Buttons**: File export with multiple formats
- **Status Indicators**: System health and connection status

### Layout Structure
```
├── Sidebar (Status & Navigation)
├── Main Content Area
│   ├── Tab Navigation
│   ├── Content Panels
│   └── Action Buttons
└── Footer (Help & Information)
```

## 🔧 Configuration Options

### Display Settings
```python
st.set_page_config(
    page_title="LLM as a Judge - Accessibility Evaluator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### Chart Configurations
```python
# Plotly chart settings
fig.update_layout(
    title=chart_title,
    showlegend=True,
    height=400
)

# Streamlit chart display
st.plotly_chart(fig, use_container_width=True)
```

## 🚀 Usage Examples

### Basic Application Launch
```python
from app.main import AccessibilityEvaluatorApp

app = AccessibilityEvaluatorApp()
app.run()
```

### Custom Configuration
```python
app = AccessibilityEvaluatorApp()
app._configure_system(
    gemini_key="your_gemini_key",
    openai_key="your_openai_key"
)
```

### Programmatic Export
```python
# Generate sample results
results = app._generate_sample_results()

# Export as PDF
pdf_path = app._generate_pdf_report(results, "comprehensive")

# Export as JSON
app._export_data_as_json(results)
```

## 📱 Best Practices

### Performance Optimization
- Use `@st.cache_data` for expensive operations
- Implement lazy loading for large datasets
- Optimize chart rendering with container width

### User Experience
- Provide clear progress feedback
- Implement graceful error handling
- Use consistent styling and layout

### Data Management
- Validate all user inputs
- Handle file upload errors gracefully
- Maintain session state consistency

---

For complete implementation details, see the [Phase 4 Implementation Guide](phase4-complete.md).
