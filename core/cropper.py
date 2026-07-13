"""
===========================================================
OES ID Extractor
Cropper

Author:
    Onyedikachi Nzute

Description
-----------
Crops the detected personnel photo and signature from the
source document.

Responsibilities
----------------
• Crop personnel photograph
• Crop signature
• Apply configurable padding
• Clamp crop coordinates to image bounds

The Cropper performs no image enhancement or background
removal.
===========================================================
"""

from __future__ import annotations

import cv2
import numpy as np

from config import config
from models.document import Document
from utils.logger import get_logger

logger = get_logger(__name__)


class Cropper:
    """
    Crops detected regions from the source image.
    """

    def __init__(self):

        image_cfg = config.image_settings

        self.photo_padding = image_cfg.get(
            "photo_padding",
            10,
        )

        self.signature_padding = image_cfg.get(
            "signature_padding",
            10,
        )

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(
        self,
        document: Document,
    ) -> Document:
        """
        Crop the detected personnel photo and signature.
        """

        logger.info(
            "Cropping '%s'.",
            document.filename,
        )

        image = document.source_image

        if image is None:

            raise RuntimeError(
                "Document has no source image."
            )

        if document.photo_bbox is not None:

            document.cropped_photo = self._crop(
                image,
                document.photo_bbox,
                self.photo_padding,
            )

        else:

            logger.warning(
                "No personnel photo detected."
            )

        if document.signature_bbox is not None:

            document.cropped_signature = self._crop(
                image,
                document.signature_bbox,
                self.signature_padding,
            )

        else:

            logger.warning(
                "No signature detected."
            )

        return document

    # ------------------------------------------------------
    # Internal
    # ------------------------------------------------------

    def _crop(
        self,
        image: np.ndarray,
        bbox: tuple[int, int, int, int],
        padding: int,
    ) -> np.ndarray:
        """
        Crop a region from an image.

        Parameters
        ----------
        image
            Source image.

        bbox
            Bounding box in (x, y, w, h) format.

        padding
            Number of pixels to extend the crop.
        """

        x, y, w, h = bbox

        height, width = image.shape[:2]

        x1 = max(0, x - padding)
        y1 = max(0, y - padding)

        x2 = min(width, x + w + padding)
        y2 = min(height, y + h + padding)

        crop = image[y1:y2, x1:x2]

        return crop.copy()