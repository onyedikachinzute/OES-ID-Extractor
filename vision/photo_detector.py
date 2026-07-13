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
- Preprocess the image
- Run YOLO inference (when a trained yolo.pt is available)
- Fall back to a classical rectangle-detection heuristic
  when no YOLO model has been supplied yet
- Filter personnel photo detections
- Select the best detection
- Return a bounding box, always in the ORIGINAL image's
  coordinate space

This module performs no cropping.
===========================================================
"""

from __future__ import annotations

import cv2
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
        "person",
        "portrait",
        "face",
    }

    #
    # Fallback heuristic bounds - a personnel photo is
    # typically portrait/near-square and occupies a modest
    # fraction of the full page.
    #
    FALLBACK_MIN_ASPECT_RATIO = 0.55
    FALLBACK_MAX_ASPECT_RATIO = 1.3
    FALLBACK_MIN_AREA_RATIO = 0.01
    FALLBACK_MAX_AREA_RATIO = 0.30
    FALLBACK_MIN_SOLIDITY = 0.5

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

        if photos:

            #
            # Highest confidence first.
            #
            photos.sort(
                key=lambda d: (d.confidence, d.area),
                reverse=True,
            )

            best = photos[0]

            logger.info(
                "Personnel photo detected via YOLO "
                "(confidence %.2f).",
                best.confidence,
            )

            return self._rescale_bbox(
                best.bbox,
                proc_width,
                proc_height,
                original_width,
                original_height,
            )

        logger.warning(
            "No YOLO photo detection available; "
            "trying contour-based fallback."
        )

        fallback_bbox = self._fallback_detect(image)

        if fallback_bbox is None:

            logger.warning("No personnel photo detected.")

            return None

        logger.info(
            "Personnel photo detected via contour fallback."
        )

        return fallback_bbox

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

    # --------------------------------------------------
    # Internal - Contour Fallback
    # --------------------------------------------------

    def _fallback_detect(
        self,
        image: np.ndarray,
    ) -> tuple[int, int, int, int] | None:
        """
        Classical rectangle-detection heuristic used only
        when no trained YOLO model is available.

        Rather than relying on Canny edges (which need a
        continuous, high-contrast outline and are easily
        broken by a faint/partial photo border), this looks
        for a SOLID block of non-white content:

          1. Threshold everything darker than near-white as
             foreground.
          2. "Open" with a stroke-sized kernel - this erodes
             away thin handwriting/text strokes entirely
             while a photograph (which is densely filled
             throughout) survives.
          3. "Close" to fill in small internal gaps/
             highlights within the photo (skin tones, white
             shirt collars, etc.) so it forms one solid blob.
          4. Keep only blobs that are photo-shaped (aspect
             ratio, size) AND solid (their contour area
             nearly fills their bounding box - text lines
             and stray marks do not).
        """

        height, width = image.shape[:2]

        page_area = float(height * width)

        gray = self.preprocessor.grayscale(image)

        #
        # Foreground = anything meaningfully darker than a
        # near-white page background.
        #
        _, mask = cv2.threshold(
            gray,
            235,
            255,
            cv2.THRESH_BINARY_INV,
        )

        #
        # Kernel sizes scale with image resolution so this
        # behaves consistently whether pages are rendered at
        # 150 DPI or 300+ DPI.
        #
        stroke_kernel_size = max(5, width // 250)

        open_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (stroke_kernel_size, stroke_kernel_size),
        )

        opened = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            open_kernel,
            iterations=1,
        )

        close_kernel_size = max(15, width // 90)

        close_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (close_kernel_size, close_kernel_size),
        )

        closed = cv2.morphologyEx(
            opened,
            cv2.MORPH_CLOSE,
            close_kernel,
            iterations=2,
        )

        contours, _ = cv2.findContours(
            closed,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        best_score = 0.0
        best_bbox = None

        for contour in contours:

            area = cv2.contourArea(contour)
            area_ratio = area / page_area

            if not (
                self.FALLBACK_MIN_AREA_RATIO
                <= area_ratio
                <= self.FALLBACK_MAX_AREA_RATIO
            ):
                continue

            x, y, w, h = cv2.boundingRect(contour)

            if h == 0:
                continue

            aspect_ratio = w / h

            if not (
                self.FALLBACK_MIN_ASPECT_RATIO
                <= aspect_ratio
                <= self.FALLBACK_MAX_ASPECT_RATIO
            ):
                continue

            #
            # Solidity: how much of the bounding box the
            # blob actually fills. A photo fills it almost
            # entirely; leftover text/noise blobs do not.
            #
            solidity = area / float(w * h)

            if solidity < self.FALLBACK_MIN_SOLIDITY:
                continue

            score = area * solidity

            if score > best_score:
                best_score = score
                best_bbox = (x, y, w, h)

        return best_bbox
