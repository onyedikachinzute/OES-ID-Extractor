"""
===========================================================
OES ID Extractor
Signature Detector

Author:
    Onyedikachi Nzute

Description
-----------
Detects the personnel signature within a scanned document
or form using classical computer-vision heuristics (no
neural network required, so it works fully offline out of
the box even before a YOLO signature class is trained).

Responsibilities
----------------
- Binarize the source image
- Merge signature ink strokes into a single connected blob
- Filter candidate regions by aspect ratio and area
- Prefer regions located toward the lower portion of the
  page (signatures are almost always below the name/photo)
- Return a single bounding box

This module performs no cropping.
===========================================================
"""

from __future__ import annotations

import cv2
import numpy as np

from config import config
from models.detection import Detection
from vision.contour_detector import ContourDetector
from vision.preprocessing import ImagePreprocessor
from utils.logger import get_logger
from vision.yolo_model import YOLOModel

logger = get_logger(__name__)


class SignatureDetector:
    """
    Detects handwritten signatures.
    """

    SIGNATURE_CLASSES = {
        "signature",
    }

    MIN_CONFIDENCE = 0.50

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
        Detect the personnel signature.

        Parameters
        ----------
        image
            OpenCV BGR image.

        Returns
        -------
        tuple[int, int, int, int] | None
            Bounding box in (x, y, w, h) format.
        """

        logger.info("Detecting signature.")

        original_height, original_width = image.shape[:2]

        processed = self.preprocessor.prepare(image)

        proc_height, proc_width = processed.shape[:2]

        detections = self.model.predict(processed)

        signatures = self._filter_signature_detections(detections)

        if not signatures:

            logger.warning("No signature detected by YOLO.")

            return None

        best = max(
            signatures,
            key=lambda d: d.confidence,
        )

        if best.confidence < self.MIN_CONFIDENCE:

            logger.warning(
                "Signature confidence %.2f below threshold %.2f.",
                best.confidence,
                self.MIN_CONFIDENCE,
            )

            return None

        logger.info(
            "Signature detected via YOLO (confidence %.2f).",
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

    def _filter_signature_detections(
        self,
        detections: list[Detection],
    ) -> list[Detection]:
        """
        Keep only signature detections.
        """

        return [
            detection
            for detection in detections
            if detection.class_name.lower() in self.SIGNATURE_CLASSES
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
        Convert the detection from the preprocessed image
        back into the original image coordinate space.
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