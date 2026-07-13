"""
===========================================================
OES ID Extractor
Enhancer

Author:
    Onyedikachi Nzute

Description
-----------
Enhances extracted personnel photographs and signatures so
they are crisp and print-ready.

Responsibilities
----------------
- Denoise before sharpening (so sharpening amplifies real
  detail, not scan/compression noise)
- Improve local contrast using CLAHE
- Apply a proper Gaussian-based unsharp mask
- Upscale small crops so fine detail survives printing
- Preserve any alpha (transparency) channel produced by
  background removal - critical once a background-removal
  model is installed, otherwise transparency is silently
  discarded here and the "removed" background reappears
- Update the Document with enhanced images

This module performs no detection or background removal.
===========================================================
"""

from __future__ import annotations

import cv2
import numpy as np

from config import config
from models.document import Document
from utils.logger import get_logger

logger = get_logger(__name__)


class Enhancer:
    """
    Enhances extracted images.
    """

    #
    # Crops smaller than these are upscaled before
    # sharpening, so fine detail survives being printed at
    # ID-card size instead of looking pixelated.
    #
    PHOTO_MIN_DIMENSION = 600
    SIGNATURE_MIN_WIDTH = 500

    def __init__(self):

        image_cfg = config.image_settings

        self.enable_clahe = image_cfg.get("clahe", True)

        self.enable_sharpen = image_cfg.get("sharpen", True)

        self.enable_denoise = image_cfg.get("denoise", True)

        self.enable_upscale = image_cfg.get("upscale_small_crops", True)

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(self, document: Document) -> Document:
        """
        Enhance the extracted images.
        """

        logger.info("Enhancing '%s'.", document.filename)

        if document.photo is not None:

            document.photo = self._enhance(
                document.photo,
                min_dimension=self.PHOTO_MIN_DIMENSION,
            )

        if document.signature is not None:

            document.signature = self._enhance(
                document.signature,
                min_dimension=self.SIGNATURE_MIN_WIDTH,
                is_signature=True,
            )

        return document

    # ------------------------------------------------------
    # Internal
    # ------------------------------------------------------

    def _enhance(
        self,
        image: np.ndarray,
        min_dimension: int,
        is_signature: bool = False,
    ) -> np.ndarray:
        """
        Apply the full enhancement pipeline, preserving an
        alpha channel end-to-end if one is present.
        """

        has_alpha = image.ndim == 3 and image.shape[2] == 4

        alpha = None

        if has_alpha:
            alpha = image[:, :, 3]
            rgb = image[:, :, :3]
        else:
            rgb = image

        if self.enable_upscale:
            rgb, alpha = self._upscale_if_small(rgb, alpha, min_dimension)

        if self.enable_denoise:
            rgb = self._denoise(rgb, is_signature)

        if self.enable_clahe:
            rgb = self._apply_clahe(rgb)

        if self.enable_sharpen:
            rgb = self._unsharp_mask(rgb, is_signature)

        if has_alpha:
            return np.dstack([rgb, alpha])

        return rgb

    def _upscale_if_small(
        self,
        rgb: np.ndarray,
        alpha: np.ndarray | None,
        min_dimension: int,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        """
        Upscale using Lanczos interpolation if the crop's
        shorter side is below `min_dimension`. Denoising and
        sharpening are applied AFTER this, so the extra
        pixels carry real, cleaned-up detail rather than
        just amplifying upscale blur.
        """

        height, width = rgb.shape[:2]

        shortest_side = min(height, width)

        if shortest_side >= min_dimension:
            return rgb, alpha

        scale = min_dimension / shortest_side

        new_size = (int(width * scale), int(height * scale))

        rgb = cv2.resize(rgb, new_size, interpolation=cv2.INTER_LANCZOS4)

        if alpha is not None:
            alpha = cv2.resize(alpha, new_size, interpolation=cv2.INTER_LANCZOS4)

        return rgb, alpha

    def _denoise(self, image: np.ndarray, is_signature: bool) -> np.ndarray:
        """
        Remove scan/compression noise BEFORE sharpening, so
        sharpening amplifies real edges instead of noise
        artifacts (a common cause of results that look
        "sharpened" but not actually clearer).
        """

        strength = 5 if is_signature else 7

        return cv2.fastNlMeansDenoisingColored(
            image, None, strength, strength, 7, 21
        )

    def _apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE contrast enhancement on the luminance
        channel only, preserving color.
        """

        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        l = clahe.apply(l)

        lab = cv2.merge((l, a, b))

        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def _unsharp_mask(self, image: np.ndarray, is_signature: bool) -> np.ndarray:
        """
        Classic Gaussian-based unsharp mask:

            sharpened = original + amount * (original - blurred)

        This produces genuinely crisper edges with far less
        ringing/noise than a fixed 3x3 sharpening kernel,
        which amplifies every high-frequency pixel
        (including noise) equally.
        """

        sigma = 1.2 if is_signature else 2.0

        amount = 1.6 if is_signature else 1.3

        blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=sigma)

        sharpened = cv2.addWeighted(
            image, 1 + amount, blurred, -amount, 0
        )

        return sharpened
