"""
Pydantic models for PDF report generation
References: Master Plan - PDF Report Integration
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ReportType(str, Enum):
    """Enumeration of available report types for evaluation output"""

    INDIVIDUAL_EVALUATION = "individual_evaluation"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    SYNTHESIS_REPORT = "synthesis_report"
    EXECUTIVE_SUMMARY = "executive_summary"


class ChartConfig(BaseModel):
    """Configuration for charts in reports"""

    chart_type: str = Field(..., description="Type of chart (bar, radar, pie)")
    title: str = Field(..., description="Chart title")
    data: Dict[str, Any] = Field(..., description="Chart data")
    width: int = Field(default=800, description="Chart width in pixels")
    height: int = Field(default=600, description="Chart height in pixels")


class ReportSection(BaseModel):
    """Individual section of a report"""

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content (HTML/Markdown)")
    charts: List[ChartConfig] = Field(default=[], description="Charts in this section")
    subsections: List["ReportSection"] = Field(
        default=[], description="Nested subsections"
    )


class ReportMetadata(BaseModel):
    """Metadata for generated reports"""

    report_id: str = Field(..., description="Unique report identifier")
    report_type: ReportType = Field(..., description="Type of report")
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str = Field(default="LLM as a Judge System")
    version: str = Field(default="1.0")
    audit_report_name: str = Field(..., description="Source audit report")
    plans_evaluated: List[str] = Field(..., description="List of plans evaluated")


class PDFReportConfig(BaseModel):
    """Configuration for PDF report generation"""

    template_name: str = Field(..., description="Template to use")
    include_charts: bool = Field(default=True)
    include_raw_data: bool = Field(default=False)
    page_size: str = Field(default="A4")
    margins: Dict[str, str] = Field(
        default={"top": "2cm", "bottom": "2cm", "left": "2cm", "right": "2cm"}
    )
    font_family: str = Field(default="Arial")
    include_cover_page: bool = Field(default=True)
    include_table_of_contents: bool = Field(default=True)


class EvaluationReport(BaseModel):
    """Complete evaluation report structure"""

    metadata: ReportMetadata
    config: PDFReportConfig
    executive_summary: ReportSection
    methodology: ReportSection
    individual_evaluations: List[ReportSection]
    comparative_analysis: ReportSection
    synthesis_recommendations: ReportSection
    appendices: List[ReportSection] = Field(default=[])

    def to_html(self) -> str:
        """Convert report to HTML for PDF generation"""
        # Implementation will be added in GREEN phase
        return "<html><body>Report content placeholder</body></html>"

    def to_pdf_bytes(self) -> bytes:
        """Generate PDF bytes from report"""
        # Implementation will be added in GREEN phase
        return b"PDF content placeholder"


# Enable self-referencing models
ReportSection.model_rebuild()
