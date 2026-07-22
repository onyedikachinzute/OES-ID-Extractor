"""
===========================================================
OES ID Extractor
Personnel Namer

Author:
    Onyedikachi Nzute

Description
-----------
Extracts the personnel name from a document and determines
the final export filename.

Responsibilities
----------------
• Obtain the cropped handwritten name
• Run handwriting OCR
• Clean OCR output
• Determine the final filename
===========================================================
"""

from __future__ import annotations

from pathlib import Path

from models.document import Document
from ocr.handwriting import HandwritingOCR
from ocr.text_cleaner import OCRTextCleaner
from utils.logger import get_logger

logger = get_logger(__name__)


class Namer:
    """
    Determines the filename for exported assets.
    """

    def __init__(self):

        self.ocr = HandwritingOCR()

        self.cleaner = OCRTextCleaner()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def process(
        self,
        document: Document,
    ) -> None:
        """
        Determine the document's export filename.
        """

        logger.info(
            "Extracting personnel name from '%s'.",
            document.filename,
        )

        #
        # Name crop produced by Cropper.
        #

        crop = document.name_crop

        if crop is None:

            logger.warning(
                "No handwritten name crop available."
            )

            document.personnel_name = None

            document.output_name = (
                Path(document.filename).stem
            )

            return

        #
        # OCR
        #

        result = self.ocr.read(crop)
        
        if result is None:

            logger.warning(
                "Handwriting OCR failed."
            )

            document.personnel_name = None

            document.output_name = (
                Path(document.filename).stem
            )

            return

        if result is None:

            logger.warning(
                "Handwriting OCR failed."
            )

            document.personnel_name = None

            document.output_name = (
                Path(document.filename).stem
            )

            return

        #
        # Clean text.
        #

        cleaned = self.cleaner.clean(
            result.text,
        )
        
        logger.info(
            "Cleaned OCR output: '%s'",
            cleaned,
        )

        if cleaned is None:

            logger.warning(
                "OCR text could not be cleaned."
            )

            document.personnel_name = None

            document.output_name = (
                Path(document.filename).stem
            )

            return

        #
        # Success.
        #

        document.raw_ocr_text = result.text

        document.personnel_name = cleaned

        document.ocr_confidence = result.confidence

        document.ocr_variant = result.variant

        filename = self.cleaner.filename(
            cleaned,
        )

        if filename is None:

            filename = Path(document.filename).stem

        document.output_name = filename

        logger.info(
            "Personnel name: %s",
            document.personnel_name,
        )

        logger.info(
            "OCR confidence: %.3f",
            result.confidence,
        )

        logger.info(
            "OCR variant: %s",
            result.variant,
        )

        logger.info(
            "Final filename: %s",
            document.output_name,
        )
        
        logger.info(
            "Raw OCR output: '%s'",
            result.text,
        )
        
    def reset(self) -> None:
        """
        Reset any cached state.

        Currently Namer is stateless, but this method exists
        for compatibility with the processing pipeline.
        """

        logger.debug(
            "Resetting Namer."
        )