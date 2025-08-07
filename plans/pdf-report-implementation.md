# PDF Report Generation - Phase 4 Implementation
*Professional Report Generation for LLM as a Judge System*

## Overview

This document provides the detailed implementation for PDF report generation that will be integrated into Phase 4 of the LLM as a Judge project. The system will generate professional, comprehensive reports suitable for stakeholder distribution.

## Report Types & Templates

### 1. Executive Summary Report
**Purpose**: High-level overview for executives and decision makers  
**Length**: 3-5 pages  
**Content**: Key findings, recommendations, budget impact, timeline

### 2. Detailed Evaluation Report  
**Purpose**: Comprehensive analysis for technical teams  
**Length**: 15-25 pages  
**Content**: Individual plan evaluations, detailed scoring, methodology

### 3. Comparative Analysis Report
**Purpose**: Side-by-side plan comparison  
**Length**: 8-12 pages  
**Content**: Comparison matrices, radar charts, trade-off analysis

### 4. Synthesis Recommendations Report
**Purpose**: Optimal plan recommendations  
**Length**: 6-10 pages  
**Content**: Synthesized recommendations, implementation roadmap

## Implementation Details

### Phase 4 Report Generator (`src/reports/generators/evaluation_report_generator.py`)

```python
"""
Comprehensive PDF report generator for accessibility evaluations
Integrates with Phase 4 Streamlit interface for seamless report generation
References: Master Plan - PDF Report Integration, Phase 4 - Export Interface
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime
from ..generators.base_generator import BaseReportGenerator
from ..models.report_models import (
    EvaluationReport, ReportMetadata, ReportSection, 
    PDFReportConfig, ReportType, ChartConfig
)
from ...models.evaluation_models import PlanEvaluation

class EvaluationReportGenerator(BaseReportGenerator):
    """
    Specialized report generator for accessibility evaluation reports
    Produces professional PDF reports for stakeholder distribution
    """
    
    def __init__(self, template_dir: Path = None):
        super().__init__(template_dir)
        self.report_templates = {
            ReportType.EXECUTIVE_SUMMARY: "executive_summary.html",
            ReportType.INDIVIDUAL_EVALUATION: "detailed_evaluation.html", 
            ReportType.COMPARATIVE_ANALYSIS: "comparative_analysis.html",
            ReportType.SYNTHESIS_REPORT: "synthesis_report.html"
        }
    
    def generate_report(self, evaluation_data: Dict[str, Any], 
                       report_type: ReportType,
                       config: PDFReportConfig) -> bytes:
        """Generate comprehensive PDF report from evaluation data"""
        
        # Create report structure
        report = self._create_report_structure(evaluation_data, report_type, config)
        
        # Generate charts
        if config.include_charts:
            self._add_charts_to_report(report, evaluation_data)
        
        # Render to HTML
        html_content = self._render_report_to_html(report, config)
        
        # Convert to PDF
        css_content = self._load_report_css(config)
        pdf_bytes = self._html_to_pdf(html_content, css_content)
        
        return pdf_bytes
    
    def _create_report_structure(self, evaluation_data: Dict[str, Any], 
                               report_type: ReportType,
                               config: PDFReportConfig) -> EvaluationReport:
        """Create structured report from evaluation data"""
        
        metadata = ReportMetadata(
            report_id=f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=report_type,
            audit_report_name=evaluation_data.get('audit_report_name', 'Unknown Audit'),
            plans_evaluated=list(evaluation_data.get('plans_evaluated', []))
        )
        
        if report_type == ReportType.EXECUTIVE_SUMMARY:
            return self._create_executive_summary_report(evaluation_data, metadata, config)
        elif report_type == ReportType.INDIVIDUAL_EVALUATION:
            return self._create_detailed_evaluation_report(evaluation_data, metadata, config)
        elif report_type == ReportType.COMPARATIVE_ANALYSIS:
            return self._create_comparative_analysis_report(evaluation_data, metadata, config)
        elif report_type == ReportType.SYNTHESIS_REPORT:
            return self._create_synthesis_report(evaluation_data, metadata, config)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
    
    def _create_executive_summary_report(self, data: Dict[str, Any], 
                                       metadata: ReportMetadata,
                                       config: PDFReportConfig) -> EvaluationReport:
        """Create executive summary report structure"""
        
        # Executive Summary Section
        executive_summary = ReportSection(
            title="Executive Summary",
            content=self._generate_executive_summary_content(data)
        )
        
        # Key Findings Section  
        key_findings = ReportSection(
            title="Key Findings",
            content=self._generate_key_findings_content(data)
        )
        
        # Recommendations Section
        recommendations = ReportSection(
            title="Strategic Recommendations", 
            content=self._generate_strategic_recommendations_content(data)
        )
        
        # Budget & Timeline Section
        budget_timeline = ReportSection(
            title="Budget & Timeline Impact",
            content=self._generate_budget_timeline_content(data)
        )
        
        return EvaluationReport(
            metadata=metadata,
            config=config,
            executive_summary=executive_summary,
            methodology=ReportSection(title="Methodology", content=self._get_methodology_summary()),
            individual_evaluations=[key_findings],
            comparative_analysis=recommendations,
            synthesis_recommendations=budget_timeline
        )
    
    def _create_detailed_evaluation_report(self, data: Dict[str, Any],
                                         metadata: ReportMetadata, 
                                         config: PDFReportConfig) -> EvaluationReport:
        """Create comprehensive detailed evaluation report"""
        
        # Individual plan evaluation sections
        individual_evaluations = []
        for plan_evaluation in data.get('evaluations', []):
            section = ReportSection(
                title=f"Plan {plan_evaluation.get('plan_name')} - Detailed Analysis",
                content=self._generate_individual_plan_content(plan_evaluation),
                subsections=[
                    ReportSection(
                        title="Scoring Breakdown",
                        content=self._generate_scoring_breakdown(plan_evaluation)
                    ),
                    ReportSection(
                        title="Strengths & Weaknesses",
                        content=self._generate_strengths_weaknesses(plan_evaluation)
                    ),
                    ReportSection(
                        title="Implementation Considerations", 
                        content=self._generate_implementation_considerations(plan_evaluation)
                    )
                ]
            )
            individual_evaluations.append(section)
        
        return EvaluationReport(
            metadata=metadata,
            config=config,
            executive_summary=ReportSection(
                title="Executive Summary",
                content=self._generate_detailed_executive_summary(data)
            ),
            methodology=ReportSection(
                title="Evaluation Methodology",
                content=self._generate_detailed_methodology(data)
            ),
            individual_evaluations=individual_evaluations,
            comparative_analysis=ReportSection(
                title="Cross-Plan Analysis",
                content=self._generate_cross_plan_analysis(data)
            ),
            synthesis_recommendations=ReportSection(
                title="Synthesis & Recommendations",
                content=self._generate_synthesis_content(data)
            )
        )
    
    def _create_comparative_analysis_report(self, data: Dict[str, Any],
                                          metadata: ReportMetadata,
                                          config: PDFReportConfig) -> EvaluationReport:
        """Create comparative analysis focused report"""
        
        comparative_analysis = ReportSection(
            title="Comparative Analysis",
            content=self._generate_comparative_analysis_content(data),
            subsections=[
                ReportSection(
                    title="Scoring Comparison Matrix",
                    content=self._generate_scoring_matrix(data)
                ),
                ReportSection(
                    title="Strengths & Trade-offs Analysis",
                    content=self._generate_tradeoffs_analysis(data)
                ),
                ReportSection(
                    title="Implementation Complexity Comparison",
                    content=self._generate_complexity_comparison(data)
                )
            ]
        )
        
        return EvaluationReport(
            metadata=metadata,
            config=config,
            executive_summary=ReportSection(
                title="Comparison Overview",
                content=self._generate_comparison_overview(data)
            ),
            methodology=ReportSection(
                title="Comparison Methodology", 
                content=self._get_comparison_methodology()
            ),
            individual_evaluations=[comparative_analysis],
            comparative_analysis=ReportSection(
                title="Decision Framework",
                content=self._generate_decision_framework(data)
            ),
            synthesis_recommendations=ReportSection(
                title="Selection Guidance",
                content=self._generate_selection_guidance(data)
            )
        )
    
    def _create_synthesis_report(self, data: Dict[str, Any],
                               metadata: ReportMetadata,
                               config: PDFReportConfig) -> EvaluationReport:
        """Create synthesis recommendations report"""
        
        synthesis_recommendations = ReportSection(
            title="Synthesized Optimal Plan",
            content=self._generate_optimal_plan_content(data),
            subsections=[
                ReportSection(
                    title="Combined Best Practices",
                    content=self._generate_best_practices_content(data)
                ),
                ReportSection(
                    title="Implementation Roadmap",
                    content=self._generate_implementation_roadmap(data)
                ),
                ReportSection(
                    title="Risk Mitigation Strategy",
                    content=self._generate_risk_mitigation(data)
                )
            ]
        )
        
        return EvaluationReport(
            metadata=metadata,
            config=config,
            executive_summary=ReportSection(
                title="Synthesis Overview",
                content=self._generate_synthesis_overview(data)
            ),
            methodology=ReportSection(
                title="Synthesis Methodology",
                content=self._get_synthesis_methodology()
            ),
            individual_evaluations=[synthesis_recommendations],
            comparative_analysis=ReportSection(
                title="Source Plan Analysis",
                content=self._generate_source_plan_analysis(data)
            ),
            synthesis_recommendations=ReportSection(
                title="Next Steps & Implementation",
                content=self._generate_next_steps_content(data)
            )
        )
    
    def _add_charts_to_report(self, report: EvaluationReport, data: Dict[str, Any]):
        """Add charts and visualizations to report sections"""
        
        # Radar chart for plan comparison
        radar_chart = ChartConfig(
            chart_type="radar",
            title="Plan Comparison - All Criteria",
            data=self._prepare_radar_chart_data(data),
            width=800,
            height=600
        )
        
        # Bar chart for overall scores
        bar_chart = ChartConfig(
            chart_type="bar", 
            title="Overall Plan Scores",
            data=self._prepare_bar_chart_data(data),
            width=800,
            height=400
        )
        
        # Add charts to appropriate sections
        if report.comparative_analysis:
            report.comparative_analysis.charts.extend([radar_chart, bar_chart])
        
        # Criterion-specific charts
        for section in report.individual_evaluations:
            if "detailed analysis" in section.title.lower():
                criterion_chart = ChartConfig(
                    chart_type="bar",
                    title=f"Detailed Scores - {section.title.split(' -')[0]}",
                    data=self._prepare_individual_chart_data(data, section.title),
                    width=600,
                    height=300
                )
                section.charts.append(criterion_chart)
    
    def _render_report_to_html(self, report: EvaluationReport, 
                             config: PDFReportConfig) -> str:
        """Render complete report to HTML"""
        
        # Generate report content HTML
        report_content = self._render_report_sections(report)
        
        # Render main template
        template_name = self.report_templates.get(
            report.metadata.report_type, 
            "evaluation_report.html"
        )
        
        context = {
            'metadata': report.metadata,
            'config': config,
            'report_content': report_content,
            'generated_charts': self._render_charts_html(report)
        }
        
        return self._render_template(template_name, context)
    
    def _render_report_sections(self, report: EvaluationReport) -> str:
        """Render all report sections to HTML"""
        sections_html = []
        
        # Executive Summary
        sections_html.append(self._render_section_html(report.executive_summary))
        
        # Methodology  
        sections_html.append(self._render_section_html(report.methodology))
        
        # Individual Evaluations
        for section in report.individual_evaluations:
            sections_html.append(self._render_section_html(section))
        
        # Comparative Analysis
        sections_html.append(self._render_section_html(report.comparative_analysis))
        
        # Synthesis Recommendations
        sections_html.append(self._render_section_html(report.synthesis_recommendations))
        
        return '\n'.join(sections_html)
    
    def _render_section_html(self, section: ReportSection) -> str:
        """Render individual section to HTML"""
        html = f'<div class="section">\n<h1>{section.title}</h1>\n'
        html += f'<div class="content">{section.content}</div>\n'
        
        # Add charts
        for chart in section.charts:
            chart_img = self._generate_chart(chart.dict())
            html += f'''
            <div class="chart-container">
                <h3>{chart.title}</h3>
                <img src="{chart_img}" alt="{chart.title}" />
            </div>
            '''
        
        # Add subsections
        for subsection in section.subsections:
            html += f'<div class="subsection">\n<h2>{subsection.title}</h2>\n'
            html += f'<div class="content">{subsection.content}</div>\n</div>\n'
        
        html += '</div>\n'
        return html
    
    def _load_report_css(self, config: PDFReportConfig) -> str:
        """Load CSS styles for report"""
        css_file = self.template_dir / "css" / "report_styles.css"
        if css_file.exists():
            return css_file.read_text()
        return ""
    
    # Content generation methods
    def _generate_executive_summary_content(self, data: Dict[str, Any]) -> str:
        """Generate executive summary content"""
        evaluations = data.get('evaluations', [])
        best_plan = max(evaluations, key=lambda x: x.get('overall_score', 0))
        
        return f"""
        <p>This report presents the evaluation results of {len(evaluations)} accessibility 
        remediation plans for {data.get('audit_report_name', 'the audited system')}.</p>
        
        <p><strong>Key Finding:</strong> {best_plan.get('plan_name')} scored highest 
        with an overall score of {best_plan.get('overall_score', 0):.1f}/10.</p>
        
        <p>The evaluation utilized a comprehensive framework assessing strategic 
        prioritization, technical specificity, comprehensiveness, and long-term vision.</p>
        
        <div class="highlight-box">
        <h3>Immediate Action Required</h3>
        <p>Based on the analysis, we recommend proceeding with implementation planning 
        for the top-ranked remediation approach while incorporating best practices 
        identified across all evaluated plans.</p>
        </div>
        """
    
    # Additional content generation methods would be implemented here...
    # _generate_key_findings_content, _generate_strategic_recommendations_content, etc.

    def _prepare_radar_chart_data(self, data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Prepare data for radar chart visualization"""
        chart_data = {}
        
        for evaluation in data.get('evaluations', []):
            plan_name = evaluation.get('plan_name')
            scores = evaluation.get('scores', {})
            
            chart_data[plan_name] = {
                'Strategic Prioritization': scores.get('strategic_prioritization', 0),
                'Technical Specificity': scores.get('technical_specificity', 0), 
                'Comprehensiveness': scores.get('comprehensiveness', 0),
                'Long-term Vision': scores.get('long_term_vision', 0)
            }
        
        return chart_data
    
    def _prepare_bar_chart_data(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Prepare data for bar chart visualization"""
        chart_data = {}
        
        for evaluation in data.get('evaluations', []):
            plan_name = evaluation.get('plan_name')
            overall_score = evaluation.get('overall_score', 0)
            chart_data[plan_name] = overall_score
        
        return chart_data
```

