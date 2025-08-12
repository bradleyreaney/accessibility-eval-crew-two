"""
Test-Driven Development for PDF parsing functionality
Red-Green-Refactor cycle implementation
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.tools.pdf_parser import DocumentContent, PDFParser


class TestPDFParserTDD:
    """Test-driven development for PDF parser"""

    def test_parser_initialization_creates_supported_formats(self):
        """RED: Test parser initializes with supported formats"""
        parser = PDFParser()
        assert hasattr(parser, "supported_formats")
        assert ".pdf" in parser.supported_formats
        assert parser.max_file_size_mb == 50

    @patch("src.tools.pdf_parser.pdfplumber.open")
    def test_parse_audit_report_extracts_text_content(self, mock_pdf_open):
        """RED: Test text extraction from PDF"""
        # Setup mock
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample audit text content"
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = None
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        # Create parser and test file
        parser = PDFParser()
        test_file = Path("test.pdf")

        # Mock file validation
        with patch.object(parser, "_validate_file"):
            result = parser.parse_audit_report(test_file)

        assert isinstance(result, DocumentContent)
        assert "Sample audit text content" in result.content
        assert result.page_count == 1

    @patch("src.tools.pdf_parser.pdfplumber.open")
    def test_parse_empty_pdf_raises_error(self, mock_pdf_open):
        """RED: Test error handling for empty PDFs"""
        # Setup mock for empty PDF
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        parser = PDFParser()
        test_file = Path("empty.pdf")

        with patch.object(parser, "_validate_file"):
            with pytest.raises(ValueError, match="No text content extracted"):
                parser.parse_audit_report(test_file)

    def test_validate_file_checks_existence(self):
        """RED: Test file validation"""
        parser = PDFParser()
        non_existent_file = Path("nonexistent.pdf")

        with pytest.raises(FileNotFoundError):
            parser._validate_file(non_existent_file)

    def test_validate_file_checks_extension(self):
        """RED: Test file extension validation"""
        parser = PDFParser()

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_size = 1024 * 1024  # 1MB

                wrong_extension = Path("document.txt")
                with pytest.raises(ValueError, match="File must be a PDF"):
                    parser._validate_file(wrong_extension)

    def test_extract_title_from_content(self):
        """Test title extraction logic"""
        parser = PDFParser()

        content_text = (
            "Page 1\nDate: 2025-01-01\n"
            "Accessibility Audit Report\n"
            "This is the main content..."
        )
        title = parser._extract_title(content_text)
        assert title == "Accessibility Audit Report"

    def test_extract_plan_name_from_filename(self):
        """Test plan name extraction"""
        parser = PDFParser()

        assert parser._extract_plan_name("PlanA") == "PlanA"
        assert parser._extract_plan_name("PlanB.pdf") == "PlanB"
        assert parser._extract_plan_name("plana") == "PlanA"
        assert parser._extract_plan_name("random_file") is None

    @patch("src.tools.pdf_parser.pdfplumber.open")
    def test_batch_parse_plans(self, mock_pdf_open):
        """Test batch parsing of multiple plans"""
        # Setup mock
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Plan content"
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = None
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        parser = PDFParser()

        # Mock directory with plan files
        with patch("pathlib.Path.glob") as mock_glob:
            mock_glob.return_value = [Path("PlanA.pdf"), Path("PlanB.pdf")]

            with patch.object(parser, "_validate_file"):
                plans = parser.batch_parse_plans(Path("test_dir"))

        assert "PlanA" in plans
        assert "PlanB" in plans
        assert len(plans) == 2


class TestPDFParserIntegration:
    """Integration tests for PDF parser"""

    @pytest.mark.integration
    def test_parse_real_audit_report(self):
        """Integration test with real audit report if available"""
        parser = PDFParser()
        audit_path = Path("data/audit-reports/AccessibilityReportTOA.pdf")

        if audit_path.exists():
            result = parser.parse_audit_report(audit_path)
            assert isinstance(result, DocumentContent)
            assert len(result.content) > 100
            assert result.page_count > 0
            assert result.title != "Untitled Document"
        else:
            pytest.skip("Real audit report not available")

    @pytest.mark.integration
    def test_parse_real_remediation_plans(self):
        """Integration test with real remediation plans if available"""
        parser = PDFParser()
        plans_dir = Path("data/remediation-plans")

        if plans_dir.exists() and any(plans_dir.glob("Plan*.pdf")):
            plans = parser.batch_parse_plans(plans_dir)
            assert len(plans) > 0

            for plan_name, plan_content in plans.items():
                assert isinstance(plan_content, DocumentContent)
                assert len(plan_content.content) > 0
                assert plan_content.page_count > 0
        else:
            pytest.skip("Real remediation plans not available")

    def test_extract_title_edge_cases(self):
        """Test title extraction edge cases"""
        parser = PDFParser()

        # Test with no clear title - should pick the first meaningful line
        content = "Page 1\nSome random content\nMore content"
        title = parser._extract_title(content)
        assert title in ["Some random content", "Untitled Document"]

        # Test with multiple potential titles
        content = "First Title\nSecond Title\nAccessibility Report\nContent"
        title = parser._extract_title(content)
        assert "Title" in title or "Report" in title

        # Test with empty content
        title = parser._extract_title("")
        assert title == "Untitled Document"

    def test_extract_metadata_error_handling(self):
        """Test metadata extraction error handling"""
        parser = PDFParser()

        # Test with mock PDF object that has no metadata
        class MockPDF:
            metadata = None

        result = parser._extract_metadata_pdfplumber(MockPDF())
        assert isinstance(result, dict)
        # Should have at least some default metadata
        assert len(result) >= 0

    def test_batch_parse_plans_empty_directory(self):
        """Test batch parsing with empty directory"""
        parser = PDFParser()

        # Create a temporary empty directory
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = parser.batch_parse_plans(temp_path)
            assert isinstance(result, dict)
            assert len(result) == 0

    def test_parse_audit_report_file_size_validation(self):
        """Test file size validation"""
        parser = PDFParser()

        # Mock a file that's too large
        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value.st_size = 100 * 1024 * 1024  # 100MB

            with pytest.raises(ValueError, match="exceeds maximum"):
                parser._validate_file(Path("large_file.pdf"))

    def test_parse_remediation_plan_error_handling(self):
        """Test error handling in remediation plan parsing"""
        parser = PDFParser()

        # Mock pdfplumber to raise an exception
        with patch("pdfplumber.open") as mock_open:
            mock_open.side_effect = Exception("PDF parsing failed")

            with pytest.raises(ValueError, match="Failed to parse remediation plan"):
                parser.parse_remediation_plan(Path("test.pdf"))

    def test_batch_parse_plans_with_invalid_files(self):
        """Test batch parsing with mix of valid and invalid files"""
        parser = PDFParser()

        # Mock directory with some files
        with patch("pathlib.Path.glob") as mock_glob:
            mock_files = [Path("PlanA.pdf"), Path("PlanB.pdf")]
            mock_glob.return_value = mock_files

            # Mock one successful parse and one failure
            with patch.object(parser, "parse_remediation_plan") as mock_parse:

                def side_effect(file_path):
                    if "PlanA" in str(file_path):
                        return DocumentContent(
                            title="Plan A",
                            content="Test content",
                            page_count=1,
                            metadata={},
                        )
                    else:
                        raise ValueError("Parse failed")

                mock_parse.side_effect = side_effect

                result = parser.batch_parse_plans(Path("test_dir"))
                assert len(result) == 1  # Only successful parse
                assert "PlanA" in result
