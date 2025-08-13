# Phase 4: User Interface Development
*Week 4 Implementation Plan*

**← [Phase 3: Workflow](./phase-3-workflow.md)** | **[Phase 5: Optimization →](./phase-5-optimization.md)**

## Overview

Phase 4 creates the user interface for the LLM as a Judge system using Streamlit. This phase focuses on building an intuitive web application that allows users to upload audit reports and remediation plans, monitor evaluation progress in real-time, and view comprehensive **scoring results**, **comparative analysis**, and **evaluation reports**.

## Prerequisites

- [x] **Phase 3 Complete**: Full evaluation workflow orchestration functional
- [x] **End-to-End Testing**: Complete scoring and evaluation pipeline working
- [x] **Output Validation**: All agent scoring outputs properly structured
- [x] **Error Handling**: Robust error recovery mechanisms in place

## Objectives

- [x] **Streamlit Web Application**: Complete user interface for evaluation system interaction
- [x] **Upload Interface**: File handling for audit reports and remediation plans
- [x] **Progress Monitoring**: Real-time evaluation progress and status updates
- [x] **Scoring Dashboard**: Interactive visualization of plan scores and rankings
- [x] **PDF Report Generation**: Professional, downloadable evaluation and comparison reports
- [x] **Export Functionality**: Multiple export formats for scores, comparisons, and analysis
- [x] **UI Documentation**: Component examples, user guides, and API endpoint documentation

## Deliverables

### 4.1 Main Application Interface

