"""
===========================================================
OES ID Extractor
PDF Reader

Author:
    Onyedikachi Nzute

Description
-----------
Provides a centralized interface for opening and
validating PDF documents.

Responsibilities
----------------
• Open PDF documents
• Validate PDF files
• Return page count
• Return document metadata
• Close PDF documents safely

This module performs no rendering or OCR.
===========================================================
"""

from __future__ import annotations

from pathlib import Path

import fitz

from utils.logger import get_logger

logger = get_logger(__name__)


class PDFReader:
    """
    Handles opening and validating PDF documents.
    """

    def open(
        self,
        pdf_path: str | Path,
    ) -> fitz.Document:
        """
        Open a PDF document.

        Parameters
        ----------
        pdf_path
            Path to the PDF file.

        Returns
        -------
        fitz.Document
            Opened PDF document.

        Raises
        ------
        FileNotFoundError
            If the PDF does not exist.

        RuntimeError
            If the PDF cannot be opened.
        """

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():

            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        if pdf_path.suffix.lower() != ".pdf":

            raise ValueError(
                f"Not a PDF file: {pdf_path.name}"
            )

        try:

            document = fitz.open(pdf_path)

            logger.info(
                "Opened PDF '%s' (%d page(s)).",
                pdf_path.name,
                document.page_count,
            )

            return document

        except Exception as exc:

            logger.exception(
                "Failed to open PDF '%s'.",
                pdf_path.name,
            )

            raise RuntimeError(
                f"Unable to open PDF: {pdf_path}"
            ) from exc

    def page_count(
        self,
        document: fitz.Document,
    ) -> int:
        """
        Return the number of pages in a PDF.
        """

        return document.page_count

    def metadata(
        self,
        document: fitz.Document,
    ) -> dict:
        """
        Return PDF metadata.
        """

        return document.metadata

    def is_encrypted(
        self,
        document: fitz.Document,
    ) -> bool:
        """
        Return True if the PDF is encrypted.
        """

        return document.needs_pass

    def close(
        self,
        document: fitz.Document,
    ) -> None:
        """
        Close an opened PDF document.
        """

        if document.is_closed:

            return

        document.close()

        logger.info(
            "Closed PDF document."
        )

    def __enter__(self):
        """
        PDFReader is not intended to be used directly as
        a context manager.
        """

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:

        return None