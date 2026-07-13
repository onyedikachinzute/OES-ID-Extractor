"""
===========================================================
OES ID Extractor
PDF Renderer

Author:
    Onyedikachi Nzute

Description
-----------
Renders PDF pages into high-resolution OpenCV images for
downstream computer vision processing.

Responsibilities
----------------
• Render one or more PDF pages
• Convert pages to OpenCV images
• Support configurable rendering DPI
• Handle page rotation
• Return NumPy image arrays

This module performs no OCR or object detection.
===========================================================
"""

from __future__ import annotations

from pathlib import Path

import cv2
import fitz
import numpy as np

from config import config
from pdf.reader import PDFReader
from utils.logger import get_logger

logger = get_logger(__name__)


class PDFRenderer:
    """
    Converts PDF pages into OpenCV images.
    """

    def __init__(self):

        self.reader = PDFReader()

        #
        # Rendering resolution.
        # 300 DPI is an excellent balance between
        # OCR quality and processing speed.
        #

        self.dpi = getattr(
            config,
            "pdf_render_dpi",
            300,
        )

        self.scale = self.dpi / 72.0

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def render(
        self,
        pdf_path: str | Path,
    ) -> list[np.ndarray]:
        """
        Render every page of a PDF.

        Parameters
        ----------
        pdf_path
            Path to the PDF.

        Returns
        -------
        list[np.ndarray]
            Rendered OpenCV images.
        """

        document = self.reader.open(pdf_path)

        try:

            pages = []

            for page in document:

                pages.append(
                    self._render_page(page)
                )

            logger.info(
                "Rendered %d page(s) from '%s'.",
                len(pages),
                Path(pdf_path).name,
            )

            return pages

        finally:

            self.reader.close(document)

    def render_page(
        self,
        pdf_path: str | Path,
        page_number: int,
    ) -> np.ndarray:
        """
        Render a single PDF page.
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

            return self._render_page(
                document.load_page(page_number)
            )

        finally:

            self.reader.close(document)

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    def _render_page(
        self,
        page: fitz.Page,
    ) -> np.ndarray:
        """
        Render a single page to an OpenCV image.
        """

        matrix = fitz.Matrix(
            self.scale,
            self.scale,
        )

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False,
        )

        image = np.frombuffer(
            pixmap.samples,
            dtype=np.uint8,
        )

        image = image.reshape(
            pixmap.height,
            pixmap.width,
            pixmap.n,
        )

        #
        # Convert RGB -> BGR for OpenCV.
        #

        image = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2BGR,
        )

        #
        # Respect page rotation.
        #

        rotation = page.rotation

        if rotation == 90:

            image = cv2.rotate(
                image,
                cv2.ROTATE_90_CLOCKWISE,
            )

        elif rotation == 180:

            image = cv2.rotate(
                image,
                cv2.ROTATE_180,
            )

        elif rotation == 270:

            image = cv2.rotate(
                image,
                cv2.ROTATE_90_COUNTERCLOCKWISE,
            )

        return image