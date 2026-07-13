"""
===========================================================
OES ID Extractor
Contour Detector

Author:
    Onyedikachi Nzute

Description
-----------
Provides contour detection utilities for locating
candidate regions in scanned documents.

Responsibilities
----------------
• Detect contours
• Filter small contours
• Return bounding boxes
• Sort candidate regions

This module performs no signature detection.
===========================================================
"""

from __future__ import annotations

import cv2
import numpy as np

from config import config
from models.detection import Detection
from utils.logger import get_logger

logger = get_logger(__name__)


class ContourDetector:
    """
    Detects candidate contour regions.
    """

    def __init__(self):

        #
        # Ignore tiny blobs.
        #

        self.minimum_area = config.min_contour_area

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def detect(
        self,
        binary_image: np.ndarray,
    ) -> list[Detection]:
        """
        Detect candidate contour regions.

        Parameters
        ----------
        binary_image
            Binary (thresholded) image.

        Returns
        -------
        list[Detection]
        """

        logger.debug(
            "Detecting contours."
        )

        contours, _ = cv2.findContours(
            binary_image,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        detections: list[Detection] = []

        for contour in contours:

            area = cv2.contourArea(contour)

            if area < self.minimum_area:

                continue

            x, y, w, h = cv2.boundingRect(
                contour
            )

            detections.append(
                Detection(
                    class_id=-1,
                    class_name="contour",
                    confidence=1.0,
                    bbox=(x, y, w, h),
                )
            )

        detections.sort(
            key=lambda d: d.area,
            reverse=True,
        )

        logger.debug(
            "%d candidate contour(s) detected.",
            len(detections),
        )

        return detections

    # --------------------------------------------------
    # Utility
    # --------------------------------------------------

    @staticmethod
    def largest(
        detections: list[Detection],
    ) -> Detection | None:
        """
        Return the largest contour.
        """

        if not detections:

            return None

        return max(
            detections,
            key=lambda d: d.area,
        )

    def filter_by_area(
        self,
        detections: list[Detection],
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> list[Detection]:
        """
        Filter detections by area.
        """

        filtered = []

        for detection in detections:
            
            if minimum is None:
                minimum = self.minimum_area

            if detection.area < minimum:

                continue

            if (
                maximum is not None
                and detection.area > maximum
            ):

                continue

            filtered.append(
                detection
            )

        return filtered

    @staticmethod
    def filter_by_aspect_ratio(
        detections: list[Detection],
        minimum: float,
        maximum: float,
    ) -> list[Detection]:
        """
        Filter detections by aspect ratio.

        Aspect ratio = width / height.
        """

        filtered = []

        for detection in detections:

            ratio = (
                detection.width
                / detection.height
            )

            if minimum <= ratio <= maximum:

                filtered.append(
                    detection
                )

        return filtered