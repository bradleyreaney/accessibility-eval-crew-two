"""
File discovery and validation for accessibility evaluation input processing.

This module provides automated discovery and validation of PDF files for
audit reports and remediation plans, replacing the manual file upload
functionality from the Streamlit UI.

References:
    - UI Removal Plan: plans/ui-removal-cli-implementation-plan.md
    - Master Plan: Input processing and validation
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pdfplumber

from ..models.evaluation_models import DocumentContent, EvaluationInput
from ..tools.pdf_parser import PDFParser

logger = logging.getLogger(__name__)


class FileDiscovery:
    """
    Automated discovery and validation of input files for evaluation.

    This class handles the discovery of PDF files in specified directories,
    validates their compatibility, and creates appropriate evaluation input
    structures for processing.
    """

    def __init__(self):
        """Initialize the file discovery system."""
        self.pdf_parser = PDFParser()
        self.supported_extensions = {".pdf"}

    def discover_audit_reports(self, directory: Path) -> List[Path]:
        """
        Find all audit report PDFs in the specified directory.

        Args:
            directory: Path to directory containing audit reports

        Returns:
            List of Path objects for discovered audit report files

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        if not directory.exists():
            raise FileNotFoundError(f"Audit reports directory not found: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Audit reports path is not a directory: {directory}")

        # Find all PDF files
        pdf_files: List[Path] = []
        for ext in self.supported_extensions:
            pdf_files.extend(directory.glob(f"*{ext}"))
            pdf_files.extend(directory.glob(f"*{ext.upper()}"))

        # Filter out hidden files and sort
        pdf_files = [f for f in pdf_files if not f.name.startswith(".")]
        pdf_files.sort()

        logger.debug(f"Discovered {len(pdf_files)} audit report files in {directory}")
        for file in pdf_files:
            logger.debug(f"  - {file.name}")

        return pdf_files

    def discover_remediation_plans(self, directory: Path) -> List[Path]:
        """
        Find all remediation plan PDFs in the specified directory.

        Args:
            directory: Path to directory containing remediation plans

        Returns:
            List of Path objects for discovered remediation plan files

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        if not directory.exists():
            raise FileNotFoundError(
                f"Remediation plans directory not found: {directory}"
            )

        if not directory.is_dir():
            raise ValueError(f"Remediation plans path is not a directory: {directory}")

        # Find all PDF files
        pdf_files: List[Path] = []
        for ext in self.supported_extensions:
            pdf_files.extend(directory.glob(f"*{ext}"))
            pdf_files.extend(directory.glob(f"*{ext.upper()}"))

        # Filter out hidden files and sort
        pdf_files = [f for f in pdf_files if not f.name.startswith(".")]
        pdf_files.sort()

        logger.debug(
            f"Discovered {len(pdf_files)} remediation plan files in {directory}"
        )
        for file in pdf_files:
            logger.debug(f"  - {file.name}")

        return pdf_files

    def validate_file_compatibility(self, files: List[Path]) -> bool:
        """
        Validate that discovered files are processable PDFs.

        Args:
            files: List of file paths to validate

        Returns:
            bool: True if all files are valid, False otherwise
        """
        if not files:
            logger.warning("No files provided for validation")
            return False

        invalid_files = []

        for file_path in files:
            validation_error = self._validate_single_file(file_path)
            if validation_error:
                invalid_files.append(validation_error)

        if invalid_files:
            logger.error("❌ File validation failed:")
            for error in invalid_files:
                logger.error(f"   - {error}")
            return False

        logger.info(f"✅ All {len(files)} files validated successfully")
        return True

    def _validate_single_file(self, file_path: Path) -> Optional[str]:
        """
        Validate a single file for PDF compatibility.

        Args:
            file_path: Path to the file to validate

        Returns:
            Error message if validation fails, None if successful
        """
        try:
            # Check file exists and is readable
            if not file_path.exists():
                return f"{file_path}: File does not exist"

            if not file_path.is_file():
                return f"{file_path}: Not a regular file"

            # Check file size (not empty, not too large)
            file_size = file_path.stat().st_size
            if file_size == 0:
                return f"{file_path}: File is empty"

            if file_size > 100 * 1024 * 1024:  # 100MB limit
                return f"{file_path}: File too large (>100MB)"

            # Try to open as PDF
            try:
                with pdfplumber.open(file_path) as pdf:
                    if len(pdf.pages) == 0:
                        return f"{file_path}: PDF has no pages"

                    # Try to extract some text from first page
                    first_page = pdf.pages[0]
                    text = first_page.extract_text()
                    if not text or len(text.strip()) < 10:
                        logger.warning(
                            f"{file_path}: PDF may contain only images or very little text"
                        )

            except Exception as e:
                return f"{file_path}: Cannot open as PDF - {str(e)}"

            logger.debug(f"✅ {file_path.name}: Valid PDF")
            return None

        except Exception as e:
            return f"{file_path}: Validation error - {str(e)}"

    def create_evaluation_input(
        self, audit_files: List[Path], plan_files: List[Path]
    ) -> EvaluationInput:
        """
        Create EvaluationInput from discovered files.

        Args:
            audit_files: List of audit report file paths
            plan_files: List of remediation plan file paths

        Returns:
            EvaluationInput object ready for processing

        Raises:
            ValueError: If files cannot be processed
            FileNotFoundError: If required files are missing
        """
        if not audit_files:
            raise ValueError("No audit report files provided")

        if not plan_files:
            raise ValueError("No remediation plan files provided")

        logger.info("📄 Processing audit reports...")
        audit_documents = []
        for file_path in audit_files:
            try:
                doc_content = self.pdf_parser.parse_audit_report(file_path)
                audit_documents.append(doc_content)
                logger.info(f"   ✅ Processed: {file_path.name}")
            except Exception as e:
                logger.error(f"   ❌ Failed to process {file_path.name}: {str(e)}")
                raise ValueError(
                    f"Cannot process audit report {file_path.name}: {str(e)}"
                )

        logger.info("📋 Processing remediation plans...")
        plan_documents = {}
        for file_path in plan_files:
            try:
                doc_content = self.pdf_parser.parse_remediation_plan(file_path)
                # Extract plan name from the document title or filename
                plan_name = self._extract_plan_name_from_file(file_path)
                if plan_name:
                    plan_documents[plan_name] = doc_content
                    logger.info(f"   ✅ Processed: {file_path.name} -> {plan_name}")
                else:
                    logger.warning(
                        f"   ⚠️  Could not determine plan name for: {file_path.name}"
                    )
            except Exception as e:
                logger.error(f"   ❌ Failed to process {file_path.name}: {str(e)}")
                raise ValueError(
                    f"Cannot process remediation plan {file_path.name}: {str(e)}"
                )

        # Create evaluation input
        # Note: For now, we'll use the first audit report as the primary one
        # In the future, this could be enhanced to handle multiple audit reports
        primary_audit = audit_documents[0]

        evaluation_input = EvaluationInput(
            audit_report=primary_audit, remediation_plans=plan_documents
        )

        logger.info("✅ Evaluation input created successfully")
        logger.info(f"   📄 Audit report: {primary_audit.title or 'Untitled'}")
        logger.info(f"   📋 Remediation plans: {len(plan_documents)}")

        return evaluation_input

    def _extract_plan_name_from_file(self, file_path: Path) -> Optional[str]:
        """
        Extract plan name from file path.

        Args:
            file_path: Path to the plan file

        Returns:
            Plan name (e.g., 'PlanA') or None if not found
        """
        import re

        # Try to extract from filename
        match = re.search(r"Plan([A-G])", file_path.name, re.IGNORECASE)
        if match:
            return f"Plan{match.group(1).upper()}"

        # If no match, try using the PDF parser's method
        return self.pdf_parser._extract_plan_name(file_path.stem)

    def get_file_summary(self, files: List[Path]) -> Dict[str, Any]:
        """
        Create a summary of discovered files for reporting.

        Args:
            files: List of file paths to summarize

        Returns:
            Dict containing file summary information
        """
        if not files:
            return {"count": 0, "total_size_mb": 0, "files": []}

        file_info = []
        total_size: float = 0.0

        for file_path in files:
            try:
                stat = file_path.stat()
                size_mb = stat.st_size / (1024 * 1024)
                total_size += size_mb

                file_info.append(
                    {
                        "name": file_path.name,
                        "size_mb": round(size_mb, 2),
                        "modified": stat.st_mtime,
                        "path": str(file_path),
                    }
                )
            except Exception as e:
                logger.warning(f"Cannot get stats for {file_path}: {str(e)}")
                file_info.append(
                    {
                        "name": file_path.name,
                        "size_mb": 0,
                        "modified": None,
                        "path": str(file_path),
                        "error": str(e),
                    }
                )

        return {
            "count": len(files),
            "total_size_mb": round(total_size, 2),
            "files": file_info,
        }

    def parse_multiple_documents(self, file_paths: List[Path]) -> List[DocumentContent]:
        """
        Parse multiple PDF documents efficiently.

        Args:
            file_paths: List of PDF file paths to parse

        Returns:
            List of DocumentContent objects

        Raises:
            ValueError: If any files cannot be processed
        """
        documents = []

        for file_path in file_paths:
            try:
                # Determine if it's an audit report or remediation plan based on filename
                if any(
                    keyword in file_path.name.lower() for keyword in ["audit", "report"]
                ):
                    doc_content = self.pdf_parser.parse_audit_report(file_path)
                else:
                    doc_content = self.pdf_parser.parse_remediation_plan(file_path)
                documents.append(doc_content)
                logger.debug(f"Parsed document: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to parse {file_path.name}: {str(e)}")
                raise ValueError(f"Cannot parse document {file_path.name}: {str(e)}")

        return documents

    def create_document_summary(
        self, documents: List[DocumentContent]
    ) -> Dict[str, Any]:
        """
        Create summary of parsed documents for reporting.

        Args:
            documents: List of parsed documents

        Returns:
            Dict containing document summary
        """
        if not documents:
            return {
                "count": 0,
                "total_content_length": 0,
                "total_pages": 0,
                "documents": [],
            }

        total_content_length = 0
        total_pages: float = 0.0
        doc_summaries = []

        for doc in documents:
            content_length = len(doc.content) if doc.content else 0
            page_count = doc.page_count if hasattr(doc, "page_count") else 0

            total_content_length += content_length
            total_pages += page_count

            doc_summaries.append(
                {
                    "title": doc.title or "Untitled",
                    "content_length": content_length,
                    "page_count": page_count,
                    "has_metadata": (
                        bool(doc.metadata) if hasattr(doc, "metadata") else False
                    ),
                }
            )

        return {
            "count": len(documents),
            "total_content_length": total_content_length,
            "total_pages": total_pages,
            "avg_content_length": (
                total_content_length // len(documents) if documents else 0
            ),
            "avg_pages": total_pages // len(documents) if documents else 0,
            "documents": doc_summaries,
        }
