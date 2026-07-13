"""
===========================================================
OES ID Extractor
Namer

Author:
    Onyedikachi Nzute

Description
-----------
Determines the final filename for extracted personnel
assets.

Responsibilities
----------------
• Obtain personnel name from OCR
• Validate extracted name
• Sanitize invalid filename characters
• Generate fallback names
• Ensure unique export names

This module performs no OCR.
===========================================================
"""

from __future__ import annotations

import re
from pathlib import Path

from models.document import Document

from ocr.tesseract import TesseractOCR
from ocr.parser import OCRParser
from utils.logger import get_logger

logger = get_logger(__name__)


class Namer:
    """
    Determines the final export filename.
    """

    INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')

    def __init__(self):

        self.ocr = TesseractOCR()

        self.parser = OCRParser()

        self._used_names: set[str] = set()

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(
        self,
        document: Document,
    ) -> Document:
        """
        Determine the personnel name.
        """

        logger.info(
            "Extracting personnel name from '%s'.",
            document.filename,
        )

        raw_text = self.ocr.extract_text(document)

        candidate = self.parser.parse_name(raw_text)

        if not candidate:

            candidate = document.stem

            logger.warning(
                "OCR could not determine a name. "
                "Using filename '%s'.",
                candidate,
            )

        candidate = self._sanitize(candidate)

        candidate = self._unique(candidate)

        document.extracted_name = candidate

        logger.info(
            "Final filename: %s",
            candidate,
        )

        return document

    # ------------------------------------------------------
    # Internal
    # ------------------------------------------------------

    def _sanitize(
        self,
        name: str,
    ) -> str:
        """
        Remove invalid filename characters.
        """

        name = self.INVALID_CHARS.sub("", name)

        name = " ".join(name.split())

        name = name.strip(" .")

        if not name:

            return "Unknown"

        return name

    def _unique(
        self,
        name: str,
    ) -> str:
        """
        Ensure the generated filename is unique
        within the current processing session.
        """

        if name not in self._used_names:

            self._used_names.add(name)

            return name

        counter = 2

        while True:

            candidate = f"{name}_{counter}"

            if candidate not in self._used_names:

                self._used_names.add(candidate)

                return candidate

            counter += 1

    def reset(self) -> None:
        """
        Clear remembered names.

        Call before beginning a new processing batch.
        """

        self._used_names.clear()