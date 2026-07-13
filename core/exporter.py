"""
===========================================================
OES ID Extractor
Exporter

Author:
    Onyedikachi Nzute

Description
-----------
Exports the processed personnel photo and signature to
their configured output directories.

Responsibilities
----------------
• Create output directories
• Save photo as PNG
• Save signature as PNG
• Prevent filename collisions
• Update Document export paths
===========================================================
"""

from __future__ import annotations

from pathlib import Path

import cv2

from config import config
from models.document import Document
from utils.logger import get_logger

logger = get_logger(__name__)


class Exporter:
    """
    Saves processed assets to disk.
    """

    def __init__(self):

        self.photo_dir = Path(config.photo_output_dir)
        self.signature_dir = Path(config.signature_output_dir)

        self.photo_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.signature_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(
        self,
        document: Document,
    ) -> Document:
        """
        Export processed images.
        """

        logger.info(
            "Exporting '%s'.",
            document.filename,
        )

        if not document.extracted_name:

            raise RuntimeError(
                "Document has no extracted name."
            )

        if document.photo is not None:

            photo_path = self._unique_path(
                self.photo_dir,
                document.extracted_name,
            )

            self._save_png(
                photo_path,
                document.photo,
            )

            document.photo_output_path = photo_path

        else:

            logger.warning(
                "No personnel photo to export."
            )

        if document.signature is not None:

            signature_path = self._unique_path(
                self.signature_dir,
                document.extracted_name,
            )

            self._save_png(
                signature_path,
                document.signature,
            )

            document.signature_output_path = signature_path

        else:

            logger.warning(
                "No signature to export."
            )

        return document

    # ------------------------------------------------------
    # Internal
    # ------------------------------------------------------

    def _save_png(
        self,
        path: Path,
        image,
    ) -> None:
        """
        Save an image as PNG.
        """

        success = cv2.imwrite(
            str(path),
            image,
        )

        if not success:

            raise RuntimeError(
                f"Failed to save '{path}'."
            )

        logger.info(
            "Saved %s",
            path.name,
        )

    def _unique_path(
        self,
        directory: Path,
        name: str,
    ) -> Path:
        """
        Generate a unique output path.
        """

        candidate = directory / f"{name}.png"

        if not candidate.exists():

            return candidate

        counter = 2

        while True:

            candidate = (
                directory /
                f"{name}_{counter}.png"
            )

            if not candidate.exists():

                return candidate

            counter += 1