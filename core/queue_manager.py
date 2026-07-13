"""
===========================================================
OES ID Extractor
Queue Manager

Author:
    Onyedikachi Nzute

Description
-----------
Manages the document processing queue.

Responsibilities
----------------
• Store documents awaiting processing
• Return documents in FIFO order
• Prevent duplicate queue entries
• Report queue statistics
• Clear the queue
===========================================================
"""

from __future__ import annotations

from collections import deque

from models.document import Document
from utils.logger import get_logger

logger = get_logger(__name__)


class QueueManager:
    """
    FIFO queue for document processing.
    """

    def __init__(self):

        self._queue: deque[Document] = deque()

        self._queued_paths: set[str] = set()

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def add(self, document: Document) -> bool:
        """
        Add a document to the queue.

        Returns
        -------
        bool
            True if added.
            False if already present.
        """

        key = str(document.path.resolve())

        if key in self._queued_paths:

            logger.debug(
                "Document already queued: %s",
                document.filename,
            )

            return False

        self._queue.append(document)

        self._queued_paths.add(key)

        logger.info(
            "Queued '%s'.",
            document.filename,
        )

        return True

    def add_many(
        self,
        documents: list[Document],
    ) -> int:
        """
        Queue multiple documents.

        Returns
        -------
        int
            Number of documents successfully added.
        """

        added = 0

        for document in documents:

            if self.add(document):

                added += 1

        logger.info(
            "Added %d document(s) to queue.",
            added,
        )

        return added

    def get(self) -> Document | None:
        """
        Retrieve the next document.

        Returns None if the queue is empty.
        """

        if self.is_empty:

            return None

        document = self._queue.popleft()

        self._queued_paths.discard(
            str(document.path.resolve())
        )

        logger.debug(
            "Dequeued '%s'.",
            document.filename,
        )

        return document

    def peek(self) -> Document | None:
        """
        View the next document without removing it.
        """

        if self.is_empty:

            return None

        return self._queue[0]

    def clear(self) -> None:
        """
        Remove all queued documents.
        """

        count = len(self._queue)

        self._queue.clear()

        self._queued_paths.clear()

        logger.info(
            "Cleared queue (%d document(s)).",
            count,
        )

    def remove(
        self,
        document: Document,
    ) -> bool:
        """
        Remove a specific document.

        Returns
        -------
        bool
            True if removed.
        """

        try:

            self._queue.remove(document)

            self._queued_paths.discard(
                str(document.path.resolve())
            )

            logger.info(
                "Removed '%s' from queue.",
                document.filename,
            )

            return True

        except ValueError:

            return False

    # ------------------------------------------------------
    # Properties
    # ------------------------------------------------------

    @property
    def size(self) -> int:
        """
        Number of queued documents.
        """

        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        """
        Returns True if queue is empty.
        """

        return len(self._queue) == 0

    # ------------------------------------------------------
    # Special Methods
    # ------------------------------------------------------

    def __len__(self):

        return len(self._queue)

    def __iter__(self):

        return iter(self._queue)

    def __bool__(self):

        return not self.is_empty