#### Core Streamlit Application (`app/main.py`)
```python
"""
Main Streamlit application for LLM as a Judge system
References: Master Plan - User Interface, Phase 3 - Workflow Integration
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import asyncio
import json
from typing import Dict, List, Optional

# Import our core system components
from src.config.crew_config import AccessibilityEvaluationCrew
from src.config.llm_config import LLMManager, LLMConfig
from src.tools.pdf_parser import PDFParser
from src.models.evaluation_models import EvaluationInput, DocumentContent
from src.utils.workflow_controller import WorkflowController
from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator
from src.models.report_models import PDFReportConfig, ReportType

# Page configuration
st.set_page_config(
    page_title="LLM as a Judge - Accessibility Evaluator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AccessibilityEvaluatorApp:
    """
    Main application class for the Streamlit interface
    Coordinates all UI components and system interactions
    """
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.report_generator = EvaluationReportGenerator()
        self.llm_manager = None
        self.crew = None
        self.workflow_controller = None
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'system_configured' not in st.session_state:
            st.session_state.system_configured = False
        if 'evaluation_input' not in st.session_state:
            st.session_state.evaluation_input = None
        if 'evaluation_results' not in st.session_state:
            st.session_state.evaluation_results = None
        if 'workflow_status' not in st.session_state:
            st.session_state.workflow_status = None
    
    def run(self):
        """Main application entry point"""
        st.title("⚖️ LLM as a Judge - Accessibility Remediation Plan Evaluator")
        st.markdown("""
        This system uses Gemini Pro and GPT-4 as expert judges to evaluate accessibility 
        remediation plans and synthesize an optimal solution.
        """)
        
        # Sidebar for navigation and configuration
        self._render_sidebar()
        
        # Main content area
        if not st.session_state.system_configured:
            self._render_configuration_page()
        else:
            # Navigation tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📤 Upload & Configure", 
                "🔄 Run Evaluation", 
                "📊 Results Dashboard", 
                "📋 Export & Reports"
            ])
            
            with tab1:
                self._render_upload_interface()
            
            with tab2:
                self._render_evaluation_interface()
            
            with tab3:
                self._render_results_dashboard()
            
            with tab4:
                self._render_export_interface()
    
    def _render_sidebar(self):
        """Render sidebar with system status and configuration"""
        with st.sidebar:
            st.header("🔧 System Configuration")
            
            # API Configuration Status
            st.subheader("API Status")
            if st.session_state.system_configured and self.llm_manager:
                status = self.llm_manager.test_connections()
                
                col1, col2 = st.columns(2)
                with col1:
                    if status.get('gemini', False):
                        st.success("✅ Gemini Pro")
                    else:
                        st.error("❌ Gemini Pro")
                
                with col2:
                    if status.get('openai', False):
                        st.success("✅ GPT-4")
                    else:
                        st.error("❌ GPT-4")
            else:
                st.warning("⚠️ APIs not configured")
            
            # Workflow Status
            st.subheader("Workflow Status")
            if self.workflow_controller and st.session_state.workflow_status:
                status = st.session_state.workflow_status
                
                # Progress bar
                progress = status.get('progress', 0)
                st.progress(progress / 100)
                
                # Current phase
                phase = status.get('phase', 'idle')
                st.info(f"Phase: {phase.replace('_', ' ').title()}")
                
                # Status indicator
                status_text = status.get('status', 'idle')
                if status_text == 'running':
                    st.warning("🔄 Running")
                elif status_text == 'completed':
                    st.success("✅ Completed")
                elif status_text == 'failed':
                    st.error("❌ Failed")
                else:
                    st.info("💤 Idle")
            else:
                st.info("💤 System Idle")
            
            # System Information
            st.subheader("System Info")
            st.info(f"""
            **Evaluation Framework:** promt/eval-prompt.md
            **Criteria Weights:**
            • Strategic Prioritization: 40%
            • Technical Specificity: 30%
            • Comprehensiveness: 20%
            • Long-term Vision: 10%
            """)
    
    def _render_configuration_page(self):
        """Render system configuration interface"""
        st.header("🚀 System Configuration")
        
        st.markdown("""
        Configure your API keys to enable the LLM judges. Both Gemini Pro and GPT-4 
        are required for the dual-judge evaluation system.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🤖 Gemini Pro Configuration")
            gemini_key = st.text_input(
                "Google API Key", 
                type="password",
                placeholder="Enter your Google AI Studio API key",
                help="Get your API key from Google AI Studio: https://makersuite.google.com/app/apikey"
            )
        
        with col2:
            st.subheader("🧠 GPT-4 Configuration")
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password", 
                placeholder="Enter your OpenAI API key",
                help="Get your API key from OpenAI: https://platform.openai.com/api-keys"
            )
        
        # Configuration button
        if st.button("🔧 Configure System", type="primary"):
            if gemini_key and openai_key:
                try:
                    # Initialize LLM manager
                    config = LLMConfig(
                        gemini_api_key=gemini_key,
                        openai_api_key=openai_key
                    )
                    self.llm_manager = LLMManager(config)
                    
                    # Test connections
                    with st.spinner("Testing API connections..."):
                        status = self.llm_manager.test_connections()
                    
                    if all(status.values()):
                        # Initialize crew and workflow controller
                        self.crew = AccessibilityEvaluationCrew(self.llm_manager)
                        self.workflow_controller = WorkflowController(self.crew)
                        
                        st.session_state.system_configured = True
                        st.success("✅ System configured successfully!")
                        st.rerun()
                    else:
                        failed_apis = [api for api, success in status.items() if not success]
                        st.error(f"❌ Failed to connect to: {', '.join(failed_apis)}")
                        
                except Exception as e:
                    st.error(f"❌ Configuration failed: {str(e)}")
            else:
                st.warning("⚠️ Please provide both API keys")
    
    def _render_upload_interface(self):
        """Render file upload and configuration interface"""
        st.header("📤 Upload Audit Report and Remediation Plans")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 Accessibility Audit Report")
            audit_file = st.file_uploader(
                "Upload audit report (PDF)",
                type=['pdf'],
                help="Upload the original accessibility audit report that identifies issues to be remediated"
            )
            
            if audit_file:
                with st.spinner("Parsing audit report..."):
                    # Save uploaded file temporarily
                    temp_path = Path(f"temp_{audit_file.name}")
                    with open(temp_path, "wb") as f:
                        f.write(audit_file.read())
                    
                    try:
                        audit_content = self.pdf_parser.parse_audit_report(temp_path)
                        st.success(f"✅ Audit report parsed: {audit_content.page_count} pages")
                        
                        # Preview
                        with st.expander("📄 Preview Audit Content"):
                            st.text_area("Content Preview", audit_content.content[:1000] + "...", height=200)
                        
                        # Store in session state
                        st.session_state.audit_content = audit_content
                        
                    except Exception as e:
                        st.error(f"❌ Failed to parse audit report: {str(e)}")
                    finally:
                        temp_path.unlink(missing_ok=True)
        
        with col2:
            st.subheader("📑 Remediation Plans")
            plan_files = st.file_uploader(
                "Upload remediation plans (PDFs)",
                type=['pdf'],
                accept_multiple_files=True,
                help="Upload all remediation plans to be evaluated (Plans A, B, C, etc.)"
            )
            
            if plan_files:
                parsed_plans = {}
                
                for plan_file in plan_files:
                    with st.spinner(f"Parsing {plan_file.name}..."):
                        temp_path = Path(f"temp_{plan_file.name}")
                        with open(temp_path, "wb") as f:
                            f.write(plan_file.read())
                        
                        try:
                            plan_content = self.pdf_parser.parse_remediation_plan(temp_path)
                            plan_name = plan_file.name.replace('.pdf', '')
                            parsed_plans[plan_name] = plan_content
                            
                            st.success(f"✅ {plan_name}: {plan_content.page_count} pages")
                            
                        except Exception as e:
                            st.error(f"❌ Failed to parse {plan_file.name}: {str(e)}")
                        finally:
                            temp_path.unlink(missing_ok=True)
                
                if parsed_plans:
                    st.session_state.remediation_plans = parsed_plans
                    
                    # Summary
                    st.info(f"📊 Total plans loaded: {len(parsed_plans)}")
                    
                    # Plan list
                    with st.expander("📋 Loaded Plans"):
                        for name, content in parsed_plans.items():
                            st.write(f"• **{name}**: {content.page_count} pages")
        
        # Evaluation configuration
        if hasattr(st.session_state, 'audit_content') and hasattr(st.session_state, 'remediation_plans'):
            st.divider()
            st.subheader("⚙️ Evaluation Configuration")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                execution_mode = st.selectbox(
                    "Execution Mode",
                    ["sequential", "parallel"],
                    help="Sequential: Phases run one after another. Parallel: Maximum concurrency for speed."
                )
                
                include_consensus = st.checkbox(
                    "Enable Consensus Building",
                    value=True,
                    help="Automatically resolve disagreements between judges"
                )
            
            with col2:
                if st.button("✅ Prepare Evaluation", type="primary"):
                    # Create evaluation input
                    evaluation_input = EvaluationInput(
                        audit_report=st.session_state.audit_content,
                        remediation_plans=st.session_state.remediation_plans
                    )
                    
                    st.session_state.evaluation_input = evaluation_input
                    st.session_state.execution_mode = execution_mode
                    st.session_state.include_consensus = include_consensus
                    
                    st.success("✅ Evaluation prepared! Go to 'Run Evaluation' tab.")
    
    def _render_evaluation_interface(self):
        """Render evaluation execution interface"""
        st.header("🔄 Run Evaluation")
        
        if not hasattr(st.session_state, 'evaluation_input') or not st.session_state.evaluation_input:
            st.warning("⚠️ Please upload and configure files in the 'Upload & Configure' tab first.")
            return
        
        evaluation_input = st.session_state.evaluation_input
        
        # Evaluation summary
        st.subheader("📋 Evaluation Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Audit Report", "1 document", f"{evaluation_input.audit_report.page_count} pages")
        
        with col2:
            plan_count = len(evaluation_input.remediation_plans)
            total_pages = sum(plan.page_count for plan in evaluation_input.remediation_plans.values())
            st.metric("Remediation Plans", f"{plan_count} documents", f"{total_pages} pages")
        
        with col3:
            estimated_time = self._estimate_evaluation_time(evaluation_input)
            st.metric("Estimated Time", estimated_time, "minutes")
        
        # Execution controls
        st.divider()
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🚀 Start Evaluation", type="primary", disabled=st.session_state.workflow_status and st.session_state.workflow_status.get('status') == 'running'):
                self._start_evaluation()
        
        with col2:
            if st.button("⏹️ Stop Evaluation"):
                self._stop_evaluation()
        
        with col3:
            if st.button("🔄 Refresh Status"):
                self._refresh_status()
        
        # Progress monitoring
        if st.session_state.workflow_status:
            self._render_progress_monitor()
    
    def _render_progress_monitor(self):
        """Render real-time progress monitoring"""
        st.subheader("📈 Evaluation Progress")
        
        status = st.session_state.workflow_status
        
        # Main progress bar
        progress = status.get('progress', 0)
        st.progress(progress / 100, f"Overall Progress: {progress}%")
        
        # Phase information
        phase = status.get('phase', 'idle')
        st.info(f"**Current Phase:** {phase.replace('_', ' ').title()}")
        
        # Detailed status
        with st.expander("🔍 Detailed Status", expanded=True):
            status_text = status.get('status', 'idle')
            
            if status_text == 'running':
                st.success("🔄 Evaluation in progress...")
                
                # Phase breakdown
                phases = [
                    ("Initialization", 10),
                    ("Individual Evaluations", 40),
                    ("Cross-Plan Comparison", 60),
                    ("Consensus Building", 75),
                    ("Plan Synthesis", 90),
                    ("Final Compilation", 100)
                ]
                
                for phase_name, phase_progress in phases:
                    if progress >= phase_progress:
                        st.success(f"✅ {phase_name}")
                    elif progress >= phase_progress - 15:
                        st.warning(f"🔄 {phase_name}")
                    else:
                        st.info(f"⏳ {phase_name}")
            
            elif status_text == 'completed':
                st.success("✅ Evaluation completed successfully!")
                if st.button("📊 View Results"):
                    # Switch to results tab (would need tab state management)
                    pass
            
            elif status_text == 'failed':
                st.error(f"❌ Evaluation failed: {status.get('error', 'Unknown error')}")
                if st.button("🔄 Retry Evaluation"):
                    self._retry_evaluation()
    
    def _render_results_dashboard(self):
        """Render comprehensive results dashboard"""
        st.header("📊 Evaluation Results Dashboard")
        
        if not st.session_state.evaluation_results:
            st.info("🔍 No evaluation results available. Run an evaluation first.")
            return
        
        results = st.session_state.evaluation_results
        
        # Results tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Score Overview", 
            "🔍 Detailed Analysis", 
            "⚖️ Judge Comparison",
            "🎯 Synthesis Plan"
        ])
        
        with tab1:
            self._render_score_overview(results)
        
        with tab2:
            self._render_detailed_analysis(results)
        
        with tab3:
            self._render_judge_comparison(results)
        
        with tab4:
            self._render_synthesis_plan(results)
    
    def _render_score_overview(self, results):
        """Render scoring overview dashboard"""
        st.subheader("📈 Overall Scoring Results")
        
        # Score summary table
        score_data = self._extract_score_data(results)
        df = pd.DataFrame(score_data)
        
        # Overall scores chart
        fig = px.bar(
            df, 
            x='Plan', 
            y='Overall Score',
            color='Overall Score',
            color_continuous_scale='RdYlGn',
            title="Overall Plan Scores"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Criteria breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            # Radar chart for top plans
            top_plans = df.nlargest(3, 'Overall Score')
            self._render_radar_chart(top_plans)
        
        with col2:
            # Score distribution
            fig = px.histogram(
                df,
                x='Overall Score',
                nbins=10,
                title="Score Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Rankings table
        st.subheader("🏆 Plan Rankings")
        ranking_df = df.sort_values('Overall Score', ascending=False).reset_index(drop=True)
        ranking_df.index += 1
        st.dataframe(ranking_df, use_container_width=True)
    
    def _render_radar_chart(self, plans_df):
        """Render radar chart for plan comparison"""
        fig = go.Figure()
        
        criteria = ['Strategic Prioritization', 'Technical Specificity', 'Comprehensiveness', 'Long-term Vision']
        
        for _, plan in plans_df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[plan[criterion] for criterion in criteria],
                theta=criteria,
                fill='toself',
                name=plan['Plan']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=True,
            title="Top Plans - Criteria Comparison"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_detailed_analysis(self, results):
        """Render detailed analysis for each plan"""
        st.subheader("🔍 Detailed Plan Analysis")
        
        # Plan selector
        plans = list(results.plan_scores.keys()) if hasattr(results, 'plan_scores') else []
        selected_plan = st.selectbox("Select Plan for Detailed Analysis", plans)
        
        if selected_plan:
            plan_analysis = results.detailed_analysis.get(selected_plan)
            
            if plan_analysis:
                # Score breakdown
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.metric("Overall Score", f"{plan_analysis.overall_score}/10")
                    
                    # Criteria scores
                    for score in plan_analysis.scores:
                        st.metric(score.criterion, f"{score.score}/10")
                
                with col2:
                    # Detailed analysis text
                    st.text_area(
                        "Detailed Analysis",
                        plan_analysis.detailed_analysis,
                        height=200
                    )
                
                # Pros and Cons
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ Strengths")
                    for pro in plan_analysis.pros:
                        st.success(f"• {pro}")
                
                with col2:
                    st.subheader("❌ Weaknesses") 
                    for con in plan_analysis.cons:
                        st.error(f"• {con}")
    
    def _render_export_interface(self):
        """Render export and reporting interface"""
        st.header("📋 Export Reports & Data")
        
        if not hasattr(st.session_state, 'evaluation_results') or not st.session_state.evaluation_results:
            st.warning("⚠️ No evaluation results available. Please run an evaluation first.")
            return
        
        results = st.session_state.evaluation_results
        
        # Report Type Selection
        st.subheader("📄 PDF Report Generation")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            report_type = st.selectbox(
                "Select Report Type",
                [
                    ("Executive Summary", ReportType.EXECUTIVE_SUMMARY),
                    ("Detailed Evaluation Report", ReportType.INDIVIDUAL_EVALUATION),
                    ("Comparative Analysis", ReportType.COMPARATIVE_ANALYSIS),
                    ("Synthesis Recommendations", ReportType.SYNTHESIS_REPORT)
                ],
                format_func=lambda x: x[0]
            )
        
        with col2:
            st.metric("Report Size", "~15-25 pages", "Estimated")
        
        # Report Configuration
        with st.expander("🔧 Report Configuration", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                include_charts = st.checkbox("Include Charts & Visualizations", value=True)
                include_raw_data = st.checkbox("Include Raw Evaluation Data", value=False)
                include_cover_page = st.checkbox("Include Cover Page", value=True)
                
            with col2:
                page_size = st.selectbox("Page Size", ["A4", "Letter", "Legal"], index=0)
                font_family = st.selectbox("Font Family", ["Arial", "Times New Roman", "Calibri"], index=0)
                include_toc = st.checkbox("Include Table of Contents", value=True)
        
        # Generate Report Button
        if st.button("🔄 Generate PDF Report", type="primary"):
            with st.spinner("Generating comprehensive PDF report..."):
                try:
                    # Configure report generation
                    config = PDFReportConfig(
                        template_name="evaluation_report.html",
                        include_charts=include_charts,
                        include_raw_data=include_raw_data,
                        page_size=page_size,
                        font_family=font_family,
                        include_cover_page=include_cover_page,
                        include_table_of_contents=include_toc
                    )
                    
                    # Generate PDF
                    pdf_bytes = self.report_generator.generate_report(
                        evaluation_data=results,
                        report_type=report_type[1],
                        config=config
                    )
                    
                    # Create download button
                    report_filename = f"accessibility_evaluation_report_{report_type[1].value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    
                    st.success("✅ PDF Report Generated Successfully!")
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=report_filename,
                        mime="application/pdf",
                        key="download_pdf_report"
                    )
                    
                    # Show report preview info
                    st.info(f"""
                    **Report Details:**
                    - Type: {report_type[0]}
                    - Pages: ~{self._estimate_report_pages(results, config)} pages
                    - File Size: ~{len(pdf_bytes) / 1024:.1f} KB
                    - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Error generating PDF report: {str(e)}")
                    st.info("Please check your evaluation results and try again.")
        
        st.divider()
        
        # Additional Export Options
        st.subheader("📊 Additional Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📈 Export Charts as Images"):
                self._export_charts_as_images(results)
        
        with col2:
            if st.button("📑 Export Data as JSON"):
                self._export_data_as_json(results)
        
        with col3:
            if st.button("📋 Export Summary as CSV"):
                self._export_summary_as_csv(results)
        
        # Batch Report Generation
        if len(results.get('evaluations', [])) > 1:
            st.divider()
            st.subheader("🔄 Batch Report Generation")
            
            if st.button("📚 Generate Complete Report Package"):
                with st.spinner("Generating complete report package..."):
                    self._generate_complete_report_package(results)
    
    def _export_charts_as_images(self, results):
        """Export all charts as individual image files"""
        try:
            # Generate charts and create ZIP file
            import zipfile
            from io import BytesIO
            
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                # Generate radar chart
                radar_chart = self._create_radar_chart_data(results)
                if radar_chart:
                    zip_file.writestr("radar_comparison.png", radar_chart)
                
                # Generate bar charts
                bar_charts = self._create_bar_chart_data(results)
                for i, chart in enumerate(bar_charts):
                    zip_file.writestr(f"scores_chart_{i+1}.png", chart)
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="📥 Download Charts Package",
                data=zip_buffer.getvalue(),
                file_name=f"evaluation_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )
            
            st.success("✅ Charts package ready for download!")
            
        except Exception as e:
            st.error(f"❌ Error exporting charts: {str(e)}")
    
    def _export_data_as_json(self, results):
        """Export evaluation data as JSON"""
        try:
            import json
            
            # Prepare data for export
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "export_type": "evaluation_data",
                    "version": "1.0"
                },
                "evaluation_results": results
            }
            
            json_data = json.dumps(export_data, indent=2, default=str)
            
            st.download_button(
                label="📥 Download JSON Data",
                data=json_data,
                file_name=f"evaluation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            st.success("✅ JSON data ready for download!")
            
        except Exception as e:
            st.error(f"❌ Error exporting JSON: {str(e)}")
    
    def _export_summary_as_csv(self, results):
        """Export evaluation summary as CSV"""
        try:
            import pandas as pd
            
            # Create summary DataFrame
            summary_data = []
            for evaluation in results.get('evaluations', []):
                summary_data.append({
                    'Plan Name': evaluation.get('plan_name'),
                    'Overall Score': evaluation.get('overall_score'),
                    'Strategic Prioritization': evaluation.get('scores', {}).get('strategic_prioritization'),
                    'Technical Specificity': evaluation.get('scores', {}).get('technical_specificity'),
                    'Comprehensiveness': evaluation.get('scores', {}).get('comprehensiveness'),
                    'Long-term Vision': evaluation.get('scores', {}).get('long_term_vision'),
                    'Judge': evaluation.get('judge_id')
                })
            
            df = pd.DataFrame(summary_data)
            csv_data = df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV Summary",
                data=csv_data,
                file_name=f"evaluation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            st.success("✅ CSV summary ready for download!")
            
        except Exception as e:
            st.error(f"❌ Error exporting CSV: {str(e)}")
    
    def _generate_complete_report_package(self, results):
        """Generate complete package with all report types"""
        try:
            import zipfile
            from io import BytesIO
            
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                # Generate all report types
                report_types = [
                    (ReportType.EXECUTIVE_SUMMARY, "executive_summary.pdf"),
                    (ReportType.INDIVIDUAL_EVALUATION, "detailed_evaluation.pdf"),
                    (ReportType.COMPARATIVE_ANALYSIS, "comparative_analysis.pdf"),
                    (ReportType.SYNTHESIS_REPORT, "synthesis_recommendations.pdf")
                ]
                
                for report_type, filename in report_types:
                    config = PDFReportConfig(
                        template_name="evaluation_report.html",
                        include_charts=True,
                        include_cover_page=True,
                        include_table_of_contents=True
                    )
                    
                    pdf_bytes = self.report_generator.generate_report(
                        evaluation_data=results,
                        report_type=report_type,
                        config=config
                    )
                    
                    zip_file.writestr(filename, pdf_bytes)
                
                # Add data exports
                json_data = json.dumps(results, indent=2, default=str)
                zip_file.writestr("evaluation_data.json", json_data)
                
                # Add charts
                charts = self._create_all_charts(results)
                for chart_name, chart_data in charts.items():
                    zip_file.writestr(f"charts/{chart_name}.png", chart_data)
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="📥 Download Complete Report Package",
                data=zip_buffer.getvalue(),
                file_name=f"complete_evaluation_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )
            
            st.success("✅ Complete report package ready for download!")
            
        except Exception as e:
            st.error(f"❌ Error generating complete package: {str(e)}")
    
    def _estimate_report_pages(self, results, config):
        """Estimate number of pages in generated report"""
        base_pages = 8  # Cover, TOC, Executive Summary, etc.
        plans_count = len(results.get('evaluations', []))
        
        if config.include_charts:
            base_pages += 3  # Chart pages
        if config.include_raw_data:
            base_pages += plans_count * 2  # Raw data pages
        
        return base_pages + plans_count * 2  # Individual evaluation pages
        st.header("📋 Export & Reports")
        
        if not st.session_state.evaluation_results:
            st.info("🔍 No evaluation results available for export.")
            return
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Data Export")
            
            # CSV export
            if st.button("📥 Export Scores (CSV)"):
                csv_data = self._generate_csv_export()
                st.download_button(
                    "Download CSV",
                    csv_data,
                    "evaluation_scores.csv",
                    "text/csv"
                )
            
            # JSON export
            if st.button("📥 Export Full Results (JSON)"):
                json_data = self._generate_json_export()
                st.download_button(
                    "Download JSON",
                    json_data,
                    "evaluation_results.json",
                    "application/json"
                )
        
        with col2:
            st.subheader("📄 Report Generation")
            
            # Executive summary
            if st.button("📋 Generate Executive Summary"):
                summary = self._generate_executive_summary()
                st.download_button(
                    "Download Summary",
                    summary,
                    "executive_summary.md",
                    "text/markdown"
                )
            
            # Comprehensive report
            if st.button("📚 Generate Full Report"):
                report = self._generate_comprehensive_report()
                st.download_button(
                    "Download Report",
                    report,
                    "comprehensive_evaluation_report.md",
                    "text/markdown"
                )
    
    # Helper methods
    def _start_evaluation(self):
        """Start the evaluation workflow"""
        try:
            # This would typically be async, but Streamlit handles it
            with st.spinner("Starting evaluation workflow..."):
                # In a real implementation, this would be async
                # For now, we'll simulate the start
                st.session_state.workflow_status = {
                    'status': 'running',
                    'phase': 'initialization',
                    'progress': 5
                }
                st.success("✅ Evaluation started!")
                st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to start evaluation: {str(e)}")
    
    def _estimate_evaluation_time(self, evaluation_input) -> str:
        """Estimate evaluation time based on input size"""
        plan_count = len(evaluation_input.remediation_plans)
        total_pages = sum(plan.page_count for plan in evaluation_input.remediation_plans.values())
        
        # Rough estimation: 2 minutes per plan + 1 minute per 5 pages
        estimated_minutes = (plan_count * 2) + (total_pages // 5) + 5
        
        return f"{estimated_minutes}-{estimated_minutes + 5}"
    
    def _extract_score_data(self, results):
        """Extract scoring data for visualization"""
        # This would extract real data from results
        # For now, return mock data structure
        return [
            {
                'Plan': 'Plan A',
                'Overall Score': 8.5,
                'Strategic Prioritization': 9.0,
                'Technical Specificity': 8.2,
                'Comprehensiveness': 8.5,
                'Long-term Vision': 8.0
            }
            # ... more plans
        ]

# Application entry point
def main():
    """Main application entry point"""
    app = AccessibilityEvaluatorApp()
    app.run()

if __name__ == "__main__":
    main()
```

