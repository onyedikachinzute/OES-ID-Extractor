"""
===========================================================
OES ID Extractor
Background Remover

Author:
    Onyedikachi Nzute

Description
-----------
Removes the background from cropped personnel photographs
using the trained YOLO segmentation model.

Responsibilities
----------------
• Segment the foreground person
• Convert the segmentation mask into an alpha channel
• Produce an RGBA image
• Leave signatures untouched
===========================================================
"""

from __future__ import annotations

import cv2
import numpy as np

from config import config
from models.document import Document
from utils.logger import get_logger
from vision.segment_model import SegmentModel

logger = get_logger(__name__)


class BackgroundRemover:
    """
    Removes backgrounds from personnel photographs.
    """

    def __init__(self):

        self.segmenter = SegmentModel()

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(
        self,
        document: Document,
    ) -> Document:
        """
        Remove backgrounds from extracted images.
        """

        if not config.background_settings["enabled"]:

            logger.info(
                "Background removal disabled."
            )

            document.photo = document.cropped_photo
            document.signature = document.cropped_signature

            return document

        logger.info(
            "Removing background from '%s'.",
            document.filename,
        )

        #
        # Remove photo background
        #

        document.photo = self._process_photo(
            document.cropped_photo
        )

        #
        # Signatures stay unchanged.
        #

        document.signature = document.cropped_signature

        logger.info(
            "Background removal complete."
        )

        return document

    # ------------------------------------------------------
    # Internal
    # ------------------------------------------------------

    def _process_photo(
        self,
        image: np.ndarray | None,
    ) -> np.ndarray | None:
        """
        Remove the background from a cropped photo.
        """

        if image is None:

            logger.warning(
                "No photo crop available."
            )

            return None

        try:

            alpha = self.segmenter.segment(image)

            if alpha is None:

                logger.warning(
                    "Segmentation returned no mask."
                )

                return image

            return self._apply_alpha(
                image,
                alpha,
            )

        except Exception:

            logger.exception(
                "Background removal failed."
            )

            return image

    def _apply_alpha(
        self,
        image: np.ndarray,
        alpha: np.ndarray,
    ) -> np.ndarray:
        """
        Combine the RGB image with the segmentation mask.
        """

        #
        # Smooth the mask slightly to avoid jagged edges.
        #

        alpha = cv2.GaussianBlur(
            alpha,
            (5, 5),
            0,
        )

        #
        # Ensure uint8.
        #

        alpha = alpha.astype(np.uint8)

        #
        # Create RGBA image.
        #

        rgba = np.dstack(
            (
                image,
                alpha,
            )
        )

        return rgba