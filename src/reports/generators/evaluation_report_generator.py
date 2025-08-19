"""
Evaluation report generator for creating comprehensive evaluation reports.

This module provides functionality to generate PDF and other format reports
from evaluation results, including scoring summaries, detailed analysis,
and visual representations.

References:
    - Phase 4 Plan: Report generation requirements
    - Master Plan: Output formats and documentation
    - LLM Error Handling Enhancement Plan - Phase 3
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ...models.evaluation_models import (
    EvaluationInput,
    EvaluationResult,
    EvaluationStatus,
    PartialEvaluationSummary,
    ResilienceInfo,
)


class EvaluationReportGenerator:
    """
    Generator for comprehensive evaluation reports.

    Creates formatted reports from evaluation results including:
    - Executive summary
    - Detailed plan analysis
    - Score comparisons
    - Synthesis recommendations
    - NA sections for unavailable evaluations
    - LLM availability status
    """

    def __init__(self):
        """Initialize the report generator with default configuration"""
        self.output_dir = Path("output/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()

        # Initialize professional color scheme
        self.colors = {
            "primary": colors.HexColor("#2E86AB"),  # Professional blue
            "secondary": colors.HexColor("#A23B72"),  # Professional purple
            "accent": colors.HexColor("#F18F01"),  # Professional orange
            "success": colors.HexColor("#C73E1D"),  # Professional red
            "light_gray": colors.HexColor("#F8F9FA"),  # Light background
            "dark_gray": colors.HexColor("#343A40"),  # Dark text
            "border": colors.HexColor("#DEE2E6"),  # Border color
        }

    def generate_pdf_report(
        self,
        evaluation_results: Dict[str, Any],
        evaluation_input: Optional[EvaluationInput] = None,
        output_path: Optional[Path] = None,
        report_type: str = "comprehensive",
    ) -> Path:
        """
        Generate a comprehensive PDF evaluation report.

        Args:
            evaluation_results: Results from the evaluation process
            evaluation_input: Original evaluation input data
            output_path: Optional custom output path
            report_type: Type of report to generate

        Returns:
            Path to the generated PDF report
        """
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = (
                    self.output_dir / f"evaluation_report_{report_type}_{timestamp}.pdf"
                )

            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            # Build report content
            story = []

            # Title page
            story.extend(self._create_title_page(evaluation_results, report_type))
            story.append(PageBreak())

            # LLM Availability Status (if resilience info is available)
            if "resilience_info" in evaluation_results:
                story.extend(
                    self._create_availability_status_section(evaluation_results)
                )
                story.append(PageBreak())

            # Executive summary
            story.extend(self._create_executive_summary(evaluation_results))
            story.append(PageBreak())

            # Scoring overview
            story.extend(self._create_scoring_overview(evaluation_results))
            story.append(PageBreak())

            # Detailed analysis
            story.extend(self._create_detailed_analysis(evaluation_results))

            if evaluation_results.get("synthesis"):
                story.append(PageBreak())
                story.extend(self._create_synthesis_section(evaluation_results))

            # Build PDF
            doc.build(story)

            return output_path

        except Exception:
            # Fallback to simple text report
            fallback_path = self._generate_text_report(evaluation_results, output_path)
            return fallback_path

    def generate_unified_pdf_report(
        self,
        evaluation_results: Dict[str, Any],
        output_dir: Path,
        metadata: Dict[str, Any],
    ) -> Path:
        """
        Generate a single unified PDF report containing all sections.

        Args:
            evaluation_results: Results from evaluation process
            output_dir: Output directory for the report
            metadata: Execution metadata

        Returns:
            Path to the generated unified PDF report
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = (
                output_dir / f"accessibility_evaluation_report_{timestamp}.pdf"
            )

            # Create document with professional styling
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
            )

            # Note: Header and footer integration requires custom canvas maker
            # For now, we'll build without headers/footers to ensure functionality

            # Build story with all sections
            story = []

            # 1. Title Page
            story.extend(self._create_title_page(evaluation_results, "Unified Report"))
            story.append(PageBreak())

            # 2. Table of Contents
            story.extend(self._create_table_of_contents())
            story.append(PageBreak())

            # 3. Executive Summary
            story.extend(self._create_executive_summary(evaluation_results))
            story.append(PageBreak())

            # 4. Execution Summary Section
            story.extend(self._create_execution_summary_section(metadata))
            story.append(PageBreak())

            # 5. Completion Summary Section
            story.extend(self._create_completion_summary_section(evaluation_results))
            story.append(PageBreak())

            # 6. Detailed Analysis
            story.extend(self._create_detailed_analysis(evaluation_results))
            story.append(PageBreak())

            # 7. Scoring Overview
            story.extend(self._create_scoring_overview(evaluation_results))
            story.append(PageBreak())

            # 7.5. Enhanced Charts (if available)
            chart_elements = self._create_chart_elements(evaluation_results)
            if chart_elements:
                story.extend(chart_elements)
                story.append(PageBreak())

            # 8. Recommendations/Synthesis
            if evaluation_results.get("synthesis"):
                story.extend(self._create_synthesis_section(evaluation_results))
            else:
                story.extend(self._create_recommendations_section(evaluation_results))

            # Build PDF
            doc.build(story)
            return output_path

        except Exception as e:
            raise Exception(f"Failed to generate unified PDF report: {e}")

    def _create_page_header_footer(self, canvas, doc):
        """Add professional headers and footers to each page."""
        # Header
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(self.colors["primary"])
        canvas.drawString(72, 800, "Accessibility Evaluation Report")

        # Add a subtle line under the header
        canvas.setStrokeColor(self.colors["border"])
        canvas.setLineWidth(0.5)
        canvas.line(72, 795, 522, 795)

        # Footer
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(self.colors["dark_gray"])
        canvas.drawString(
            72, 50, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        canvas.drawRightString(522, 50, f"Page {doc.page}")

        # Add a subtle line above the footer
        canvas.setLineWidth(0.5)
        canvas.line(72, 55, 522, 55)

        canvas.restoreState()

    def _create_table_of_contents(self) -> List:
        """
        Create professional table of contents for unified report.

        Returns:
            List of ReportLab elements for table of contents
        """
        story = []

        # Title with enhanced styling
        title_style = getSampleStyleSheet()["Title"]
        title_style.textColor = self.colors["primary"]
        story.append(Paragraph("Table of Contents", title_style))
        story.append(Spacer(1, 20))

        # TOC entries with enhanced styling
        toc_style = getSampleStyleSheet()["Normal"]
        toc_style.textColor = self.colors["dark_gray"]
        toc_style.fontSize = 11
        toc_style.leading = 16

        toc_entries = [
            "Executive Summary",
            "Execution Summary",
            "Completion Summary",
            "Detailed Analysis",
            "Scoring Overview",
            "Recommendations",
        ]

        for i, entry in enumerate(toc_entries, 1):
            # Create styled TOC entry with page number placeholder
            toc_text = f"<b>{i}.</b> {entry}"
            story.append(Paragraph(toc_text, toc_style))
            story.append(Spacer(1, 4))

        # Add a subtle divider
        story.append(Spacer(1, 10))
        divider = Table(
            [[""]],
            colWidths=[400],
            style=[("LINEBELOW", (0, 0), (-1, 0), 0.5, self.colors["border"])],
        )
        story.append(divider)

        return story

    def _create_execution_summary_section(self, metadata: Dict[str, Any]) -> List:
        """
        Create execution summary section for unified report.

        Args:
            metadata: Execution metadata

        Returns:
            List of ReportLab elements for execution summary
        """
        story = []

        # Section title
        title_style = getSampleStyleSheet()["Heading1"]
        story.append(Paragraph("Execution Summary", title_style))
        story.append(Spacer(1, 12))

        # Metadata table with enhanced styling
        normal_style = getSampleStyleSheet()["Normal"]

        # Create metadata table
        metadata_rows = []
        for key, value in metadata.items():
            if isinstance(value, dict):
                # Handle nested metadata
                for sub_key, sub_value in value.items():
                    metadata_rows.append([f"{key}.{sub_key}", str(sub_value)])
            else:
                metadata_rows.append([key, str(value)])

        if metadata_rows:
            table = Table(metadata_rows, colWidths=[200, 300])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), self.colors["primary"]),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), self.colors["light_gray"]),
                        ("GRID", (0, 0), (-1, -1), 0.5, self.colors["border"]),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, self.colors["light_gray"]],
                        ),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("LEFTPADDING", (0, 0), (-1, -1), 12),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ]
                )
            )
            story.append(table)
        else:
            story.append(Paragraph("No execution metadata available", normal_style))

        return story

    def _create_completion_summary_section(
        self, evaluation_results: Dict[str, Any]
    ) -> List:
        """
        Create completion summary section for unified report.

        Args:
            evaluation_results: Evaluation results

        Returns:
            List of ReportLab elements for completion summary
        """
        story = []

        # Section title
        title_style = getSampleStyleSheet()["Heading1"]
        story.append(Paragraph("Completion Summary", title_style))
        story.append(Spacer(1, 12))

        normal_style = getSampleStyleSheet()["Normal"]

        # Calculate completion statistics
        plans = evaluation_results.get("plans", {})
        total_plans = len(plans)
        completed_plans = sum(
            1 for plan in plans.values() if plan.get("status") == "completed"
        )
        na_plans = sum(1 for plan in plans.values() if plan.get("status") == "NA")

        completion_pct = (completed_plans / total_plans * 100) if total_plans > 0 else 0

        # Create completion summary
        summary_text = f"""
        <b>Total Plans:</b> {total_plans}<br/>
        <b>Completed Evaluations:</b> {completed_plans}<br/>
        <b>NA Evaluations:</b> {na_plans}<br/>
        <b>Completion Rate:</b> {completion_pct:.1f}%
        """

        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 12))

        # Add resilience information if available
        if "resilience_info" in evaluation_results:
            resilience_info = evaluation_results["resilience_info"]
            if resilience_info.get("partial_evaluation"):
                story.append(
                    Paragraph(
                        "<b>Note:</b> This evaluation was completed with partial LLM availability.",
                        normal_style,
                    )
                )
                story.append(Spacer(1, 8))

        return story

    def _create_recommendations_section(
        self, evaluation_results: Dict[str, Any]
    ) -> List:
        """
        Create recommendations section for unified report.

        Args:
            evaluation_results: Evaluation results

        Returns:
            List of ReportLab elements for recommendations
        """
        story = []

        # Section title
        title_style = getSampleStyleSheet()["Heading1"]
        story.append(Paragraph("Recommendations", title_style))
        story.append(Spacer(1, 12))

        normal_style = getSampleStyleSheet()["Normal"]

        # Create recommendations based on evaluation results
        plans = evaluation_results.get("plans", {})
        if plans:
            # Sort plans by score if available
            scored_plans = []
            for plan_name, plan_data in plans.items():
                if (
                    plan_data.get("status") == "completed"
                    and "overall_score" in plan_data
                ):
                    scored_plans.append((plan_name, plan_data["overall_score"]))

            if scored_plans:
                scored_plans.sort(key=lambda x: x[1], reverse=True)

                story.append(Paragraph("<b>Top Recommendations:</b>", normal_style))
                story.append(Spacer(1, 8))

                for i, (plan_name, score) in enumerate(scored_plans[:3], 1):
                    story.append(
                        Paragraph(
                            f"{i}. <b>{plan_name}</b> (Score: {score}/10)", normal_style
                        )
                    )
                    story.append(Spacer(1, 4))
            else:
                story.append(
                    Paragraph(
                        "No scored plans available for recommendations.", normal_style
                    )
                )
        else:
            story.append(
                Paragraph(
                    "No evaluation results available for recommendations.", normal_style
                )
            )

        return story

    def _create_chart_elements(self, evaluation_results: Dict[str, Any]) -> List:
        """
        Create enhanced chart elements for the report.

        Args:
            evaluation_results: Evaluation results

        Returns:
            List of ReportLab elements for charts
        """
        story = []

        # Create a scoring comparison chart
        plans = evaluation_results.get("plans", {})
        if plans and len(plans) > 1:
            # Extract scores for chart
            plan_names = []
            plan_scores = []

            for plan_name, plan_data in plans.items():
                if (
                    plan_data.get("status") == "completed"
                    and "overall_score" in plan_data
                ):
                    plan_names.append(plan_name)
                    plan_scores.append(plan_data["overall_score"])

            if len(plan_scores) > 1:
                # Create a simple bar chart representation using tables
                story.append(Spacer(1, 12))

                # Chart title
                chart_title_style = getSampleStyleSheet()["Heading2"]
                chart_title_style.textColor = self.colors["secondary"]
                story.append(Paragraph("Score Comparison Chart", chart_title_style))
                story.append(Spacer(1, 8))

                # Create chart table
                chart_data = []
                chart_data.append(["Plan", "Score", "Visual"])

                for name, score in zip(plan_names, plan_scores):
                    # Create a visual bar representation
                    bar_length = int((score / 10) * 20)  # Scale to 20 characters
                    bar = "█" * bar_length
                    chart_data.append([name, f"{score}/10", bar])

                chart_table = Table(chart_data, colWidths=[150, 80, 200])
                chart_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), self.colors["secondary"]),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),
                            ("GRID", (0, 0), (-1, -1), 0.5, self.colors["border"]),
                            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 1), (-1, -1), 9),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )

                story.append(chart_table)
                story.append(Spacer(1, 12))

        return story

    def _create_title_page(self, results: Dict[str, Any], report_type: str) -> List:
        """Create the title page content"""
        content = []

        # Title
        title = Paragraph(
            f"Accessibility Evaluation Report<br/><br/>{report_type.title()}",
            self.styles["Title"],
        )
        content.append(title)
        content.append(Spacer(1, 0.5 * inch))

        # Metadata
        metadata = [
            f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"<b>Plans Evaluated:</b> {len(results.get('plans', {}))}",
            f"<b>Report Type:</b> {report_type.title()}",
        ]

        # Add resilience information if available
        if "resilience_info" in results:
            resilience_info = results["resilience_info"]
            if resilience_info.get("partial_evaluation"):
                metadata.append("Evaluation Type: Partial (Some LLMs Unavailable)")
                completion_pct = resilience_info.get("completion_percentage", 0)
                metadata.append(f"Completion Rate: {completion_pct:.1f}%")
            else:
                metadata.append("Evaluation Type: Complete (All LLMs Available)")

        for item in metadata:
            content.append(Paragraph(item, self.styles["Normal"]))
            content.append(Spacer(1, 0.2 * inch))

        return content

    def _create_availability_status_section(self, results: Dict[str, Any]) -> List:
        """Create LLM availability status section"""
        content = []

        # Section title
        content.append(Paragraph("LLM Availability Status", self.styles["Heading2"]))
        content.append(Spacer(1, 0.3 * inch))

        resilience_info = results.get("resilience_info", {})
        llm_availability = results.get("llm_availability", {})

        # Availability summary
        na_count = resilience_info.get("na_evaluations_count", 0)
        completion_pct = resilience_info.get("completion_percentage", 100)

        # Status summary
        if resilience_info.get("partial_evaluation"):
            status_text = f"""
            <b>Evaluation Status:</b> Partial Evaluation Completed

            This evaluation was completed with reduced LLM availability.
            Some evaluations could not be performed due to LLM connectivity issues.

            <b>Completion Rate:</b> {completion_pct:.1f}%
            <b>NA Evaluations:</b> {na_count}
            """
        else:
            status_text = f"""
            <b>Evaluation Status:</b> Complete Evaluation

            All LLMs were available during this evaluation, providing full coverage
            of all planned assessments.

            <b>Completion Rate:</b> {completion_pct:.1f}%
            """

        content.append(Paragraph(status_text, self.styles["Normal"]))
        content.append(Spacer(1, 0.2 * inch))

        # LLM status details
        content.append(Paragraph("<b>LLM Status Details:</b>", self.styles["Normal"]))
        content.append(Spacer(1, 0.1 * inch))

        for llm_name, is_available in llm_availability.items():
            status = "Available" if is_available else "Unavailable"
            status_color = "green" if is_available else "red"
            content.append(
                Paragraph(
                    f"• <b>{llm_name}:</b> <font color='{status_color}'>{status}</font>",
                    self.styles["Normal"],
                )
            )

        content.append(Spacer(1, 0.2 * inch))

        # Troubleshooting guidance for partial evaluations
        if resilience_info.get("partial_evaluation"):
            troubleshooting_text = """
            <b>Troubleshooting Guidance:</b>

            If you see "NA" (Not Available) sections in this report, it indicates that
            certain LLMs were unavailable during evaluation. This can happen due to:

            • API connectivity issues
            • Rate limiting or quota exceeded
            • Temporary service outages
            • Network connectivity problems

            To resolve these issues:
            1. Check your internet connection
            2. Verify API keys are valid and have sufficient quota
            3. Wait a few minutes and retry the evaluation
            4. Contact support if issues persist

            The evaluation results shown are based on available LLMs and provide
            valuable insights despite the partial completion.
            """
            content.append(Paragraph(troubleshooting_text, self.styles["Normal"]))

        content.append(Spacer(1, 0.3 * inch))

        return content

    def _create_executive_summary(self, results: Dict[str, Any]) -> List:
        """Create executive summary section"""
        content = []

        # Section title
        content.append(Paragraph("Executive Summary", self.styles["Heading1"]))
        content.append(Spacer(1, 0.3 * inch))

        # Handle both "individual_evaluations" and "plans" keys for backward compatibility
        plans = results.get("individual_evaluations", {})
        if not plans:
            plans = results.get("plans", {})
        resilience_info = results.get("resilience_info", {})

        if plans:
            # Filter out NA evaluations for summary
            completed_plans = {
                name: data for name, data in plans.items() if data.get("status") != "NA"
            }

            if completed_plans:
                # Top scoring plan from completed evaluations
                top_plan = max(
                    completed_plans.items(), key=lambda x: x[1].get("overall_score", 0)
                )

                summary_text = f"""
                Based on comprehensive evaluation of {len(plans)} remediation plans,
                <b>{top_plan[0]}</b> achieved the highest overall score of
                <b>{top_plan[1].get('overall_score', 0)}/10</b> among completed evaluations.

                The evaluation assessed plans across four key criteria:
                • Strategic Prioritization (40% weight)
                • Technical Specificity (30% weight)
                • Comprehensiveness (20% weight)
                • Long-term Vision (10% weight)
                """

                # Add partial evaluation notice if applicable
                if resilience_info.get("partial_evaluation"):
                    completion_pct = resilience_info.get("completion_percentage", 0)
                    na_count = resilience_info.get("na_evaluations_count", 0)
                    summary_text += f"""

                    <b>Note:</b> This evaluation was completed with {completion_pct:.1f}% coverage
                    ({na_count} evaluations marked as NA due to LLM availability issues).
                    Please refer to the LLM Availability Status section for details.
                    """
            else:
                summary_text = """
                <b>Evaluation Summary:</b>

                All evaluations were marked as NA due to LLM availability issues.
                Please check the LLM Availability Status section for troubleshooting guidance
                and retry the evaluation when LLM services are available.
                """
        else:
            summary_text = "No evaluation results available."

        content.append(Paragraph(summary_text, self.styles["Normal"]))
        content.append(Spacer(1, 0.3 * inch))

        return content

    def _create_scoring_overview(self, results: Dict[str, Any]) -> List:
        """Create scoring overview section with tables"""
        content = []

        # Section title
        content.append(Paragraph("Scoring Overview", self.styles["Heading1"]))
        content.append(Spacer(1, 0.3 * inch))

        # Handle both "individual_evaluations" and "plans" keys for backward compatibility
        plans = results.get("individual_evaluations", {})
        if not plans:
            plans = results.get("plans", {})
        if plans:
            # Create scoring table
            data = [
                [
                    "Plan",
                    "Status",
                    "Overall Score",
                    "Strategic",
                    "Technical",
                    "Comprehensive",
                    "Long-term",
                ]
            ]

            for plan_name, plan_data in plans.items():
                status = plan_data.get("status", "completed")

                if status == "NA":
                    # NA evaluation row
                    row = [
                        plan_name,
                        "NA",
                        "N/A",
                        "N/A",
                        "N/A",
                        "N/A",
                        "N/A",
                    ]
                else:
                    # Completed evaluation row
                    criteria = plan_data.get("criteria_scores", {})
                    row = [
                        plan_name,
                        "Completed",
                        f"{plan_data.get('overall_score', 0)}/10",
                        f"{criteria.get('strategic_prioritization', 0)}/10",
                        f"{criteria.get('technical_specificity', 0)}/10",
                        f"{criteria.get('comprehensiveness', 0)}/10",
                        f"{criteria.get('long_term_vision', 0)}/10",
                    ]
                data.append(row)

            # Create table
            table = Table(
                data,
                colWidths=[
                    1.2 * inch,
                    0.8 * inch,
                    1 * inch,
                    0.9 * inch,
                    0.9 * inch,
                    1.1 * inch,
                    0.9 * inch,
                ],
            )

            # Define table style with NA row highlighting
            style_commands = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]

            # Add background colors for different row types
            for i, row in enumerate(data[1:], 1):  # Skip header row
                if row[1] == "NA":
                    # Highlight NA rows in light red
                    style_commands.append(
                        ("BACKGROUND", (0, i), (-1, i), colors.lightcoral)
                    )
                else:
                    # Completed rows in light green
                    style_commands.append(
                        ("BACKGROUND", (0, i), (-1, i), colors.lightgreen)
                    )

            table.setStyle(TableStyle(style_commands))
            content.append(table)

        content.append(Spacer(1, 0.3 * inch))

        return content

    def _create_detailed_analysis(self, results: Dict[str, Any]) -> List:
        """Create detailed analysis section"""
        content = []

        # Section title
        content.append(Paragraph("Detailed Plan Analysis", self.styles["Heading1"]))
        content.append(Spacer(1, 0.3 * inch))

        plans = results.get("individual_evaluations", {})
        for plan_name, plan_data in plans.items():
            # Plan title
            content.append(Paragraph(f"Plan: {plan_name}", self.styles["Heading2"]))
            content.append(Spacer(1, 0.2 * inch))

            status = plan_data.get("status", "completed")

            if status == "NA":
                # Create NA section
                content.extend(self._create_na_evaluation_section(plan_name, plan_data))
            else:
                # Create completed evaluation section
                content.extend(
                    self._create_completed_evaluation_section(plan_name, plan_data)
                )

            content.append(Spacer(1, 0.3 * inch))

        return content

    def _create_na_evaluation_section(
        self, plan_name: str, plan_data: Dict[str, Any]
    ) -> List:
        """Create standardized NA section for PDF reports"""
        content = []

        # Status indicator
        content.append(
            Paragraph("<b>Status: Not Available (NA)</b>", self.styles["Normal"])
        )
        content.append(Spacer(1, 0.1 * inch))

        # Reason for NA
        na_reason = plan_data.get("na_reason", "LLM unavailable")
        content.append(Paragraph(f"<b>Reason:</b> {na_reason}", self.styles["Normal"]))
        content.append(Spacer(1, 0.1 * inch))

        # LLM information
        llm_used = plan_data.get("llm_used", "Unknown")
        content.append(Paragraph(f"<b>LLM:</b> {llm_used}", self.styles["Normal"]))
        content.append(Spacer(1, 0.1 * inch))

        # Explanation
        explanation_text = """
        This evaluation could not be completed due to LLM availability issues.
        The system attempted to evaluate this plan but encountered connectivity
        or service problems with the required LLM.

        Please refer to the LLM Availability Status section for troubleshooting
        guidance and consider retrying the evaluation when LLM services are available.
        """
        content.append(Paragraph(explanation_text, self.styles["Normal"]))

        return content

    def _create_completed_evaluation_section(
        self, plan_name: str, plan_data: Dict[str, Any]
    ) -> List:
        """Create section for completed evaluation results"""
        content = []

        # Score
        score_text = f"<b>Overall Score:</b> {plan_data.get('overall_score', 0)}/10"
        content.append(Paragraph(score_text, self.styles["Normal"]))
        content.append(Spacer(1, 0.1 * inch))

        # Analysis
        analysis = plan_data.get("analysis", "No detailed analysis available.")
        content.append(Paragraph(f"<b>Analysis:</b> {analysis}", self.styles["Normal"]))
        content.append(Spacer(1, 0.1 * inch))

        # Strengths
        strengths = plan_data.get("strengths", [])
        if strengths:
            content.append(Paragraph("<b>Strengths:</b>", self.styles["Normal"]))
            for strength in strengths:
                content.append(Paragraph(f"• {strength}", self.styles["Normal"]))
            content.append(Spacer(1, 0.1 * inch))

        # Weaknesses
        weaknesses = plan_data.get("weaknesses", [])
        if weaknesses:
            content.append(
                Paragraph("<b>Areas for Improvement:</b>", self.styles["Normal"])
            )
            for weakness in weaknesses:
                content.append(Paragraph(f"• {weakness}", self.styles["Normal"]))

        return content

    def _create_synthesis_section(self, results: Dict[str, Any]) -> List:
        """Create synthesis recommendations section"""
        content = []

        # Section title
        content.append(Paragraph("Synthesis Recommendations", self.styles["Heading1"]))
        content.append(Spacer(1, 0.3 * inch))

        synthesis = results.get("synthesis", {})

        # Summary
        summary = synthesis.get("summary", "No synthesis summary available.")
        content.append(Paragraph(f"<b>Summary:</b> {summary}", self.styles["Normal"]))
        content.append(Spacer(1, 0.2 * inch))

        # Recommendations
        recommendations = synthesis.get("recommendations", [])
        if recommendations:
            content.append(
                Paragraph("<b>Key Recommendations:</b>", self.styles["Normal"])
            )
            for i, rec in enumerate(recommendations, 1):
                content.append(Paragraph(f"{i}. {rec}", self.styles["Normal"]))
            content.append(Spacer(1, 0.2 * inch))

        return content

    def _generate_text_report(
        self, results: Dict[str, Any], output_path: Optional[Path]
    ) -> Path:
        """Generate a fallback text report if PDF generation fails"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"evaluation_report_{timestamp}.txt"
        else:
            output_path = output_path.with_suffix(".txt")

        content = f"""
