"""
===========================================================
OES ID Extractor
Processor

Author:
    Onyedikachi Nzute

Description
-----------
Coordinates the complete document processing workflow.

The Processor acts as the application's orchestrator. It
does not perform any image processing itself. Instead, it
coordinates the analyzer, processing pipeline and exporter
while reporting progress back to the GUI.
===========================================================
"""

from __future__ import annotations

from collections.abc import Callable
from threading import Event

from core.analyzer import DocumentAnalyzer
from core.pipeline import ProcessingPipeline
from models.document import Document
from utils.logger import get_logger

logger = get_logger(__name__)


class Processor:
    """
    Coordinates the complete processing workflow.
    """

    def __init__(
        self,
        progress_callback: Callable[[float], None] | None = None,
        status_callback: Callable[[str], None] | None = None,
        operation_callback: Callable[[str], None] | None = None,
        file_callback: Callable[[int, int], None] | None = None,
    ):

        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.operation_callback = operation_callback
        self.file_callback = file_callback

        self.analyzer = DocumentAnalyzer()
        self.pipeline = ProcessingPipeline()

        self._stop_event = Event()

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(
        self,
        documents: list[Document],
    ) -> None:
        """
        Process a collection of documents.
        """

        total = len(documents)

        if total == 0:
            logger.warning("No documents supplied for processing.")
            return

        self._stop_event.clear()

        logger.info("Starting processing of %d document(s).", total)

        self._set_status("Processing")

        for index, document in enumerate(documents, start=1):

            if self._stop_event.is_set():

                logger.warning("Processing cancelled.")

                self._set_status("Cancelled")

                self._set_operation("Processing cancelled.")

                break

            self._set_operation(
                f"Processing {document.path.name}"
            )

            self._set_file_progress(index, total)

            logger.info(
                "Processing (%d/%d): %s",
                index,
                total,
                document.path.name,
            )

            try:

                analyzed = self.analyzer.analyze(document)

                self.pipeline.process(analyzed)

                analyzed.status = "Completed"

            except Exception:

                analyzed.status = "Failed"

                logger.exception(
                    "Failed to process '%s'.",
                    document.path.name,
                )

            progress = index / total

            self._set_progress(progress)

        else:

            self._set_status("Completed")

            self._set_operation("All documents processed.")

            logger.info("Processing completed.")

    def stop(self) -> None:
        """
        Request cancellation of processing.
        """

        logger.info("Stop requested.")

        self._stop_event.set()

    @property
    def is_running(self) -> bool:
        """
        Returns True while processing is active.
        """

        return not self._stop_event.is_set()

    # ------------------------------------------------------
    # Callback Helpers
    # ------------------------------------------------------

    def _set_progress(
        self,
        value: float,
    ) -> None:

        if self.progress_callback:

            self.progress_callback(value)

    def _set_status(
        self,
        text: str,
    ) -> None:

        if self.status_callback:

            self.status_callback(text)

    def _set_operation(
        self,
        text: str,
    ) -> None:

        if self.operation_callback:

            self.operation_callback(text)

    def _set_file_progress(
        self,
        current: int,
        total: int,
    ) -> None:

        if self.file_callback:

            self.file_callback(current, total)