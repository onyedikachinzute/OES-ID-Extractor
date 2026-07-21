"""
===========================================================
OES ID Extractor
Handwritten Name Detector

Author:
    Onyedikachi Nzute

Description
-----------
Detects the handwritten personnel name within an ID card.

Responsibilities
----------------
• Preprocess the image
• Run YOLO inference
• Filter handwritten-name detections
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


class NameDetector:
    """
    Detects handwritten personnel names.
    """

    NAME_CLASSES = {
        "name",
    }

    MIN_CONFIDENCE = config.yolo_confidence

    def __init__(self):

        self.preprocessor = ImagePreprocessor()

        self.model = YOLOModel(
            model_name=config.name_detector_model,
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def detect(
        self,
        image: np.ndarray,
    ) -> tuple[int, int, int, int] | None:
        """
        Detect the handwritten personnel name.

        Parameters
        ----------
        image
            OpenCV BGR image.

        Returns
        -------
        tuple[int, int, int, int] | None
            Bounding box in original image coordinates.
        """

        logger.info(
            "Detecting handwritten name."
        )

        original_height, original_width = image.shape[:2]

        processed = self.preprocessor.prepare(image)

        proc_height, proc_width = processed.shape[:2]

        detections = self.model.predict(processed)

        names = self._filter_name_detections(
            detections,
        )

        if not names:

            logger.warning(
                "No handwritten name detected by YOLO."
            )

            return None

        best = max(
            names,
            key=lambda d: d.confidence,
        )

        if best.confidence < self.MIN_CONFIDENCE:

            logger.warning(
                "Name confidence %.2f below threshold %.2f; ignoring.",
                best.confidence,
                self.MIN_CONFIDENCE,
            )

            return None

        logger.info(
            "Handwritten name detected via YOLO (confidence %.2f).",
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
    # Internal
    # --------------------------------------------------

    def _filter_name_detections(
        self,
        detections: list[Detection],
    ) -> list[Detection]:

        return [
            detection
            for detection in detections
            if detection.class_name.lower() in self.NAME_CLASSES
        ]

    def _rescale_bbox(
        self,
        bbox: tuple[int, int, int, int],
        proc_width: int,
        proc_height: int,
        original_width: int,
        original_height: int,
    ) -> tuple[int, int, int, int]:

        scale_x = original_width / proc_width
        scale_y = original_height / proc_height

        x, y, w, h = bbox

        return (
            int(x * scale_x),
            int(y * scale_y),
            int(w * scale_x),
            int(h * scale_y),
        )