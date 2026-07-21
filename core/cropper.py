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

        #
        # Photo padding is PROPORTIONAL to the detected box
        # size (not a fixed pixel count - a fixed 10-20px
        # padding is a tiny fraction of a real detection box
        # on any reasonably-sized source image) and
        # ASYMMETRIC: a face/head detection box - even a
        # correctly, tightly drawn one - ends around the
        # chin. Reaching the shoulders/chest for an ID photo
        # requires deliberately extending well below the box,
        # not just adding a uniform margin on all sides.
        #
        self.photo_padding_top_ratio = image_cfg.get(
            "photo_padding_top_ratio", 0.15,
        )

        self.photo_padding_bottom_ratio = image_cfg.get(
            "photo_padding_bottom_ratio", 0.70,
        )

        self.photo_padding_side_ratio = image_cfg.get(
            "photo_padding_side_ratio", 0.30,
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

            document.cropped_photo = self._crop_photo(
                image,
                document.photo_bbox,
            )
            print(document.cropped_photo.shape)

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
            print(document.cropped_signature.shape)

        else:

            logger.warning(
                "No signature detected."
            )

        return document

    # ------------------------------------------------------
    # Internal
    # ------------------------------------------------------

    def _crop_photo(
        self,
        image: np.ndarray,
        bbox: tuple[int, int, int, int],
    ) -> np.ndarray:
        """
        Crop the personnel photo with proportional, asymmetric
        padding around the detected box - extending well
        below it to reach the shoulders/chest, since a face/
        head detection box (from YOLO or any other detector)
        naturally ends around the chin, not the shoulders.
        """

        x, y, w, h = bbox

        height, width = image.shape[:2]

        top_pad = int(h * self.photo_padding_top_ratio)

        bottom_pad = int(h * self.photo_padding_bottom_ratio)

        side_pad = int(w * self.photo_padding_side_ratio)

        x1 = max(0, x - side_pad)
        y1 = max(0, y - top_pad)

        x2 = min(width, x + w + side_pad)
        y2 = min(height, y + h + bottom_pad)

        crop = image[y1:y2, x1:x2]

        return crop.copy()

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
        
        cv2.imwrite("debug_raw_crop.png", crop)
        
        return crop.copy()