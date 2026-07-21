"""
===========================================================
OES ID Extractor
Segmentation Model

Author:
    Onyedikachi Nzute

Description
-----------
Wraps the YOLO segmentation model used to remove the
background from cropped personnel photographs.

Responsibilities
----------------
• Load the segmentation model once
• Run inference
• Return an alpha mask
• Remain completely independent of Document objects
===========================================================
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from config import config
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    from ultralytics import YOLO

    _ULTRALYTICS_AVAILABLE = True

except ImportError:

    YOLO = None

    _ULTRALYTICS_AVAILABLE = False


class SegmentModel:
    """
    Wrapper around the YOLO segmentation model.
    """

    _model: YOLO | None = None

    _load_attempted = False

    def __init__(self):

        if not SegmentModel._load_attempted:

            SegmentModel._load_attempted = True

            self._load_model()

        self.model = SegmentModel._model

    # ------------------------------------------------------
    # Initialization
    # ------------------------------------------------------

    def _load_model(self) -> None:
        """
        Load the trained segmentation model.
        """

        if not _ULTRALYTICS_AVAILABLE:

            logger.warning(
                "Ultralytics is not installed."
            )

            return

        model_path = Path(config.models_dir) / config.segment_model

        if not model_path.exists():

            logger.warning(
                "Segmentation model not found: %s",
                model_path,
            )

            return

        logger.info(
            "Loading segmentation model..."
        )

        SegmentModel._model = YOLO(str(model_path))

        logger.info(
            "Segmentation model loaded successfully."
        )

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def segment(
        self,
        image: np.ndarray,
    ) -> np.ndarray | None:
        """
        Segment the foreground person.

        Returns
        -------
        uint8 alpha mask or None.
        """

        if image is None:

            return None

        if self.model is None:

            logger.warning(
                "Segmentation model unavailable."
            )

            return None

        results = self.model.predict(
            source=image,
            conf=config.segmentation_confidence,
            imgsz=config.segmentation_imgsz,
            device=config.device,
            verbose=False,
        )

        if not results:

            return None

        result = results[0]

        if result.masks is None:

            logger.warning(
                "Segmentation model produced no mask."
            )

            return None

        masks = result.masks.data

        if len(masks) == 0:

            return None

        #
        # Choose the largest mask.
        #

        largest = max(
            masks,
            key=lambda mask: float(mask.sum()),
        )

        alpha = largest.cpu().numpy()

        alpha = cv2.resize(
            alpha,
            (
                image.shape[1],
                image.shape[0],
            ),
            interpolation=cv2.INTER_LINEAR,
        )

        alpha = (alpha * 255).astype(np.uint8)

        return alpha

    # ------------------------------------------------------
    # Utility
    # ------------------------------------------------------

    @classmethod
    def unload(cls) -> None:
        """
        Release the shared model.
        """

        if cls._model is not None:

            logger.info(
                "Unloading segmentation model."
            )

            cls._model = None

            cls._load_attempted = False