"""
===========================================================
OES ID Extractor
Tesseract OCR Engine

Author:
    Onyedikachi Nzute

Description
-----------
Provides the text-extraction source used by Namer to
determine the personnel's name.

Two extraction strategies are used depending on the
document that was already classified by DocumentAnalyzer:

1. Digital PDF (has an embedded text layer)
   -> reuse the fast, 100% accurate PyMuPDF text layer
      instead of re-OCRing a rendered page.

2. Scanned PDF or plain image
   -> run local Tesseract OCR against the rendered/loaded
      page image.

Responsibilities
----------------
- Decide which extraction strategy a document needs
- Run Tesseract OCR fully offline
- Return raw (uncleaned) text to the caller

This module performs no name parsing (see ocr/parser.py)
and no text cleaning (see ocr/cleaner.py).
===========================================================
"""

from __future__ import annotations

import shutil

import cv2
import numpy as np
import pytesseract

from config import config
from models.document import Document
from pdf.text_detector import PDFTextDetector
from utils.logger import get_logger

logger = get_logger(__name__)


class TesseractOCR:
    """
    Offline OCR engine backed by Tesseract.
    """

    def __init__(self):

        ocr_cfg = config.ocr_settings

        self.enabled = ocr_cfg.get("enabled", True)

        self.language = ocr_cfg.get("language", "eng")

        self.text_detector = PDFTextDetector()

        self._configure_tesseract_binary()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def extract_text(self, document: Document) -> str:
        """
        Extract raw text relevant to personnel-name lookup
        for the given document.
        """

        if not self.enabled:
            logger.info("OCR is disabled in settings.")
            return ""

        try:

            if document.is_pdf and not document.requires_ocr:

                logger.info(
                    "Using embedded PDF text layer for '%s'.",
                    document.filename,
                )

                return self.text_detector.extract_text(document.path)

        except Exception:

            logger.exception(
                "Failed reading embedded PDF text for '%s'; "
                "falling back to OCR.",
                document.filename,
            )

        image = document.source_image

        if image is None:

            logger.warning(
                "No source image available for OCR on '%s'.",
                document.filename,
            )

            return ""

        return self._ocr_image(image)

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    def _configure_tesseract_binary(self) -> None:
        """
        Point pytesseract at a bundled/offline Tesseract
        binary if one is configured, otherwise rely on the
        binary being available on the system PATH.
        """

        custom_path = config.get("tesseract_cmd", None)

        if custom_path:
            pytesseract.pytesseract.tesseract_cmd = custom_path
            return

        if shutil.which("tesseract") is None:

            logger.warning(
                "Tesseract binary not found on PATH. Set "
                "'tesseract_cmd' in settings.json to point "
                "at tesseract.exe for fully offline OCR."
            )

    def _ocr_image(self, image: np.ndarray) -> str:
        """
        Run Tesseract OCR on a single OpenCV image.
        """

        gray = image

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        try:

            text = pytesseract.image_to_string(
                gray,
                lang=self.language,
            )

        except pytesseract.TesseractNotFoundError:

            logger.error(
                "Tesseract is not installed or not on PATH. "
                "OCR cannot run."
            )

            return ""

        except Exception:

            logger.exception("Tesseract OCR failed.")

            return ""

        return text
