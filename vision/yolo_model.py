"""
===========================================================
OES ID Extractor
YOLO Model Wrapper

Author:
    Onyedikachi Nzute

Description
-----------
Provides a centralized wrapper around the Ultralytics
YOLO model used throughout the application.

Responsibilities
----------------
• Load the YOLO model
• Perform inference
• Return detection results
• Manage model lifetime

This module performs no application-specific detection
logic.
===========================================================
"""

from __future__ import annotations

from pathlib import Path

from models.detection import Detection

import numpy as np

from config import config
from utils.logger import get_logger

logger = get_logger(__name__)

#
# ultralytics (and its torch dependency) is a large,
# optional install. If it isn't present, YOLOModel simply
# runs in "unavailable" mode and PhotoDetector falls back
# to its contour-based heuristic instead of crashing the
# whole application.
#
try:

    from ultralytics import YOLO

    _ULTRALYTICS_AVAILABLE = True

except ImportError:

    YOLO = None

    _ULTRALYTICS_AVAILABLE = False


class YOLOModel:
    """
    Singleton wrapper around a YOLO model.
    """

    _model: YOLO | None = None

    _load_attempted: bool = False

    def __init__(self):

        if not YOLOModel._load_attempted:

            YOLOModel._load_attempted = True

            if not _ULTRALYTICS_AVAILABLE:

                logger.warning(
                    "ultralytics is not installed. Photo "
                    "detection will fall back to the "
                    "contour-based heuristic. Run "
                    "'pip install ultralytics' to enable "
                    "YOLO-based detection."
                )

                self.model = None

                self.confidence = getattr(config, "yolo_confidence", 0.35)

                return

            model_path = (
                Path(config.models_dir)
                / "yolo.pt"
            )

            if not model_path.exists():

                #
                # No trained YOLO model has been supplied yet.
                # Rather than crash the whole application, log
                # a clear warning and continue in degraded mode.
                # PhotoDetector falls back to a contour-based
                # heuristic when self.model is None.
                #
                logger.warning(
                    "YOLO model not found at '%s'. Photo "
                    "detection will fall back to the "
                    "contour-based heuristic until a trained "
                    "yolo.pt is placed in the models folder.",
                    model_path,
                )

            else:

                logger.info("Loading YOLO model...")

                YOLOModel._model = YOLO(str(model_path))

                logger.info("YOLO model loaded successfully.")

        self.model = YOLOModel._model

        #
        # Detection confidence.
        #

        self.confidence = getattr(
            config,
            "yolo_confidence",
            0.35,
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def predict(
        self,
        image: np.ndarray,
    ) -> list[Detection]:
        """
        Run inference on an image.

        Returns
        -------
        list[Detection]
            Each detection contains:
                class_id
                class_name
                confidence
                bbox
        """

        if self.model is None:

            logger.debug(
                "YOLO model unavailable; returning no detections."
            )

            return []

        logger.debug(
            "Running YOLO inference."
        )

        result = self.model.predict(
            source=image,
            conf=self.confidence,
            verbose=False,
        )[0]

        detections: list[Detection] = []

        for box in result.boxes:

            class_id = int(box.cls.item())

            class_name = self.model.names[class_id]

            confidence = float(box.conf.item())

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append(
                Detection(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox=(
                        int(x1),
                        int(y1),
                        int(x2 - x1),
                        int(y2 - y1),
                    )
                )
            )

        return detections


    def predict_batch(
        self,
        images: list[np.ndarray],
    ) -> list[list[Detection]]:
        """
        Run inference on multiple images.
        """

        if self.model is None:

            logger.debug(
                "YOLO model unavailable; returning no detections "
                "for batch."
            )

            return [[] for _ in images]

        logger.debug(
            "Running batch inference (%d images).",
            len(images),
        )

        results = self.model.predict(
            source=images,
            conf=self.confidence,
            verbose=False,
        )

        output: list[list[Detection]] = []

        for result in results:

            detections = []

            for box in result.boxes:

                class_id = int(box.cls.item())

                class_name = self.model.names[class_id]

                confidence = float(box.conf.item())

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append(
                    Detection(
                        class_id=class_id,
                        class_name=class_name,
                        confidence=confidence,
                        bbox=(
                            int(x1),
                            int(y1),
                            int(x2 - x1),
                            int(y2 - y1),
                        ),
                    )
                )

            output.append(detections)

        return output
    # --------------------------------------------------
    # Utility
    # --------------------------------------------------

    @property
    def class_names(self) -> dict[int, str]:
        """
        Return the model's class names.
        """

        return self.model.names

    @classmethod
    def unload(cls) -> None:
        """
        Release the shared model.
        """

        if cls._model is not None:

            logger.info(
                "Unloading YOLO model."
            )

            cls._model = None