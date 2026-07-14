"""
===========================================================
OES ID Extractor
Personnel Photo Detector

Author:
    Onyedikachi Nzute

Description
-----------
Detects the personnel photograph within an ID card,
application form, or scanned document.

Responsibilities
----------------
• Preprocess the image
• Run YOLO inference
• Filter personnel photo detections
• Select the highest-confidence detection
• Return a bounding box in the original image coordinates

This module performs no cropping.
===========================================================
"""

from __future__ import annotations
import numpy as np

from config import config
from models.detection import Detection
from utils.logger import get_logger
from vision.preprocessing import ImagePreprocessor
from vision.yolo_model import YOLOModel

logger = get_logger(__name__)


class PhotoDetector:
    """
    Detects personnel photographs.
    """

    #
    # Accepted YOLO class names.
    #
    # This allows the model to evolve without changing
    # application logic.
    #
    PHOTO_CLASSES = {
        "photo",
    }

    MIN_CONFIDENCE = config.yolo_confidence

    def __init__(self):

        self.preprocessor = ImagePreprocessor()

        self.model = YOLOModel()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def detect(
        self,
        image: np.ndarray,
    ) -> tuple[int, int, int, int] | None:
        """
        Detect the personnel photograph.

        Parameters
        ----------
        image
            OpenCV BGR image, at full/original resolution.

        Returns
        -------
        tuple[int, int, int, int] | None
            Bounding box in (x, y, w, h) format, expressed
            in `image`'s original coordinate space.
        """

        logger.info("Detecting personnel photo.")

        original_height, original_width = image.shape[:2]

        processed = self.preprocessor.prepare(image)

        proc_height, proc_width = processed.shape[:2]

        detections = self.model.predict(processed)

        photos = self._filter_photo_detections(detections)

        if not photos:

            logger.warning("No personnel photo detected by YOLO.")

            return None

        best = max(
            photos,
            key=lambda d: d.confidence,
        )
        
        if best.confidence < self.MIN_CONFIDENCE:
            
            logger.warning(
                "Photo confidence %.2f below threshold %.2f; ignoring.",
                best.confidence,
            )
            
            return None

        logger.info(
            "Personnel photo detected via YOLO (confidence %.2f).",
            best.confidence,
        )

        return self._rescale_bbox(
            best.bbox,
            proc_width,
            proc_height,
            original_width,
            original_height,
        )

    # --------------------------------------------------
    # Internal - YOLO
    # --------------------------------------------------

    def _filter_photo_detections(
        self,
        detections: list[Detection],
    ) -> list[Detection]:
        """
        Keep only detections representing a personnel
        photograph.
        """

        return [
            detection
            for detection in detections
            if detection.class_name.lower() in self.PHOTO_CLASSES
        ]

    def _rescale_bbox(
        self,
        bbox: tuple[int, int, int, int],
        proc_width: int,
        proc_height: int,
        original_width: int,
        original_height: int,
    ) -> tuple[int, int, int, int]:
        """
        YOLO runs against the (possibly downscaled)
        preprocessed image. Rescale its bounding box back
        into the original image's coordinate space so the
        Cropper - which crops from the full-resolution
        source image - crops the correct region.
        """

        scale_x = original_width / proc_width
        scale_y = original_height / proc_height

        x, y, w, h = bbox

        return (
            int(x * scale_x),
            int(y * scale_y),
            int(w * scale_x),
            int(h * scale_y),
        )

