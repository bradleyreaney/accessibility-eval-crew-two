"""
Evaluation report generator for creating comprehensive evaluation reports.

This module provides functionality to generate PDF and other format reports
from evaluation results, including scoring summaries, detailed analysis,
and visual representations.

References:
    - Phase 4 Plan: Report generation requirements
    - Master Plan: Output formats and documentation
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

from ...models.evaluation_models import EvaluationInput


class EvaluationReportGenerator:
    """
    Generator for comprehensive evaluation reports.

    Creates formatted reports from evaluation results including:
    - Executive summary
    - Detailed plan analysis
    - Score comparisons
    - Synthesis recommendations
    """

    def __init__(self):
        """Initialize the report generator with default configuration"""
        self.output_dir = Path("output/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()

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

        for item in metadata:
            content.append(Paragraph(item, self.styles["Normal"]))
            content.append(Spacer(1, 0.2 * inch))

        return content

    def _create_executive_summary(self, results: Dict[str, Any]) -> List:
        """Create executive summary section"""
        content = []

        # Section title
        content.append(Paragraph("Executive Summary", self.styles["Heading1"]))
        content.append(Spacer(1, 0.3 * inch))

        # Summary content
        plans = results.get("plans", {})
        if plans:
            # Top scoring plan
            top_plan = max(plans.items(), key=lambda x: x[1].get("overall_score", 0))

            summary_text = f"""
            Based on comprehensive evaluation of {len(plans)} remediation plans,
            <b>{top_plan[0]}</b> achieved the highest overall score of
            <b>{top_plan[1].get('overall_score', 0)}/10</b>.

            The evaluation assessed plans across four key criteria:
            • Strategic Prioritization (40% weight)
            • Technical Specificity (30% weight)
            • Comprehensiveness (20% weight)
            • Long-term Vision (10% weight)
            """

            content.append(Paragraph(summary_text, self.styles["Normal"]))

        content.append(Spacer(1, 0.3 * inch))

        return content

    def _create_scoring_overview(self, results: Dict[str, Any]) -> List:
        """Create scoring overview section with tables"""
        content = []

        # Section title
        content.append(Paragraph("Scoring Overview", self.styles["Heading1"]))
        content.append(Spacer(1, 0.3 * inch))

        plans = results.get("plans", {})
        if plans:
            # Create scoring table
            data = [
                [
                    "Plan",
                    "Overall Score",
                    "Strategic",
                    "Technical",
                    "Comprehensive",
                    "Long-term",
                ]
            ]

            for plan_name, plan_data in plans.items():
                criteria = plan_data.get("criteria_scores", {})
                row = [
                    plan_name,
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
                    1.5 * inch,
                    1 * inch,
                    1 * inch,
                    1 * inch,
                    1.2 * inch,
                    1 * inch,
                ],
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )

            content.append(table)

        content.append(Spacer(1, 0.3 * inch))

        return content

    def _create_detailed_analysis(self, results: Dict[str, Any]) -> List:
        """Create detailed analysis section"""
        content = []

        # Section title
        content.append(Paragraph("Detailed Plan Analysis", self.styles["Heading1"]))
        content.append(Spacer(1, 0.3 * inch))

        plans = results.get("plans", {})
        for plan_name, plan_data in plans.items():
            # Plan title
            content.append(Paragraph(f"Plan: {plan_name}", self.styles["Heading2"]))
            content.append(Spacer(1, 0.2 * inch))

            # Score
            score_text = f"<b>Overall Score:</b> {plan_data.get('overall_score', 0)}/10"
            content.append(Paragraph(score_text, self.styles["Normal"]))
            content.append(Spacer(1, 0.1 * inch))

            # Analysis
            analysis = plan_data.get("analysis", "No detailed analysis available.")
            content.append(
                Paragraph(f"<b>Analysis:</b> {analysis}", self.styles["Normal"])
            )
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

            content.append(Spacer(1, 0.3 * inch))

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

        plans = results.get("plans", {})
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
        plans = evaluation_results.get("plans", {})
        data = []

        for plan_name, plan_data in plans.items():
            criteria = plan_data.get("criteria_scores", {})
            data.append(
                {
                    "Plan": plan_name,
                    "Overall_Score": plan_data.get("overall_score", 0),
                    "Strategic_Prioritization": criteria.get(
                        "strategic_prioritization", 0
                    ),
                    "Technical_Specificity": criteria.get("technical_specificity", 0),
                    "Comprehensiveness": criteria.get("comprehensiveness", 0),
                    "Long_term_Vision": criteria.get("long_term_vision", 0),
                    "Gemini_Score": plan_data.get("gemini_score", 0),
                    "GPT4_Score": plan_data.get("gpt4_score", 0),
                }
            )

        # Write CSV
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)

        return output_path

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

        # Create export data with metadata
        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "export_type": "evaluation_results",
                "version": "1.0",
                "plans_count": len(evaluation_results.get("plans", {})),
            },
            "evaluation_results": evaluation_results,
        }

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
