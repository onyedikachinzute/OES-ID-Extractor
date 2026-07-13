"""
===========================================================
OES ID Extractor
Threading Utilities

Author:
    Onyedikachi Nzute

Description
-----------
Runs the (potentially slow) document processing pipeline on
a background thread so the CustomTkinter GUI never freezes
while photos/signatures are being extracted.

All GUI-facing callbacks passed into Processor already
marshal their widget updates back onto the main thread via
`.after(0, ...)`, so this wrapper only needs to worry about:

- Starting the Processor on a daemon background thread
- Reporting unexpected/unhandled exceptions back to the GUI
- Exposing a clean stop() passthrough

This module contains no business/processing logic itself.
===========================================================
"""

from __future__ import annotations

import threading
from collections.abc import Callable

from core.processor import Processor
from models.document import Document
from utils.logger import get_logger

logger = get_logger(__name__)


class ProcessingThread(threading.Thread):
    """
    Runs Processor.process() on a background thread.
    """

    def __init__(
        self,
        processor: Processor,
        documents: list[Document],
        on_error: Callable[[Exception], None] | None = None,
        on_done: Callable[[], None] | None = None,
    ):

        super().__init__(daemon=True)

        self.processor = processor

        self.documents = documents

        self.on_error = on_error

        self.on_done = on_done

    # --------------------------------------------------
    # Thread Entry Point
    # --------------------------------------------------

    def run(self) -> None:

        try:

            logger.info(
                "Background processing thread started (%d document(s)).",
                len(self.documents),
            )

            self.processor.process(self.documents)

        except Exception as exc:  # noqa: BLE001 - report to GUI, not crash

            logger.exception("Unhandled error during batch processing.")

            if self.on_error:
                self.on_error(exc)

        finally:

            logger.info("Background processing thread finished.")

            if self.on_done:
                self.on_done()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def request_stop(self) -> None:
        """
        Ask the underlying Processor to stop after the
        current document finishes.
        """

        self.processor.stop()
