"""
Main Streamlit application for LLM as a Judge system
Phase 4 Implementation - Core UI functionality
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our core system components
from src.config.crew_config import AccessibilityEvaluationCrew  # noqa: E402
from src.config.llm_config import LLMConfig, LLMManager  # noqa: E402
from src.models.evaluation_models import DocumentContent, EvaluationInput  # noqa: E402
from src.reports.generators.evaluation_report_generator import (  # noqa: E402
    EvaluationReportGenerator,
)
from src.tools.pdf_parser import PDFParser  # noqa: E402
from src.utils.workflow_controller import WorkflowController  # noqa: E402

# Page configuration
st.set_page_config(
    page_title="LLM as a Judge - Accessibility Evaluator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


class AccessibilityEvaluatorApp:
    """Main application class for the Streamlit interface"""

    def __init__(self):
        """Initialize the application"""
        self.pdf_parser = PDFParser()
        self.report_generator = EvaluationReportGenerator()
        self.llm_manager: Optional[LLMManager] = None
        self.crew: Optional[AccessibilityEvaluationCrew] = None
        self.workflow_controller: Optional[WorkflowController] = None
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state variables"""
        if "system_configured" not in st.session_state:
            st.session_state.system_configured = False
        if "evaluation_input" not in st.session_state:
            st.session_state.evaluation_input = None
        if "evaluation_results" not in st.session_state:
            st.session_state.evaluation_results = None
        if "workflow_status" not in st.session_state:
            st.session_state.workflow_status = None

    def run(self):
        """Main application entry point"""
        st.title("⚖️ LLM as a Judge - Accessibility Remediation Plan Evaluator")
        st.markdown(
            """
        This system uses Gemini Pro and GPT-4 as expert judges to evaluate accessibility
        remediation plans and synthesize an optimal solution.
        """
        )

        # Sidebar for navigation and configuration
        self._render_sidebar()

        # Main content area
        if not st.session_state.system_configured:
            self._render_configuration_page()
        else:
            # Navigation tabs
            tab1, tab2, tab3, tab4 = st.tabs(
                [
                    "📤 Upload & Configure",
                    "🔄 Run Evaluation",
                    "📊 Results Dashboard",
                    "📋 Export & Reports",
                ]
            )

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
                # Mock status for demo - in real implementation would test connections
                st.success("✅ Gemini Pro")
                st.success("✅ GPT-4")
            else:
                st.warning("⚠️ APIs not configured")

            # Workflow Status
            st.subheader("Workflow Status")
            if (
                hasattr(st.session_state, "workflow_status")
                and st.session_state.workflow_status
            ):
                status = st.session_state.workflow_status

                # Progress bar
                progress = status.get("progress", 0)
                st.progress(progress / 100)

                # Current phase
                phase = status.get("phase", "idle")
                st.info(f"Phase: {phase.replace('_', ' ').title()}")

                # Status indicator
                status_text = status.get("status", "idle")
                if status_text == "running":
                    st.warning("🔄 Running")
                elif status_text == "completed":
                    st.success("✅ Completed")
                elif status_text == "failed":
                    st.error("❌ Failed")
                else:
                    st.info("💤 Idle")
            else:
                st.info("💤 System Idle")

            # System Information
            st.subheader("System Info")
            st.info(
                f"""
            **Evaluation Framework:** WCAG-based scoring
            **Criteria Weights:**
            • Strategic Prioritization: 40%
            • Technical Specificity: 30%
            • Comprehensiveness: 20%
            • Long-term Vision: 10%
            """
            )

    def _render_configuration_page(self):
        """Render system configuration interface"""
        st.header("🚀 System Configuration")

        st.markdown(
            """
        Configure your API keys to enable the LLM judges. Both Gemini Pro and GPT-4
        are required for the dual-judge evaluation system.
        """
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🤖 Gemini Pro Configuration")
            gemini_key = st.text_input(
                "Google API Key",
                type="password",
                placeholder="Enter your Google AI Studio API key",
                help="Get your API key from Google AI Studio",
            )

        with col2:
            st.subheader("🧠 GPT-4 Configuration")
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="Enter your OpenAI API key",
                help="Get your API key from OpenAI",
            )

        # Configuration button
        if st.button("🔧 Configure System", type="primary"):
            if gemini_key and openai_key:
                try:
                    # Initialize LLM manager
                    config = LLMConfig(
                        gemini_api_key=gemini_key, openai_api_key=openai_key
                    )
                    self.llm_manager = LLMManager(config)

                    # Initialize crew and workflow controller
                    self.crew = AccessibilityEvaluationCrew(self.llm_manager)
                    self.workflow_controller = WorkflowController(self.crew)

                    st.session_state.system_configured = True
                    st.success("✅ System configured successfully!")
                    st.rerun()

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
                type=["pdf"],
                help="Upload the original accessibility audit report",
            )

            if audit_file:
                # Mock parsing for demo
                st.success(f"✅ Audit report parsed: {audit_file.name}")

                # Store mock data
                st.session_state.audit_content = {
                    "title": audit_file.name,
                    "page_count": 5,
                    "content": "Mock audit content for demonstration...",
                }

        with col2:
            st.subheader("📑 Remediation Plans")
            plan_files = st.file_uploader(
                "Upload remediation plans (PDFs)",
                type=["pdf"],
                accept_multiple_files=True,
                help="Upload all remediation plans to be evaluated",
            )

            if plan_files:
                parsed_plans = {}

                for plan_file in plan_files:
                    plan_name = plan_file.name.replace(".pdf", "")
                    parsed_plans[plan_name] = {
                        "title": plan_file.name,
                        "page_count": 3,
                        "content": f"Mock content for {plan_name}...",
                    }
                    st.success(f"✅ {plan_name}: {plan_file.name}")

                if parsed_plans:
                    st.session_state.remediation_plans = parsed_plans
                    st.info(f"📊 Total plans loaded: {len(parsed_plans)}")

        # Evaluation configuration
        if hasattr(st.session_state, "audit_content") and hasattr(
            st.session_state, "remediation_plans"
        ):
            st.divider()
            st.subheader("⚙️ Evaluation Configuration")

            col1, col2 = st.columns([2, 1])

            with col1:
                execution_mode = st.selectbox(
                    "Execution Mode",
                    ["sequential", "parallel"],
                    help="Sequential: Phases run one after another. Parallel: Maximum concurrency.",
                )

                include_consensus = st.checkbox(
                    "Enable Consensus Building",
                    value=True,
                    help="Automatically resolve disagreements between judges",
                )

            with col2:
                if st.button("✅ Prepare Evaluation", type="primary"):
                    st.session_state.evaluation_prepared = True
                    st.session_state.execution_mode = execution_mode
                    st.session_state.include_consensus = include_consensus

                    st.success("✅ Evaluation prepared! Go to 'Run Evaluation' tab.")

    def _render_evaluation_interface(self):
        """Render evaluation execution interface"""
        st.header("🔄 Run Evaluation")

        if not hasattr(st.session_state, "evaluation_prepared"):
            st.warning(
                "⚠️ Please upload and configure files in the 'Upload & Configure' tab first."
            )
            return

        # Evaluation summary
        st.subheader("📋 Evaluation Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Audit Report", "1 document", "5 pages")

        with col2:
            plan_count = len(st.session_state.get("remediation_plans", {}))
            total_pages = plan_count * 3  # Mock calculation
            st.metric(
                "Remediation Plans", f"{plan_count} documents", f"{total_pages} pages"
            )

        with col3:
            estimated_time = f"{plan_count * 2 + 3}-{plan_count * 2 + 5}"
            st.metric("Estimated Time", estimated_time, "minutes")

        # Execution controls
        st.divider()

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button("🚀 Start Evaluation", type="primary"):
                self._start_evaluation()

        with col2:
            if st.button("⏹️ Stop Evaluation"):
                self._stop_evaluation()

        with col3:
            if st.button("🔄 Refresh Status"):
                self._refresh_status()

        # Progress monitoring
        if hasattr(st.session_state, "workflow_status"):
            self._render_progress_monitor()

    def _render_progress_monitor(self):
        """Render real-time progress monitoring"""
        st.subheader("📈 Evaluation Progress")

        status = st.session_state.workflow_status

        # Main progress bar
        progress = status.get("progress", 0)
        st.progress(progress / 100, f"Overall Progress: {progress}%")

        # Phase information
        phase = status.get("phase", "idle")
        st.info(f"**Current Phase:** {phase.replace('_', ' ').title()}")

        # Detailed status
        with st.expander("🔍 Detailed Status", expanded=True):
            status_text = status.get("status", "idle")

            if status_text == "running":
                st.success("🔄 Evaluation in progress...")

                # Phase breakdown
                phases = [
                    ("Initialization", 10),
                    ("Individual Evaluations", 40),
                    ("Cross-Plan Comparison", 60),
                    ("Consensus Building", 75),
                    ("Plan Synthesis", 90),
                    ("Final Compilation", 100),
                ]

                for phase_name, phase_progress in phases:
                    if progress >= phase_progress:
                        st.success(f"✅ {phase_name}")
                    elif progress >= phase_progress - 15:
                        st.warning(f"🔄 {phase_name}")
                    else:
                        st.info(f"⏳ {phase_name}")

            elif status_text == "completed":
                st.success("✅ Evaluation completed successfully!")
                if st.button("📊 View Results"):
                    # Generate mock results for demo
                    self._generate_mock_results()

            elif status_text == "failed":
                st.error(
                    f"❌ Evaluation failed: {status.get('error', 'Unknown error')}"
                )
                if st.button("🔄 Retry Evaluation"):
                    self._start_evaluation()

    def _render_results_dashboard(self):
        """Render comprehensive results dashboard"""
        st.header("📊 Evaluation Results Dashboard")

        if (
            not hasattr(st.session_state, "evaluation_results")
            or not st.session_state.evaluation_results
        ):
            st.info("🔍 No evaluation results available. Run an evaluation first.")
            return

        results = st.session_state.evaluation_results

        # Results tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📈 Score Overview",
                "🔍 Detailed Analysis",
                "⚖️ Judge Comparison",
                "🎯 Synthesis Plan",
            ]
        )

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
            x="Plan",
            y="Overall Score",
            color="Overall Score",
            color_continuous_scale="RdYlGn",
            title="Overall Plan Scores",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Criteria breakdown
        col1, col2 = st.columns(2)

        with col1:
            # Radar chart for top plans
            top_plans = df.nlargest(3, "Overall Score")
            self._render_radar_chart(top_plans)

        with col2:
            # Score distribution
            fig = px.histogram(
                df, x="Overall Score", nbins=10, title="Score Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Rankings table
        st.subheader("🏆 Plan Rankings")
        ranking_df = df.sort_values("Overall Score", ascending=False).reset_index(
            drop=True
        )
        ranking_df.index += 1
        st.dataframe(ranking_df, use_container_width=True)

    def _render_radar_chart(self, plans_df):
        """Render radar chart for plan comparison"""
        fig = go.Figure()

        criteria = [
            "Strategic Prioritization",
            "Technical Specificity",
            "Comprehensiveness",
            "Long-term Vision",
        ]

        for _, plan in plans_df.iterrows():
            fig.add_trace(
                go.Scatterpolar(
                    r=[plan[criterion] for criterion in criteria],
                    theta=criteria,
                    fill="toself",
                    name=plan["Plan"],
                )
            )

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True,
            title="Top Plans - Criteria Comparison",
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_detailed_analysis(self, results):
        """Render detailed analysis for each plan"""
        st.subheader("🔍 Detailed Plan Analysis")

        # Plan selector
        plans = list(results.get("plans", {}).keys())
        if not plans:
            st.warning("No plans available for analysis")
            return

        selected_plan = st.selectbox("Select Plan for Detailed Analysis", plans)

        if selected_plan:
            plan_analysis = results["plans"][selected_plan]

            # Score breakdown
            col1, col2 = st.columns([1, 2])

            with col1:
                st.metric("Overall Score", f"{plan_analysis['overall_score']}/10")

                # Criteria scores
                for criterion, score in plan_analysis["criteria_scores"].items():
                    st.metric(criterion.replace("_", " ").title(), f"{score}/10")

            with col2:
                # Detailed analysis text
                st.text_area(
                    "Detailed Analysis",
                    plan_analysis.get("analysis", "No detailed analysis available."),
                    height=200,
                )

            # Pros and Cons
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("✅ Strengths")
                for pro in plan_analysis.get("strengths", []):
                    st.success(f"• {pro}")

            with col2:
                st.subheader("❌ Weaknesses")
                for con in plan_analysis.get("weaknesses", []):
                    st.error(f"• {con}")

    def _render_judge_comparison(self, results):
        """Render judge comparison interface"""
        st.subheader("⚖️ Judge Comparison")

        # Judge agreement analysis
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Overall Agreement", "85%", "High")

        with col2:
            st.metric("Consensus Required", "2 plans", "Medium conflict")

        # Comparison table
        st.subheader("📊 Judge Score Comparison")

        comparison_data = []
        for plan_name, plan_data in results.get("plans", {}).items():
            comparison_data.append(
                {
                    "Plan": plan_name,
                    "Gemini Score": plan_data.get("gemini_score", 0),
                    "GPT-4 Score": plan_data.get("gpt4_score", 0),
                    "Final Score": plan_data.get("overall_score", 0),
                    "Agreement": (
                        "High"
                        if abs(
                            plan_data.get("gemini_score", 0)
                            - plan_data.get("gpt4_score", 0)
                        )
                        < 1
                        else "Low"
                    ),
                }
            )

        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)

            # Judge comparison chart
            fig = px.scatter(
                comparison_df,
                x="Gemini Score",
                y="GPT-4 Score",
                color="Agreement",
                size="Final Score",
                hover_data=["Plan"],
                title="Judge Score Agreement Analysis",
            )
            # Add diagonal line for perfect agreement
            fig.add_shape(
                type="line",
                x0=0,
                y0=0,
                x1=10,
                y1=10,
                line=dict(color="red", dash="dash"),
                name="Perfect Agreement",
            )
            st.plotly_chart(fig, use_container_width=True)

    def _render_synthesis_plan(self, results):
        """Render synthesis plan interface"""
        st.subheader("🎯 Synthesized Recommendations")

        synthesis = results.get("synthesis", {})

        if not synthesis:
            st.warning("No synthesis recommendations available")
            return

        # Executive summary
        st.subheader("📋 Executive Summary")
        st.markdown(synthesis.get("summary", "No synthesis summary available."))

        # Key recommendations
        st.subheader("🎯 Key Recommendations")
        for i, rec in enumerate(synthesis.get("recommendations", []), 1):
            st.markdown(f"**{i}.** {rec}")

        # Implementation timeline
        if "timeline" in synthesis:
            st.subheader("📅 Implementation Timeline")

            timeline_data = synthesis["timeline"]
            fig = px.timeline(
                timeline_data,
                x_start="start_date",
                x_end="end_date",
                y="phase",
                color="priority",
                title="Implementation Timeline",
            )
            st.plotly_chart(fig, use_container_width=True)

    def _render_export_interface(self):
        """Render export and reporting interface"""
        st.header("📋 Export Reports & Data")

        if (
            not hasattr(st.session_state, "evaluation_results")
            or not st.session_state.evaluation_results
        ):
            st.warning(
                "⚠️ No evaluation results available. Please run an evaluation first."
            )
            return

        results = st.session_state.evaluation_results

        # Report Type Selection
        st.subheader("📄 PDF Report Generation")

        col1, col2 = st.columns([2, 1])

        with col1:
            report_types = [
                "Executive Summary",
                "Detailed Evaluation Report",
                "Comparative Analysis",
                "Synthesis Recommendations",
            ]

            selected_report = st.selectbox("Select Report Type", report_types)

        with col2:
            st.metric("Report Size", "~15-25 pages", "Estimated")

        # Report Configuration
        with st.expander("🔧 Report Configuration", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                _include_charts = st.checkbox(
                    "Include Charts & Visualizations", value=True
                )
                _include_raw_data = st.checkbox(
                    "Include Raw Evaluation Data", value=False
                )
                _include_cover_page = st.checkbox("Include Cover Page", value=True)

            with col2:
                _page_size = st.selectbox(
                    "Page Size", ["A4", "Letter", "Legal"], index=0
                )
                _font_family = st.selectbox(
                    "Font Family", ["Arial", "Times New Roman", "Calibri"], index=0
                )
                _include_toc = st.checkbox("Include Table of Contents", value=True)

        # Generate Report Button
        if st.button("🔄 Generate PDF Report", type="primary"):
            with st.spinner("Generating comprehensive PDF report..."):
                try:
                    # Mock PDF generation for demo
                    report_content = self._generate_mock_pdf_content(
                        selected_report, results
                    )

                    st.success("✅ PDF Report Generated Successfully!")
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=report_content,
                        file_name=f"accessibility_evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                    )

                    # Show report preview info
                    st.info(
                        f"""
                    **Report Details:**
                    - Type: {selected_report}
                    - Pages: ~{self._estimate_report_pages(results)} pages
                    - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                    )

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

    # Helper methods
    def _start_evaluation(self):
        """Start the evaluation workflow"""
        try:
            # Mock evaluation start for demo
            st.session_state.workflow_status = {
                "status": "running",
                "phase": "initialization",
                "progress": 5,
            }
            st.success("✅ Evaluation started!")

            # Simulate progress with time
            import time

            for progress in [10, 25, 40, 60, 75, 90, 100]:
                time.sleep(0.5)  # Simulate work
                st.session_state.workflow_status["progress"] = progress
                if progress == 100:
                    st.session_state.workflow_status["status"] = "completed"
                    self._generate_mock_results()

            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to start evaluation: {str(e)}")

    def _stop_evaluation(self):
        """Stop the evaluation workflow"""
        if hasattr(st.session_state, "workflow_status"):
            st.session_state.workflow_status["status"] = "stopped"
            st.warning("⏹️ Evaluation stopped")
            st.rerun()

    def _refresh_status(self):
        """Refresh the evaluation status"""
        st.info("🔄 Status refreshed")
        st.rerun()

    def _generate_mock_results(self):
        """Generate mock evaluation results for demonstration"""
        plans = list(st.session_state.get("remediation_plans", {}).keys())

        mock_results = {"plans": {}}

        # Generate mock scores for each plan
        import random

        for plan in plans:
            mock_results["plans"][plan] = {
                "overall_score": round(random.uniform(6.5, 9.5), 1),
                "criteria_scores": {
                    "strategic_prioritization": round(random.uniform(6, 10), 1),
                    "technical_specificity": round(random.uniform(6, 10), 1),
                    "comprehensiveness": round(random.uniform(6, 10), 1),
                    "long_term_vision": round(random.uniform(6, 10), 1),
                },
                "gemini_score": round(random.uniform(6.5, 9.5), 1),
                "gpt4_score": round(random.uniform(6.5, 9.5), 1),
                "analysis": f"Comprehensive analysis of {plan} shows strong alignment with accessibility standards...",
                "strengths": [
                    "Clear implementation roadmap",
                    "Strong technical foundation",
                    "Comprehensive coverage of issues",
                ],
                "weaknesses": [
                    "Limited timeline details",
                    "Resource allocation unclear",
                ],
            }

        # Add synthesis
        mock_results["synthesis"] = {
            "summary": "Based on comprehensive evaluation, the recommended approach combines elements from multiple plans...",
            "recommendations": [
                "Prioritize high-impact accessibility fixes from Plan A",
                "Adopt technical implementation approach from Plan B",
                "Integrate comprehensive testing strategy from Plan C",
            ],
            "timeline": [
                {
                    "phase": "Phase 1",
                    "start_date": "2025-09-01",
                    "end_date": "2025-10-01",
                    "priority": "High",
                },
                {
                    "phase": "Phase 2",
                    "start_date": "2025-10-01",
                    "end_date": "2025-11-15",
                    "priority": "Medium",
                },
                {
                    "phase": "Phase 3",
                    "start_date": "2025-11-15",
                    "end_date": "2025-12-31",
                    "priority": "Low",
                },
            ],
        }

        st.session_state.evaluation_results = mock_results

    def _extract_score_data(self, results):
        """Extract scoring data for visualization"""
        score_data = []

        for plan_name, plan_data in results.get("plans", {}).items():
            score_data.append(
                {
                    "Plan": plan_name,
                    "Overall Score": plan_data.get("overall_score", 0),
                    "Strategic Prioritization": plan_data.get(
                        "criteria_scores", {}
                    ).get("strategic_prioritization", 0),
                    "Technical Specificity": plan_data.get("criteria_scores", {}).get(
                        "technical_specificity", 0
                    ),
                    "Comprehensiveness": plan_data.get("criteria_scores", {}).get(
                        "comprehensiveness", 0
                    ),
                    "Long-term Vision": plan_data.get("criteria_scores", {}).get(
                        "long_term_vision", 0
                    ),
                }
            )

        return score_data

    def _generate_mock_pdf_content(
        self, report_type: str, results: Dict[str, Any]
    ) -> bytes:
        """Generate actual PDF content using the report generator"""
        try:
            # Use the real report generator
            pdf_path = self.report_generator.generate_pdf_report(
                evaluation_results=results,
                report_type=report_type.lower().replace(" ", "_"),
            )

            # Read the generated PDF
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            return pdf_bytes

        except Exception:
            # Fallback to mock content if PDF generation fails
            content = f"Mock PDF content for {report_type}\n\nGenerated: {datetime.now()}\n\nResults: {json.dumps(results, indent=2)}"
            return content.encode("utf-8")

    def _estimate_report_pages(self, results: Dict[str, Any]) -> int:
        """Estimate number of pages in generated report"""
        base_pages = 8
        plans_count = len(results.get("plans", {}))
        return base_pages + plans_count * 2

    def _export_charts_as_images(self, results: Dict[str, Any]):
        """Export charts as images"""
        st.success("✅ Charts exported successfully! (Mock implementation)")

    def _export_data_as_json(self, results: Dict[str, Any]):
        """Export evaluation data as JSON"""
        try:
            json_path = self.report_generator.generate_json_export(results)

            with open(json_path, "rb") as f:
                json_data = f.read()

            st.download_button(
                label="📥 Download JSON Data",
                data=json_data,
                file_name=f"evaluation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )
            st.success("✅ JSON data ready for download!")
        except Exception as e:
            st.error(f"❌ Error generating JSON: {str(e)}")

    def _export_summary_as_csv(self, results: Dict[str, Any]):
        """Export evaluation summary as CSV"""
        try:
            csv_path = self.report_generator.generate_csv_export(results)

            with open(csv_path, "rb") as f:
                csv_data = f.read()

            st.download_button(
                label="📥 Download CSV Summary",
                data=csv_data,
                file_name=f"evaluation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
            st.success("✅ CSV summary ready for download!")
        except Exception as e:
            st.error(f"❌ Error generating CSV: {str(e)}")


def main():
    """Main entry point"""
    app = AccessibilityEvaluatorApp()
    app.run()


if __name__ == "__main__":
    main()
