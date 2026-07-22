"""
===========================================================
OES ID Extractor
Name Preprocessor

Author:
    Onyedikachi Nzute

Description
-----------
Prepares cropped handwritten-name regions for OCR.

Responsibilities
----------------
• Upscale small crops
• Improve local contrast
• Reduce scan noise
• Sharpen handwriting
• Produce multiple OCR-ready variants

This module performs no OCR.
===========================================================
"""

from __future__ import annotations

import cv2
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


class NamePreprocessor:
    """
    Improves cropped handwritten names before OCR.
    """

    def __init__(self):

        self.min_width = 1200

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def process(
        self,
        image: np.ndarray | None,
    ) -> dict[str, np.ndarray]:
        """
        Produce several OCR-ready versions of the image.

        Returns
        -------
        dict
            {
                "enhanced": image,
                "adaptive": image,
                "binary": image,
                "inverse": image,
            }
        """

        if image is None:

            return {}

        logger.info(
            "Preprocessing handwritten name."
        )

        base = image.copy()

        base = self._upscale(base)

        base = self._add_border(base)

        base = self._grayscale(base)

        base = self._denoise(base)

        base = self._enhance_contrast(base)

        enhanced = self._sharpen(base)

        adaptive = self._adaptive_threshold(base)

        binary = self._otsu_threshold(base)

        inverse = cv2.bitwise_not(binary)
        
        gaussian = cv2.GaussianBlur(
            enhanced,
            (3,3),
            0,
        )
        
        return {
            "enhanced": enhanced,
            "adaptive": adaptive,
            "binary": binary,
            "inverse": inverse,
            "gaussian": gaussian,
        }

    # --------------------------------------------------
    # Processing steps
    # --------------------------------------------------

    def _upscale(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        h, w = image.shape[:2]

        if w >= self.min_width:

            return image

        scale = self.min_width / w

        return cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    def _add_border(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        return cv2.copyMakeBorder(
            image,
            30,
            30,
            30,
            30,
            cv2.BORDER_CONSTANT,
            value=255,
        )

    def _grayscale(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

    def _denoise(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        return cv2.fastNlMeansDenoising(
            image,
            None,
            h=8,
        )

    def _enhance_contrast(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        clahe = cv2.createCLAHE(
            clipLimit=3.5,
            tileGridSize=(8, 8),
        )

        return clahe.apply(image)

    def _sharpen(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        blurred = cv2.GaussianBlur(
            image,
            (0, 0),
            1.2,
        )

        return cv2.addWeighted(
            image,
            1.7,
            blurred,
            -0.7,
            0,
        )

    def _adaptive_threshold(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            12,
        )

    def _otsu_threshold(
        self,
        image: np.ndarray,
    ) -> np.ndarray:

        _, result = cv2.threshold(
            image,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )

        return result