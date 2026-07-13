"""
===========================================================
OES ID Extractor
Processing Pipeline

Author:
    Onyedikachi Nzute

Description
-----------
Coordinates the document processing stages.

Each stage has a single responsibility. The pipeline simply
executes them in the correct order and passes the Document
object between them.

Pipeline Order
--------------
1. Detect photo and signature
2. Crop detections
3. Remove backgrounds
4. Enhance extracted images
5. Extract personnel name
6. Export final images
===========================================================
"""

from __future__ import annotations

from models.document import Document

from core.detector import Detector
from core.cropper import Cropper
from core.remover import BackgroundRemover
from core.enhancer import Enhancer
from core.namer import Namer
from core.exporter import Exporter

from utils.logger import get_logger

logger = get_logger(__name__)


class ProcessingPipeline:
    """
    Executes the complete processing pipeline.
    """

    def __init__(self):

        self.detector = Detector()

        self.cropper = Cropper()

        self.remover = BackgroundRemover()

        self.enhancer = Enhancer()

        self.namer = Namer()

        self.exporter = Exporter()

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(
        self,
        document: Document,
    ) -> Document:
        """
        Process a single document through the complete
        extraction pipeline.
        """

        logger.info(
            "Running processing pipeline for '%s'.",
            document.filename,
        )

        document.status = "Processing"

        #
        # Stage 1
        #

        self.detector.process(document)

        #
        # Stage 2
        #

        self.cropper.process(document)

        #
        # Stage 3
        #

        self.remover.process(document)

        #
        # Stage 4
        #

        self.enhancer.process(document)

        #
        # Stage 5
        #

        self.namer.process(document)

        #
        # Stage 6
        #

        self.exporter.process(document)

        document.status = "Completed"

        logger.info(
            "Finished processing '%s'.",
            document.filename,
        )

        return document

    def process_batch(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Process multiple documents sequentially.
        """

        return [
            self.process(document)
            for document in documents
        ]