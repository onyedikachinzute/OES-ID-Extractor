"""
===========================================================
OES ID Extractor
OCR Parser

Author:
    Onyedikachi Nzute

Description
-----------
Parses cleaned OCR text to find the personnel's name.

Responsibilities
----------------
- Search for known name-field labels (NAME, EMPLOYEE NAME,
  STAFF NAME, FULL NAME, SURNAME, etc.)
- Read the value that follows the label, on the same line
  or, if empty, the next line
- Validate that the candidate value actually looks like a
  person's name
- Fall back to a "best guess" line if no label is found

This module performs no OCR and no filename sanitizing
(that is Namer's job).
===========================================================
"""

from __future__ import annotations

import re

from ocr.cleaner import OCRCleaner
from utils.logger import get_logger

logger = get_logger(__name__)


class OCRParser:
    """
    Extracts a personnel name from cleaned OCR/PDF text.
    """

    #
    # Ordered by specificity - more specific labels are
    # checked first so "EMPLOYEE NAME" isn't swallowed by
    # a looser "NAME" match on the same pass.
    #
    LABEL_PATTERNS = [
        re.compile(r"employee\s*name\s*[:\-]?\s*", re.IGNORECASE),
        re.compile(r"staff\s*name\s*[:\-]?\s*", re.IGNORECASE),
        re.compile(r"personnel\s*name\s*[:\-]?\s*", re.IGNORECASE),
        re.compile(r"full\s*name\s*[:\-]?\s*", re.IGNORECASE),
        re.compile(r"surname\s*[:\-]?\s*", re.IGNORECASE),
        re.compile(r"\bname\s*[:\-]?\s*", re.IGNORECASE),
    ]

    #
    # A valid name candidate: letters, spaces, hyphens,
    # apostrophes and periods only, reasonable length.
    #
    NAME_CANDIDATE = re.compile(r"^[A-Za-z][A-Za-z.\-' ]{1,59}$")

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def parse_name(self, raw_text: str) -> str | None:
        """
        Attempt to extract a personnel name from raw text.

        Returns
        -------
        str | None
            The best-guess personnel name, or None if
            nothing usable was found.
        """

        if not raw_text:
            return None

        cleaned = OCRCleaner.clean_text(raw_text)

        if not cleaned:
            return None

        lines = cleaned.split("\n")

        labelled = self._find_labelled_name(lines)

        if labelled:
            logger.info("Name resolved via label: '%s'.", labelled)
            return labelled

        fallback = self._find_fallback_name(lines)

        if fallback:
            logger.info("Name resolved via fallback heuristic: '%s'.", fallback)
            return fallback

        logger.warning("No name candidate found in OCR text.")

        return None

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    def _find_labelled_name(self, lines: list[str]) -> str | None:
        """
        Search each line for a known name label. If the
        label has trailing text on the same line, use it.
        Otherwise fall through to the next non-empty line.
        """

        for pattern in self.LABEL_PATTERNS:

            for index, line in enumerate(lines):

                match = pattern.search(line)

                if not match:
                    continue

                remainder = line[match.end():].strip()

                remainder = OCRCleaner.clean_line(remainder)

                if self._looks_like_name(remainder):
                    return remainder

                #
                # Label found but no value on the same line -
                # check the next non-empty line.
                #
                for next_line in lines[index + 1: index + 3]:

                    candidate = OCRCleaner.clean_line(next_line)

                    if self._looks_like_name(candidate):
                        return candidate

        return None

    def _find_fallback_name(self, lines: list[str]) -> str | None:
        """
        No label was found. Fall back to the first line that
        plausibly looks like "Firstname Lastname".
        """

        for line in lines:

            candidate = OCRCleaner.clean_line(line)

            if not candidate or " " not in candidate:
                continue

            if self._looks_like_name(candidate, strict=True):
                return candidate

        return None

    def _looks_like_name(self, value: str, strict: bool = False) -> bool:

        if not value:
            return False

        if not self.NAME_CANDIDATE.match(value):
            return False

        #
        # Reject single-word all-caps labels/noise like
        # "APPLICATION" or "FORM" that slipped through.
        #
        common_non_names = {
            "name", "date", "form", "signature", "photo",
            "application", "staff", "employee", "department",
            "position", "id", "card",
        }

        if value.strip().lower() in common_non_names:
            return False

        words = [w for w in value.split() if w]

        #
        # Handwritten/cursive OCR frequently produces short
        # garbage fragments (e.g. "a a", "l I"). A label
        # ("Name:") gives us positional confidence even for
        # a short value, but the unlabelled fallback path has
        # no such context, so it must be held to a stricter
        # standard - real names are virtually always at least
        # two words of two-plus letters each.
        #
        if strict:

            if len(words) < 2:
                return False

            if any(len(w.strip(".'-")) < 2 for w in words):
                return False

            if len(value.replace(" ", "")) < 5:
                return False

        return True
