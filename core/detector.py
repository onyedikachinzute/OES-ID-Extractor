"""
===========================================================
OES ID Extractor
Detector

Author:
    Onyedikachi Nzute

Description
-----------
Coordinates personnel photo and signature detection.

The Detector does not implement detection algorithms.
Instead, it delegates detection to the vision package and
stores the resulting bounding boxes inside the Document.

Responsibilities
----------------
• Load the source image
• Detect personnel photo
• Detect signature
• Store detection results
===========================================================
"""

from __future__ import annotations

from models.document import Document

from pdf.renderer import PDFRenderer

from vision.photo_detector import PhotoDetector
from vision.signature_detector import SignatureDetector

from utils.file import load_image
from utils.logger import get_logger

logger = get_logger(__name__)


class Detector:
    """
    Coordinates object detection.
    """

    def __init__(self):

        self.pdf_renderer = PDFRenderer()

        self.photo_detector = PhotoDetector()

        self.signature_detector = SignatureDetector()

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(
        self,
        document: Document,
    ) -> Document:
        """
        Detect the personnel photograph and signature.
        """

        logger.info(
            "Detecting objects in '%s'.",
            document.filename,
        )

        #
        # Load source image
        #

        if document.is_pdf:

            pages = self.pdf_renderer.render(document.path)

            if not pages:

                raise RuntimeError(
                    "No pages rendered from PDF."
                )

            #
            # For v1 we process the first page.
            #

            document.source_image = pages[0]

        else:

            document.source_image = load_image(
                document.path
            )

        #
        # Detect personnel photo
        #

        document.photo_bbox = (
            self.photo_detector.detect(
                document.source_image
            )
        )

        #
        # Detect signature
        #

        document.signature_bbox = (
            self.signature_detector.detect(
                document.source_image
            )
        )

        logger.info(
            "Detection complete for '%s'.",
            document.filename,
        )

        return document