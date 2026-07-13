"""
===========================================================
OES ID Extractor
Vision Preprocessing

Author:
    Onyedikachi Nzute

Description
-----------
Provides reusable image preprocessing operations for
computer vision tasks.

Responsibilities
----------------
• Resize images
• Grayscale conversion
• Noise reduction
• Contrast enhancement
• Thresholding
• Morphological operations
• Edge detection

This module performs no object detection.
===========================================================
"""

from __future__ import annotations

import cv2
import numpy as np

from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class ImagePreprocessor:
    """
    Collection of reusable preprocessing methods for
    computer vision.
    """

    def __init__(self):

        self.max_dimension = getattr(
            config,
            "max_processing_dimension",
            1600,
        )

    # --------------------------------------------------
    # General Processing
    # --------------------------------------------------

    def prepare(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Standard preprocessing pipeline.

        Used before running detectors.
        """

        image = self.resize(image)

        return image

    # --------------------------------------------------
    # Resize
    # --------------------------------------------------

    def resize(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Resize while preserving aspect ratio.
        """

        height, width = image.shape[:2]

        longest = max(height, width)

        if longest <= self.max_dimension:

            return image

        scale = self.max_dimension / longest

        new_width = int(width * scale)
        new_height = int(height * scale)

        resized = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA,
        )

        logger.debug(
            "Image resized to %dx%d.",
            new_width,
            new_height,
        )

        return resized

    # --------------------------------------------------
    # Color
    # --------------------------------------------------

    def grayscale(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Convert BGR image to grayscale.
        """

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

    # --------------------------------------------------
    # Noise Reduction
    # --------------------------------------------------

    def denoise(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Reduce image noise.
        """

        if len(image.shape) == 2:

            return cv2.GaussianBlur(
                image,
                (5, 5),
                0,
            )

        return cv2.GaussianBlur(
            image,
            (5, 5),
            0,
        )

    # --------------------------------------------------
    # Contrast Enhancement
    # --------------------------------------------------

    def enhance_contrast(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Apply CLAHE contrast enhancement.
        """

        if len(image.shape) == 2:

            clahe = cv2.createCLAHE(
                clipLimit=2.0,
                tileGridSize=(8, 8),
            )

            return clahe.apply(image)

        lab = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2LAB,
        )

        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8),
        )

        l = clahe.apply(l)

        merged = cv2.merge((l, a, b))

        return cv2.cvtColor(
            merged,
            cv2.COLOR_LAB2BGR,
        )

    # --------------------------------------------------
    # Thresholding
    # --------------------------------------------------

    def adaptive_threshold(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Adaptive threshold for scanned documents.
        """

        gray = image

        if len(image.shape) == 3:

            gray = self.grayscale(image)

        return cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            21,
            10,
        )

    def otsu_threshold(
        self,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Otsu thresholding.
        """

        gray = image

        if len(image.shape) == 3:

            gray = self.grayscale(image)

        _, thresh = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )

        return thresh

    # --------------------------------------------------
    # Morphology
    # --------------------------------------------------

    def morphology(
        self,
        image: np.ndarray,
        operation: int,
        kernel_size: int = 3,
        iterations: int = 1,
    ) -> np.ndarray:
        """
        Apply a morphology operation.
        """

        kernel = np.ones(
            (kernel_size, kernel_size),
            np.uint8,
        )

        return cv2.morphologyEx(
            image,
            operation,
            kernel,
            iterations=iterations,
        )

    # --------------------------------------------------
    # Edge Detection
    # --------------------------------------------------

    def edges(
        self,
        image: np.ndarray,
        low: int = 50,
        high: int = 150,
    ) -> np.ndarray:
        """
        Compute Canny edges.
        """

        gray = image

        if len(image.shape) == 3:

            gray = self.grayscale(image)

        return cv2.Canny(
            gray,
            low,
            high,
        )

    # --------------------------------------------------
    # Utility
    # --------------------------------------------------

    @staticmethod
    def is_grayscale(
        image: np.ndarray,
    ) -> bool:
        """
        Return True if the image is grayscale.
        """

        return len(image.shape) == 2

    @staticmethod
    def copy(
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Return a deep copy of the image.
        """

        return image.copy()