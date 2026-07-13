"""
===========================================================
OES ID Extractor
OCR Cleaner

Author:
    Onyedikachi Nzute

Description
-----------
Cleans raw OCR/text output before it is handed to the
parser. Tesseract output (and even embedded PDF text) is
frequently noisy: stray symbols, inconsistent whitespace,
and common character misreads.

Responsibilities
----------------
- Normalize whitespace and line breaks
- Strip non-printable / control characters
- Fix a small set of common OCR misreads
- Remove obviously non-textual noise lines

This module performs no name extraction.
===========================================================
"""

from __future__ import annotations

import re
import unicodedata

from utils.logger import get_logger

logger = get_logger(__name__)


class OCRCleaner:
    """
    Cleans raw OCR text.
    """

    #
    # Common single-character OCR misreads seen in printed
    # ID card / form fields. Conservative on purpose - we
    # only fix substitutions that are unambiguous within a
    # word context handled by parser.py, not here.
    #
    _CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")

    _MULTI_SPACE = re.compile(r"[ \t]+")

    _MULTI_BLANK_LINES = re.compile(r"\n{3,}")

    _NOISE_LINE = re.compile(r"^[\W_]+$")

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Full cleaning pipeline for a block of OCR text.
        """

        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text)

        text = cls._CONTROL_CHARS.sub("", text)

        text = text.replace("\r\n", "\n").replace("\r", "\n")

        lines = [cls._clean_line_internal(line) for line in text.split("\n")]

        lines = [line for line in lines if not cls._is_noise_line(line)]

        cleaned = "\n".join(lines)

        cleaned = cls._MULTI_BLANK_LINES.sub("\n\n", cleaned)

        return cleaned.strip()

    @classmethod
    def clean_line(cls, line: str) -> str:
        """
        Clean a single candidate name/line for final use
        (e.g. right before it becomes a filename fragment).
        """

        return cls._clean_line_internal(line)

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    @classmethod
    def _clean_line_internal(cls, line: str) -> str:

        line = cls._MULTI_SPACE.sub(" ", line)

        line = line.strip(" \t.:;,-_|")

        return line

    @classmethod
    def _is_noise_line(cls, line: str) -> bool:

        if not line:
            return True

        if cls._NOISE_LINE.match(line):
            return True

        return False
