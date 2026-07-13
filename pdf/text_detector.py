"""
===========================================================
OES ID Extractor
PDF Text Detector

Author:
    Onyedikachi Nzute

Description
-----------
Detects and extracts embedded text from PDF documents.

Responsibilities
----------------
• Detect whether a PDF contains selectable text
• Extract text from one or more pages
• Estimate whether OCR is required

This module performs no OCR.
===========================================================
"""

from __future__ import annotations

from pathlib import Path

import fitz

from pdf.reader import PDFReader
from utils.logger import get_logger

logger = get_logger(__name__)


class PDFTextDetector:
    """
    Detects embedded text in PDF documents.
    """

    def __init__(self):

        self.reader = PDFReader()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def has_text(
        self,
        pdf_path: str | Path,
    ) -> bool:
        """
        Return True if the PDF contains embedded text.
        """

        document = self.reader.open(pdf_path)

        try:

            for page in document:

                if page.get_text().strip():

                    logger.info(
                        "Embedded text detected in '%s'.",
                        Path(pdf_path).name,
                    )

                    return True

            logger.info(
                "No embedded text found in '%s'.",
                Path(pdf_path).name,
            )

            return False

        finally:

            self.reader.close(document)

    def extract_text(
        self,
        pdf_path: str | Path,
    ) -> str:
        """
        Extract all embedded text from the PDF.
        """

        document = self.reader.open(pdf_path)

        try:

            text_parts: list[str] = []

            for page in document:

                text = page.get_text()

                if text:

                    text_parts.append(text)

            text = "\n".join(text_parts).strip()

            logger.info(
                "Extracted %d characters from '%s'.",
                len(text),
                Path(pdf_path).name,
            )

            return text

        finally:

            self.reader.close(document)

    def page_text(
        self,
        pdf_path: str | Path,
        page_number: int,
    ) -> str:
        """
        Extract text from a single page.
        """

        document = self.reader.open(pdf_path)

        try:

            if (
                page_number < 0
                or page_number >= document.page_count
            ):

                raise IndexError(
                    "Page index out of range."
                )

            page = document.load_page(page_number)

            return page.get_text().strip()

        finally:

            self.reader.close(document)

    def requires_ocr(
        self,
        pdf_path: str | Path,
    ) -> bool:
        """
        Determine whether OCR is likely required.

        Returns
        -------
        bool
            True if no embedded text is detected.
        """

        return not self.has_text(pdf_path)