## Quality Gates

### Phase 4 Completion Criteria
- [ ] **Streamlit Application**: Complete web interface functional
- [ ] **File Upload**: PDF parsing and validation working
- [ ] **Progress Monitoring**: Real-time workflow status updates
- [ ] **Results Dashboard**: Interactive visualization of all results
- [ ] **PDF Report Generation**: All 4 report types generating successfully
- [ ] **Professional Reports**: Reports meet enterprise quality standards
- [ ] **Export Functionality**: Multiple format exports working
- [ ] **Download Interface**: Seamless report download experience
- [ ] **Error Handling**: Graceful handling of UI and workflow errors

### Enhanced Quality Gates

**Note**: Quality gates focused on local development and usage. Production security and infrastructure features removed as this application will only run locally.

#### 📊 User Experience & Performance
- [ ] **Cross-Browser Compatibility**: Works in Chrome, Firefox, Safari, Edge
- [ ] **Performance Testing**: UI loads and responds quickly under normal load
- [ ] **Accessibility Compliance**: Interface meets WCAG 2.1 AA standards

#### 🔧 Error Handling & Support
- [ ] **User-Friendly Errors**: Error messages clear and actionable
- [ ] **Help System**: Comprehensive help and documentation integrated
- [ ] **Debug Information**: Appropriate debug info available for troubleshooting

