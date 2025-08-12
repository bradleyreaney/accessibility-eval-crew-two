"""
PDF parsing tools for audit reports and remediation plans
References: Master Plan - Data Processing section
"""

import logging
from pathlib import Path
from typing import Dict, Optional

import pdfplumber

from ..models.evaluation_models import DocumentContent

logger = logging.getLogger(__name__)


class PDFParser:
    """
    Handles extraction of text content from PDF files
    Supports both audit reports and remediation plans
    """

    def __init__(self):
        """
        Initialize PDF parser with default configuration.

        Sets up supported formats and file size limits.
        """
        self.supported_formats = [".pdf"]
        self.max_file_size_mb = 50

    def parse_audit_report(self, file_path: Path) -> DocumentContent:
        """
        Parse accessibility audit report PDF
        Returns structured content for evaluation framework
        """
        try:
            self._validate_file(file_path)

            with pdfplumber.open(file_path) as pdf:
                content = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"

                if not content.strip():
                    raise ValueError("No text content extracted from PDF")

                return DocumentContent(
                    title=self._extract_title(content),
                    content=content,
                    page_count=len(pdf.pages),
                    metadata=self._extract_metadata_pdfplumber(pdf),
                )
        except Exception as e:
            logger.error(f"Failed to parse audit report {file_path}: {e}")
            raise ValueError(f"Failed to parse audit report: {e}")

    def parse_remediation_plan(self, file_path: Path) -> DocumentContent:
        """
        Parse remediation plan PDF (Plans A-G)
        Returns structured content for evaluation
        """
        try:
            self._validate_file(file_path)

            with pdfplumber.open(file_path) as pdf:
                content = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"

                if not content.strip():
                    raise ValueError("No text content extracted from PDF")

                # Extract plan name from filename
                plan_name = self._extract_plan_name(file_path.stem)

                return DocumentContent(
                    title=(
                        f"Remediation Plan {plan_name}"
                        if plan_name
                        else self._extract_title(content)
                    ),
                    content=content,
                    page_count=len(pdf.pages),
                    metadata=self._extract_metadata_pdfplumber(pdf),
                )
        except Exception as e:
            logger.error(f"Failed to parse remediation plan {file_path}: {e}")
            raise ValueError(f"Failed to parse remediation plan: {e}")

    def batch_parse_plans(self, plans_directory: Path) -> Dict[str, DocumentContent]:
        """
        Parse all remediation plans in directory
        Returns dictionary with plan names as keys
        """
        plans: Dict[str, DocumentContent] = {}
        plan_files = list(plans_directory.glob("Plan*.pdf"))

        if not plan_files:
            logger.warning(f"No plan files found in {plans_directory}")
            return plans

        for plan_file in plan_files:
            try:
                plan_name = self._extract_plan_name(plan_file.stem)
                if plan_name:
                    plans[plan_name] = self.parse_remediation_plan(plan_file)
                    logger.info(f"Successfully parsed {plan_name}")
            except Exception as e:
                logger.error(f"Failed to parse {plan_file}: {e}")
                continue

        return plans

    def _validate_file(self, file_path: Path) -> None:
        """Validate file exists and is within size limits"""
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if not file_path.suffix.lower() == ".pdf":
            raise ValueError(f"File must be a PDF: {file_path}")

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(
                f"File size ({file_size_mb:.1f}MB) exceeds maximum ({self.max_file_size_mb}MB)"
            )

    def _extract_title(self, content: str) -> str:
        """Extract document title from content"""
        if not content:
            return "Untitled Document"

        lines = content.split("\n")
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                # Skip lines that are likely metadata
                if not any(
                    keyword in line.lower()
                    for keyword in ["page", "date", "version", "draft"]
                ):
                    return line

        return "Untitled Document"

    def _extract_plan_name(self, filename: str) -> Optional[str]:
        """Extract plan name from filename (e.g., 'PlanA' from 'PlanA.pdf')"""
        import re

        match = re.search(r"Plan([A-G])", filename, re.IGNORECASE)
        if match:
            return f"Plan{match.group(1).upper()}"
        return None

    def _extract_metadata_pdfplumber(self, pdf) -> Dict[str, str]:
        """Extract PDF metadata using pdfplumber"""
        metadata = {}
        try:
            if hasattr(pdf, "metadata") and pdf.metadata:
                for key, value in pdf.metadata.items():
                    if value:
                        metadata[key.lower()] = str(value)
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")

        return metadata
