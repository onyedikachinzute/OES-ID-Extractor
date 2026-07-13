"""
===========================================================
OES ID Extractor
Document Analyzer

Author:
    Onyedikachi Nzute

Description
-----------
Analyzes supported documents and determines how they
should be processed.

Responsibilities
----------------
• Identify document type
• Determine page count
• Detect scanned vs digital PDFs
• Determine whether OCR is required
• Populate Document metadata

This module performs no extraction.
===========================================================
"""

from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image

from models.document import Document
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentAnalyzer:
    """
    Analyzes documents before processing.
    """

    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff",
    }

    PDF_EXTENSION = ".pdf"

    def analyze(
        self,
        document: Document,
    ) -> Document:
        """
        Analyze a single document.
        """

        logger.info(
            "Analyzing %s",
            document.path.name,
        )

        suffix = document.extension.lower()

        if suffix == self.PDF_EXTENSION:
            self._analyze_pdf(document)

        elif suffix in self.IMAGE_EXTENSIONS:
            self._analyze_image(document)

        else:

            document.status = "Unsupported"

            logger.warning(
                "Unsupported document: %s",
                document.path.name,
            )

        return document

    def analyze_batch(
        self,
        documents: list[Document],
    ) -> list[Document]:

        return [
            self.analyze(doc)
            for doc in documents
        ]

    # --------------------------------------------------
    # PDF
    # --------------------------------------------------

    def _analyze_pdf(
        self,
        document: Document,
    ):

        pdf = fitz.open(document.path)

        try:

            document.document_type = "PDF"

            document.page_count = len(pdf)

            total_text = 0

            for page in pdf:

                total_text += len(
                    page.get_text().strip()
                )

            document.is_scanned = total_text < 50

            document.requires_ocr = (
                document.is_scanned
            )

            document.metadata.update({

                "text_characters": total_text,

                "pages": len(pdf),

            })

            logger.info(

                "PDF (%s) | pages=%d | scanned=%s",

                document.path.name,

                document.page_count,

                document.is_scanned,

            )

        finally:

            pdf.close()

    # --------------------------------------------------
    # IMAGE
    # --------------------------------------------------

    def _analyze_image(
        self,
        document: Document,
    ):

        with Image.open(document.path) as image:

            width, height = image.size

            document.document_type = "Image"

            document.page_count = 1

            document.is_scanned = True

            document.requires_ocr = True

            document.metadata.update({

                "width": width,

                "height": height,

                "mode": image.mode,

                "format": image.format,

            })

            logger.info(

                "Image (%s) | %dx%d",

                document.path.name,

                width,

                height,

            )