#### 🎯 Report Quality & Distribution
- [ ] **Report Consistency**: All reports generate with consistent formatting
- [ ] **Chart Quality**: High-resolution charts with proper labeling
- [ ] **File Optimization**: PDF file sizes optimized for local use
- [ ] **Batch Operations**: Multiple reports generate efficiently

### PDF Report Quality Gates
- [ ] **Report Types**: Executive Summary, Detailed, Comparative, Synthesis reports
- [ ] **Professional Layout**: Consistent styling, proper formatting, cover pages
- [ ] **Chart Integration**: High-quality charts embedded in PDFs
- [ ] **Template System**: Flexible, maintainable template architecture  
- [ ] **Performance**: Reports generate within 30 seconds
- [ ] **File Optimization**: PDF file sizes under 5MB for easy local storage
- [ ] **Batch Generation**: Complete report packages with all types

### User Experience Testing
- [ ] **Intuitive Navigation**: Clear user flow through all features
- [ ] **Performance**: Fast loading and responsive interactions
- [ ] **Error Messages**: Clear, actionable error communication
- [ ] **Help Documentation**: Adequate guidance for users

## Next Steps

Upon successful completion of Phase 4:
1. **Local application is fully functional and ready for use**
2. **All features optimized for local development environment**
3. **Application ready for accessibility remediation plan evaluation**

---

**← [Phase 3: Workflow](./phase-3-workflow.md)** | **Phase 5 removed (production-only features)**
