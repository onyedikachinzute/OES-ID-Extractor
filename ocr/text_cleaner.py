"""
===========================================================
OES ID Extractor
OCR Text Cleaner

Author:
    Onyedikachi Nzute

Description
-----------
Normalizes OCR output into a clean personnel name.

Responsibilities
----------------
• Remove punctuation
• Remove digits
• Collapse whitespace
• Remove stray symbols
• Convert to title case
• Produce filename-safe text

This module performs no OCR.
===========================================================
"""

from __future__ import annotations

import re

from utils.logger import get_logger

logger = get_logger(__name__)


class OCRTextCleaner:
    """
    Cleans OCR output into a usable personnel name.
    """

    def clean(
        self,
        text: str | None,
    ) -> str | None:
        """
        Clean OCR output.

        Parameters
        ----------
        text
            Raw OCR output.

        Returns
        -------
        str | None
        """

        if not text:

            return None

        logger.debug(
            "Raw OCR text: '%s'",
            text,
        )

        #
        # Remove line breaks.
        #
        text = text.replace("\n", " ")

        #
        # Remove tabs.
        #
        text = text.replace("\t", " ")

        #
        # Remove digits.
        #
        text = re.sub(
            r"\d+",
            "",
            text,
        )

        #
        # Keep only letters, spaces,
        # apostrophes and hyphens.
        #
        text = re.sub(
            r"[^A-Za-z\s'-]",
            "",
            text,
        )

        #
        # Collapse multiple spaces.
        #
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        text = text.strip()

        if not text:

            return None

        #
        # Convert to title case.
        #
        text = text.title()

        logger.debug(
            "Cleaned OCR text: '%s'",
            text,
        )

        return text

    # --------------------------------------------------
    # Filename helper
    # --------------------------------------------------

    def filename(
        self,
        text: str | None,
    ) -> str | None:
        """
        Convert cleaned text into a safe filename.
        """

        cleaned = self.clean(text)

        if cleaned is None:

            return None

        cleaned = cleaned.replace(" ", "_")

        cleaned = cleaned.replace("/", "_")

        cleaned = cleaned.replace("\\", "_")

        cleaned = cleaned.strip("_")

        return cleaned