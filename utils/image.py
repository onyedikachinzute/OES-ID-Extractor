"""
===========================================================
OES ID Extractor
Image Utilities

Author:
    Onyedikachi Nzute

Description
-----------
Small, reusable image conversion helpers shared across the
core, vision and GUI packages (OpenCV <-> Pillow <-> raw
bytes conversions).

This module performs no detection, cropping, or background
removal - see vision/ and core/ for those.
===========================================================
"""

from __future__ import annotations

from io import BytesIO

import cv2
import numpy as np
from PIL import Image


def cv_to_pil(image: np.ndarray) -> Image.Image:
    """
    Convert an OpenCV BGR(A) array to a Pillow image.
    """

    if image.shape[2] == 4:
        return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA))

    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def pil_to_cv(image: Image.Image) -> np.ndarray:
    """
    Convert a Pillow image to an OpenCV BGR(A) array.
    """

    array = np.array(image)

    if image.mode == "RGBA":
        return cv2.cvtColor(array, cv2.COLOR_RGBA2BGRA)

    return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)


def cv_to_png_bytes(image: np.ndarray) -> bytes:
    """
    Encode an OpenCV image as in-memory PNG bytes.
    """

    success, buffer = cv2.imencode(".png", image)

    if not success:
        raise RuntimeError("Failed to encode image as PNG.")

    return buffer.tobytes()


def resize_for_preview(image: np.ndarray, max_dimension: int = 320) -> np.ndarray:
    """
    Downscale an image for lightweight GUI thumbnail
    previews, preserving aspect ratio.
    """

    height, width = image.shape[:2]

    longest = max(height, width)

    if longest <= max_dimension:
        return image

    scale = max_dimension / longest

    return cv2.resize(
        image,
        (int(width * scale), int(height * scale)),
        interpolation=cv2.INTER_AREA,
    )
