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

logger = get_logger(__name__)


class SignatureDetector:
    """
    Detects handwritten signatures using contour heuristics.
    """

    def __init__(self):

        self.preprocessor = ImagePreprocessor()

        self.contour_detector = ContourDetector()

        self.min_aspect_ratio = getattr(
            config,
            "signature_min_aspect_ratio",
            2.0,
        )

        self.max_aspect_ratio = getattr(
            config,
            "signature_max_aspect_ratio",
            12.0,
        )

        #
        # Ignore candidates in the extreme top/bottom of the
        # page - these are almost always scanner artifacts
        # (bed edges, staple/hole-punch marks, dust), not a
        # signature field.
        #
        self.top_margin_ratio = 0.05
        self.bottom_margin_ratio = 0.02

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

        binary = self._binarize(image)

        candidates = self.contour_detector.detect(binary)

        candidates = self.contour_detector.filter_by_aspect_ratio(
            candidates,
            self.min_aspect_ratio,
            self.max_aspect_ratio,
        )

        candidates = self.contour_detector.filter_by_area(candidates)

        if not candidates:
            logger.warning("No signature detected.")
            return None

        best = self._select_best(candidates, image.shape[0])

        logger.info("Signature detected at %s.", best.bbox)

        return best.bbox

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    def _binarize(self, image: np.ndarray) -> np.ndarray:
        """
        Produce a binary image where ink strokes are white
        (foreground) on a black background, with nearby
        strokes merged into a single connected blob so that
        an entire signature is captured as one contour.
        """

        gray = image

        if len(image.shape) == 3:
            gray = self.preprocessor.grayscale(image)

        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        _, binary = cv2.threshold(
            blurred,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )

        #
        # Wide horizontal kernel: joins individual pen
        # strokes/letters of a signature into one blob
        # without merging unrelated page elements.
        #
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))

        merged = cv2.morphologyEx(
            binary,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=2,
        )

        return merged

    def _select_best(
        self,
        candidates: list[Detection],
        image_height: int,
    ) -> Detection:
        """
        Select the signature candidate.

        A signature is virtually always the LAST handwritten
        field on a form - below the name, ID, and other
        fields - so the bottom-most valid candidate is a far
        more reliable signal than the largest one. Area-based
        scoring was previously choosing long lines of cursive
        prose (e.g. a name field) over the actual, often
        shorter, signature scribble simply because they
        covered more pixels.
        """

        top_cutoff = image_height * self.top_margin_ratio
        bottom_cutoff = image_height * (1 - self.bottom_margin_ratio)

        in_bounds = [
            detection
            for detection in candidates
            if top_cutoff <= detection.center[1] <= bottom_cutoff
        ]

        pool = in_bounds if in_bounds else candidates

        #
        # Bottom-most center_y wins; ties broken by area so
        # a larger blob is preferred among near-identical
        # vertical positions.
        #
        return max(
            pool,
            key=lambda detection: (detection.center[1], detection.area),
        )