ACCESSIBILITY EVALUATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 50}

EXECUTIVE SUMMARY
Plans evaluated: {len(results.get('plans', {}))}

SCORING RESULTS
{'=' * 20}
"""

        plans = results.get("individual_evaluations", {})
        for plan_name, plan_data in plans.items():
            content += f"""
Plan: {plan_name}
Overall Score: {plan_data.get('overall_score', 0)}/10
Analysis: {plan_data.get('analysis', 'No analysis available')}

"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path

    def generate_csv_export(
        self, evaluation_results: Dict[str, Any], output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate CSV export of evaluation scores and data.

        Args:
            evaluation_results: Results from the evaluation process
            output_path: Optional custom output path

        Returns:
            Path to the generated CSV file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"evaluation_scores_{timestamp}.csv"

        # Create CSV data
        # Handle both "individual_evaluations" and "plans" keys for backward compatibility
        plans = evaluation_results.get("individual_evaluations", {})
        if not plans:
            plans = evaluation_results.get("plans", {})
        data = []

        for plan_name, plan_data in plans.items():
            status = plan_data.get("status", "completed")

            if status == "NA":
                # NA evaluation row
                na_row = {
                    "Plan": plan_name,
                    "Status": "Not Available",
                    "Overall_Score": None,
                    "Strategic_Prioritization": None,
                    "Technical_Specificity": None,
                    "Comprehensiveness": None,
                    "Long_term_Vision": None,
                    "Gemini_Score": None,
                    "GPT4_Score": None,
                    "NA_Reason": plan_data.get("na_reason", "LLM unavailable"),
                    "LLM_Used": plan_data.get("llm_used", "Unknown"),
                }
                data.append(na_row)
            else:
                # Completed evaluation row
                criteria = plan_data.get("criteria_scores", {})
                completed_row = {
                    "Plan": plan_name,
                    "Status": "Completed",
                    "Overall_Score": plan_data.get("overall_score", 0),
                    "Strategic_Prioritization": criteria.get(
                        "strategic_prioritization", 0
                    ),
                    "Technical_Specificity": criteria.get("technical_specificity", 0),
                    "Comprehensiveness": criteria.get("comprehensiveness", 0),
                    "Long_term_Vision": criteria.get("long_term_vision", 0),
                    "Gemini_Score": plan_data.get("gemini_score", 0),
                    "GPT4_Score": plan_data.get("gpt4_score", 0),
                    "NA_Reason": "",
                    "LLM_Used": plan_data.get("llm_used", "Multiple"),
                }
                data.append(completed_row)

        # Write CSV
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, na_rep="")

        return output_path

    def create_completion_statistics(
        self, evaluation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create completion statistics for evaluation results.

        Args:
            evaluation_results: Results from the evaluation process

        Returns:
            Dictionary containing completion statistics
        """
        # Handle both "individual_evaluations" and "plans" keys for backward compatibility
        plans = evaluation_results.get("individual_evaluations", {})
        if not plans:
            plans = evaluation_results.get("plans", {})

        resilience_info = evaluation_results.get("resilience_info", {})

        # Count different statuses
        total_plans = len(plans)
        completed_count = 0
        na_count = 0
        failed_count = 0

        for plan_data in plans.values():
            status = plan_data.get("status", "completed")
            if status == "completed":
                completed_count += 1
            elif status == "NA":
                na_count += 1
            elif status == "failed":
                failed_count += 1

        # Calculate completion percentage
        completion_percentage = (
            (completed_count / total_plans * 100) if total_plans > 0 else 0
        )

        # Get LLM availability info
        available_llms = resilience_info.get("available_llms", [])
        unavailable_llms = resilience_info.get("unavailable_llms", [])

        statistics = {
            "total_plans": total_plans,
            "completed_evaluations": completed_count,
            "na_evaluations": na_count,
            "failed_evaluations": failed_count,
            "completion_percentage": round(completion_percentage, 1),
            "available_llms": available_llms,
            "unavailable_llms": unavailable_llms,
            "partial_evaluation": resilience_info.get("partial_evaluation", False),
            "evaluation_timestamp": datetime.now().isoformat(),
        }

        return statistics

    def generate_completion_summary_report(
        self, evaluation_results: Dict[str, Any], output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate a completion summary report with statistics.

        Args:
            evaluation_results: Results from the evaluation process
            output_path: Optional custom output path

        Returns:
            Path to the generated summary report
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"completion_summary_{timestamp}.pdf"

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            story = []

            # Title
            title = Paragraph("Evaluation Completion Summary", self.styles["Title"])
            story.append(title)
            story.append(Spacer(1, 0.5 * inch))

            # Get completion statistics
            stats = self.create_completion_statistics(evaluation_results)

            # Summary section
            story.append(Paragraph("Completion Statistics", self.styles["Heading2"]))
            story.append(Spacer(1, 0.3 * inch))

            # Create statistics table
            stats_data = [
                ["Metric", "Value"],
                ["Total Plans", str(stats["total_plans"])],
                ["Completed Evaluations", str(stats["completed_evaluations"])],
                ["NA Evaluations", str(stats["na_evaluations"])],
                ["Failed Evaluations", str(stats["failed_evaluations"])],
                ["Completion Rate", f"{stats['completion_percentage']}%"],
            ]

            stats_table = Table(stats_data, colWidths=[2 * inch, 1.5 * inch])
            stats_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )

            story.append(stats_table)
            story.append(Spacer(1, 0.3 * inch))

            # LLM Status section
            story.append(Paragraph("LLM Availability Status", self.styles["Heading2"]))
            story.append(Spacer(1, 0.2 * inch))

            available_llms = stats["available_llms"]
            unavailable_llms = stats["unavailable_llms"]

            if available_llms:
                story.append(
                    Paragraph(
                        f"<b>Available LLMs:</b> {', '.join(available_llms)}",
                        self.styles["Normal"],
                    )
                )
            if unavailable_llms:
                story.append(
                    Paragraph(
                        f"<b>Unavailable LLMs:</b> {', '.join(unavailable_llms)}",
                        self.styles["Normal"],
                    )
                )

            story.append(Spacer(1, 0.3 * inch))

            # Evaluation type summary
            if stats["partial_evaluation"]:
                evaluation_type_text = f"""
                <b>Evaluation Type:</b> Partial Evaluation

                This evaluation was completed with reduced LLM availability.
                Some evaluations could not be performed due to LLM connectivity issues.
                The completion rate of {stats['completion_percentage']}% indicates that {stats['completed_evaluations']} out of {stats['total_plans']}
                plans were successfully evaluated.
                """
            else:
                evaluation_type_text = f"""
                <b>Evaluation Type:</b> Complete Evaluation

                All LLMs were available during this evaluation, providing full coverage
                of all planned assessments. The completion rate of {stats['completion_percentage']}% indicates
                successful evaluation of all {stats['total_plans']} plans.
                """

            story.append(Paragraph(evaluation_type_text, self.styles["Normal"]))

            # Build PDF
            doc.build(story)
            return output_path

        except Exception:
            # Fallback to text report
            fallback_path = output_path.with_suffix(".txt")
            stats = self.create_completion_statistics(evaluation_results)

            with open(fallback_path, "w") as f:
                f.write("Evaluation Completion Summary\n")
                f.write("============================\n\n")
                f.write(f"Total Plans: {stats['total_plans']}\n")
                f.write(f"Completed Evaluations: {stats['completed_evaluations']}\n")
                f.write(f"NA Evaluations: {stats['na_evaluations']}\n")
                f.write(f"Failed Evaluations: {stats['failed_evaluations']}\n")
                f.write(f"Completion Rate: {stats['completion_percentage']}%\n")
                f.write(f"Available LLMs: {', '.join(stats['available_llms'])}\n")
                f.write(f"Unavailable LLMs: {', '.join(stats['unavailable_llms'])}\n")

            return fallback_path

    def generate_json_export(
        self, evaluation_results: Dict[str, Any], output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate JSON export of complete evaluation results.

        Args:
            evaluation_results: Results from the evaluation process
            output_path: Optional custom output path

        Returns:
            Path to the generated JSON file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"evaluation_results_{timestamp}.json"

        # Create export data with metadata and resilience information
        # Handle both "individual_evaluations" and "plans" keys for backward compatibility
        plans = evaluation_results.get("individual_evaluations", {})
        if not plans:
            plans = evaluation_results.get("plans", {})

        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "export_type": "evaluation_results",
                "version": "1.0",
                "plans_count": len(plans),
            },
            "evaluation_results": evaluation_results,
        }

        # Add completion statistics if resilience info is available
        if "resilience_info" in evaluation_results:
            completion_stats = self.create_completion_statistics(evaluation_results)
            export_data["completion_statistics"] = completion_stats

        # Write JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)

        return output_path

    # Specialized report generators for different report types
    def _generate_executive_summary(
        self, evaluation_results: Dict[str, Any], output_path: Optional[Path] = None
    ) -> Path:
        """Generate executive summary report."""
        return self.generate_pdf_report(
            evaluation_results, output_path=output_path, report_type="executive"
        )

    def _generate_detailed_analysis(
        self, evaluation_results: Dict[str, Any], output_path: Optional[Path] = None
    ) -> Path:
        """Generate detailed analysis report."""
        return self.generate_pdf_report(
            evaluation_results, output_path=output_path, report_type="detailed"
        )

    def _generate_comparison_analysis(
        self, evaluation_results: Dict[str, Any], output_path: Optional[Path] = None
    ) -> Path:
        """Generate comparison analysis report."""
        return self.generate_pdf_report(
            evaluation_results, output_path=output_path, report_type="comparative"
        )

    def _generate_synthesis_recommendations(
        self, evaluation_results: Dict[str, Any], output_path: Optional[Path] = None
    ) -> Path:
        """Generate synthesis recommendations report."""
        return self.generate_pdf_report(
            evaluation_results, output_path=output_path, report_type="synthesis"
        )

    def generate_complete_report_package(
        self, evaluation_results: Dict[str, Any], output_dir: Optional[Path] = None
    ) -> Dict[str, Path]:
        """
        Generate complete report package with all report types.

        Args:
            evaluation_results: Results from evaluation process
            output_dir: Optional directory for reports

        Returns:
            Dictionary mapping report types to file paths
        """
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = self.output_dir / f"complete_package_{timestamp}"

        output_dir.mkdir(parents=True, exist_ok=True)

        report_paths = {}

        # Generate all report types
        try:
            report_paths["executive"] = self._generate_executive_summary(
                evaluation_results, output_dir / "executive_summary.pdf"
            )
            report_paths["detailed"] = self._generate_detailed_analysis(
                evaluation_results, output_dir / "detailed_analysis.pdf"
            )
            report_paths["comparative"] = self._generate_comparison_analysis(
                evaluation_results, output_dir / "comparison_analysis.pdf"
            )
            report_paths["synthesis"] = self._generate_synthesis_recommendations(
                evaluation_results, output_dir / "synthesis_recommendations.pdf"
            )

            # Generate export files
            report_paths["csv"] = self.generate_csv_export(
                evaluation_results, output_dir / "evaluation_data.csv"
            )
            report_paths["json"] = self.generate_json_export(
                evaluation_results, output_dir / "evaluation_data.json"
            )

        except Exception as e:
            raise Exception(f"Failed to generate complete report package: {e}")

        return report_paths

    def generate_cli_report_package(
        self,
        evaluation_results: Dict[str, Any],
        report_types: List[str],
        output_dir: Path,
        metadata: Dict[str, Any],
    ) -> Dict[str, Path]:
        """
        Generate complete report package for CLI execution.

        Args:
            evaluation_results: Results from evaluation process
            report_types: List of report types to generate
            output_dir: Output directory for reports
            metadata: CLI execution metadata

        Returns:
            Dict mapping report types to generated file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        report_paths = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Generate unified PDF report (replaces three individual PDFs)
            unified_report_path = self.generate_unified_pdf_report(
                evaluation_results, output_dir, metadata
            )
            report_paths["unified_report"] = unified_report_path

            # Always generate data exports
            report_paths["csv"] = self.generate_csv_export(
                evaluation_results, output_dir / f"evaluation_data_{timestamp}.csv"
            )
            report_paths["json"] = self.generate_json_export(
                evaluation_results, output_dir / f"evaluation_data_{timestamp}.json"
            )

        except Exception as e:
            raise Exception(f"Failed to generate CLI report package: {e}")

        return report_paths

    def _add_execution_configuration_section(
        self, story: List, execution_metadata: Dict[str, Any]
    ) -> None:
        """Add execution configuration section to the story."""
        story.append(Paragraph("Execution Configuration", self.styles["Heading2"]))

        config = execution_metadata.get("configuration", {})
        metadata_items = [
            (
                "Execution Time",
                execution_metadata.get("execution_timestamp", "Unknown"),
            ),
            (
                "Duration",
                f"{execution_metadata.get('duration_minutes', 0):.1f} minutes",
            ),
            ("Mode", config.get("execution_mode", "Unknown")),
            (
                "Consensus Enabled",
                "Yes" if config.get("consensus_enabled") else "No",
            ),
            ("Audit Directory", config.get("audit_dir", "Unknown")),
            ("Plans Directory", config.get("plans_dir", "Unknown")),
            ("Output Directory", config.get("output_dir", "Unknown")),
            ("Report Types", config.get("report_types", "Unknown")),
        ]

        for label, value in metadata_items:
            story.append(Paragraph(f"<b>{label}:</b> {value}", self.styles["Normal"]))
            story.append(Spacer(1, 0.1 * inch))

    def _add_file_processing_summary_section(
        self, story: List, execution_metadata: Dict[str, Any]
    ) -> None:
        """Add file processing summary section to the story."""
        story.append(Paragraph("File Processing Summary", self.styles["Heading2"]))

        audit_files = execution_metadata.get("audit_files", [])
        plan_files = execution_metadata.get("plan_files", [])

        story.append(
            Paragraph(
                f"<b>Audit Reports Processed:</b> {len(audit_files)}",
                self.styles["Normal"],
            )
        )
        for file_name in audit_files:
            story.append(Paragraph(f"  • {file_name}", self.styles["Normal"]))

        story.append(Spacer(1, 0.2 * inch))
        story.append(
            Paragraph(
                f"<b>Remediation Plans Processed:</b> {len(plan_files)}",
                self.styles["Normal"],
            )
        )
        for file_name in plan_files:
            story.append(Paragraph(f"  • {file_name}", self.styles["Normal"]))

    def _add_results_summary_section(
        self, story: List, evaluation_results: Dict[str, Any]
    ) -> None:
        """Add results summary section to the story."""
        story.append(Paragraph("Results Summary", self.styles["Heading2"]))

        # Check if we have any evaluation results
        has_results = (
            evaluation_results.get("individual_evaluations")
            and len(evaluation_results["individual_evaluations"]) > 0
        )

        if has_results:
            self._add_successful_results_summary(story, evaluation_results)
        else:
            self._add_no_results_summary(story, evaluation_results)

    def _add_successful_results_summary(
        self, story: List, evaluation_results: Dict[str, Any]
    ) -> None:
        """Add summary for successful evaluations."""
        # Show synthesis plan if available
        if evaluation_results.get("synthesis_plan"):
            synthesis = evaluation_results["synthesis_plan"]
            story.append(
                Paragraph(
                    f"<b>Recommended Plan:</b> {synthesis.get('title', 'Unknown')}",
                    self.styles["Normal"],
                )
            )
            story.append(Spacer(1, 0.1 * inch))

        # Show evaluation count
        story.append(
            Paragraph(
                f"<b>Plans Evaluated:</b> {len(evaluation_results['individual_evaluations'])}",
                self.styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.1 * inch))

        # Show completion statistics if available
        if evaluation_results.get("resilience_stats"):
            stats = evaluation_results["resilience_stats"].get("evaluation_stats", {})
            if stats:
                story.append(
                    Paragraph(
                        f"<b>Successful Evaluations:</b> {stats.get('successful_evaluations', 0)}",
                        self.styles["Normal"],
                    )
                )
                story.append(Spacer(1, 0.1 * inch))

    def _add_no_results_summary(
        self, story: List, evaluation_results: Dict[str, Any]
    ) -> None:
        """Add summary when no evaluation results are available."""
        # No results available - show informative message
        story.append(
            Paragraph(
                "<b>No Evaluation Results Available</b>",
                self.styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.1 * inch))

        # Show what might have happened
        if evaluation_results.get("resilience_stats"):
            stats = evaluation_results["resilience_stats"].get("evaluation_stats", {})
            if stats:
                story.append(
                    Paragraph(
                        f"<b>Evaluation Status:</b> {stats.get('total_evaluations', 0)} total, "
                        f"{stats.get('successful_evaluations', 0)} successful, "
                        f"{stats.get('failed_evaluations', 0)} failed, "
                        f"{stats.get('na_evaluations', 0)} N/A",
                        self.styles["Normal"],
                    )
                )
                story.append(Spacer(1, 0.1 * inch))

        # Show LLM availability status
        if evaluation_results.get("resilience_stats"):
            llm_status = evaluation_results["resilience_stats"].get(
                "llm_availability", {}
            )
            if llm_status:
                available_llms = [llm for llm, status in llm_status.items() if status]
                unavailable_llms = [
                    llm for llm, status in llm_status.items() if not status
                ]

                if available_llms:
                    story.append(
                        Paragraph(
                            f"<b>Available LLMs:</b> {', '.join(available_llms)}",
                            self.styles["Normal"],
                        )
                    )
                    story.append(Spacer(1, 0.1 * inch))

                if unavailable_llms:
                    story.append(
                        Paragraph(
                            f"<b>Unavailable LLMs:</b> {', '.join(unavailable_llms)}",
                            self.styles["Normal"],
                        )
                    )
                    story.append(Spacer(1, 0.1 * inch))

        story.append(
            Paragraph(
                "<i>Note: The evaluation may have failed due to LLM unavailability, "
                "timeout, or other technical issues. Check the logs for more details.</i>",
                self.styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.1 * inch))

    def _add_system_information_section(
        self, story: List, execution_metadata: Dict[str, Any]
    ) -> None:
        """Add system information section to the story."""
        story.append(PageBreak())
        story.append(Paragraph("System Information", self.styles["Heading2"]))

        system_info = execution_metadata.get("system_info", {})
        env_info = execution_metadata.get("environment", {})

        system_items = [
            ("Python Version", system_info.get("python_version", "Unknown")),
            ("Platform", system_info.get("platform", "Unknown")),
            ("Working Directory", system_info.get("cwd", "Unknown")),
            (
                "Google API Configured",
                "Yes" if env_info.get("google_api_configured") else "No",
            ),
            (
                "OpenAI API Configured",
                "Yes" if env_info.get("openai_api_configured") else "No",
            ),
        ]

        for label, value in system_items:
            story.append(Paragraph(f"<b>{label}:</b> {value}", self.styles["Normal"]))
            story.append(Spacer(1, 0.1 * inch))

    def create_execution_summary_report(
        self,
        evaluation_results: Dict[str, Any],
        execution_metadata: Dict[str, Any],
        output_path: Path,
    ) -> Path:
        """
        Create execution summary with CLI arguments and timing.

        Args:
            evaluation_results: Evaluation results
            execution_metadata: CLI execution metadata
            output_path: Path for output file

        Returns:
            Path to generated report
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            story = []

            # Title
            title = Paragraph(
                "Accessibility Evaluation - Execution Summary", self.styles["Title"]
            )
            story.append(title)
            story.append(Spacer(1, 0.5 * inch))

            # Add sections using helper methods
            self._add_execution_configuration_section(story, execution_metadata)
            story.append(PageBreak())
            self._add_file_processing_summary_section(story, execution_metadata)
            story.append(PageBreak())
            self._add_results_summary_section(story, evaluation_results)
            self._add_system_information_section(story, execution_metadata)

            # Build PDF
            doc.build(story)
            return output_path

        except Exception:
            # Fallback to text report
            with open(output_path.with_suffix(".txt"), "w") as f:
                f.write("Execution Summary\n")
                f.write("================\n\n")
                f.write(
                    f"Execution Time: {execution_metadata.get('execution_timestamp', 'Unknown')}\n"
                )
                f.write(
                    f"Duration: {execution_metadata.get('duration_minutes', 0):.1f} minutes\n"
                )
                f.write(
                    f"Files Processed: {len(execution_metadata.get('audit_files', []))} audit reports, {len(execution_metadata.get('plan_files', []))} plans\n"
                )
            return output_path.with_suffix(".txt")

    def _generate_judge_agreement_analysis(
        self, evaluation_results: Dict[str, Any], output_path: Path
    ) -> Path:
        """
        Generate judge agreement analysis report.

        Args:
            evaluation_results: Evaluation results
            output_path: Output file path

        Returns:
            Path to generated report
        """
        return self.generate_pdf_report(
            evaluation_results, output_path=output_path, report_type="judge_agreement"
        )