## Integration with Streamlit Interface

### Updated Phase 4 Navigation
The Phase 4 Streamlit interface now includes a dedicated "Reports" tab:

```python
# Enhanced tab navigation in main.py
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📤 Upload & Configure", 
    "🔄 Run Evaluation", 
    "📊 Results Dashboard",
    "📋 Generate Reports",  # New dedicated reports tab
    "💾 Export & Archive"
])

with tab4:  # Reports tab
    self._render_report_generation_interface()
```

### Report Generation Interface
```python
def _render_report_generation_interface(self):
    """Dedicated interface for report generation"""
    st.header("📋 Professional Report Generation")
    
    if not st.session_state.evaluation_results:
        st.warning("No evaluation results available. Run an evaluation first.")
        return
    
    # Report type selection with previews
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Select Report Type")
        
        report_options = [
            {
                "name": "Executive Summary",
                "type": ReportType.EXECUTIVE_SUMMARY,
                "description": "High-level overview for decision makers",
                "pages": "3-5 pages",
                "audience": "Executives, Project Sponsors"
            },
            {
                "name": "Detailed Evaluation", 
                "type": ReportType.INDIVIDUAL_EVALUATION,
                "description": "Comprehensive technical analysis",
                "pages": "15-25 pages", 
                "audience": "Development Teams, Technical Leads"
            },
            {
                "name": "Comparative Analysis",
                "type": ReportType.COMPARATIVE_ANALYSIS, 
                "description": "Side-by-side plan comparison",
                "pages": "8-12 pages",
                "audience": "Product Managers, Architects"
            },
            {
                "name": "Synthesis Report",
                "type": ReportType.SYNTHESIS_REPORT,
                "description": "Optimal plan recommendations", 
                "pages": "6-10 pages",
                "audience": "Implementation Teams"
            }
        ]
        
        selected_report = st.selectbox(
            "Report Type",
            report_options,
            format_func=lambda x: x["name"]
        )
    
    with col2:
        st.subheader("Report Preview")
        st.info(f"""
        **{selected_report['name']}**
        
        {selected_report['description']}
        
        📄 **Length:** {selected_report['pages']}  
        👥 **Target Audience:** {selected_report['audience']}
        """)
    
    # Report configuration and generation
    self._render_report_configuration(selected_report)
```

## Quality Gates for PDF Reports

### Phase 4 PDF Report Completion Criteria
- [ ] **Report Generation**: All 4 report types generate successfully
- [ ] **Professional Format**: Reports meet professional standards
- [ ] **Chart Integration**: Charts render correctly in PDF format
- [ ] **Template System**: Flexible template system working
- [ ] **Download Interface**: Seamless download experience
- [ ] **Batch Generation**: Multiple report types in one package
- [ ] **Performance**: Reports generate within acceptable time limits

### Report Quality Standards
- **Visual Design**: Professional layout with consistent styling
- **Content Quality**: Clear, actionable content with proper structure
- **Chart Quality**: High-resolution charts with proper labeling
- **Accessibility**: Reports themselves follow accessibility standards
- **File Size**: Optimized file sizes for easy distribution
- **Cross-platform**: PDFs render consistently across devices

This comprehensive PDF report generation system transforms the LLM as a Judge project from a technical evaluation tool into a complete professional solution suitable for enterprise use and stakeholder communication.
