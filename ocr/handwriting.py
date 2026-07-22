"""
===========================================================
OES ID Extractor
Handwriting OCR

Author:
    Onyedikachi Nzute

Description
-----------
Recognizes handwritten personnel names using PaddleOCR.

Responsibilities
----------------
• Load PaddleOCR once
• Preprocess cropped handwritten names
• Run OCR on multiple preprocessing variants
• Select the highest-confidence result
• Return recognized text

This module performs no filename generation or
Document manipulation.
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from paddleocr import PaddleOCR

from vision.name_preprocessor import NamePreprocessor
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class OCRResult:
    """
    Result of handwritten OCR.
    """

    text: str
    confidence: float
    variant: str


class HandwritingOCR:
    """
    Singleton wrapper around PaddleOCR.
    """

    _ocr: PaddleOCR | None = None
    _load_attempted = False

    def __init__(self):

        self.preprocessor = NamePreprocessor()

        if not HandwritingOCR._load_attempted:

            HandwritingOCR._load_attempted = True

            logger.info(
                "Loading PaddleOCR..."
            )

            HandwritingOCR._ocr = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang="en",

                text_det_limit_side_len=1536,
                text_det_thresh=0.18,
                text_det_box_thresh=0.35,
            )

            logger.info(
                "PaddleOCR loaded successfully."
            )

        self.ocr = HandwritingOCR._ocr

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def read(
        self,
        image: np.ndarray | None,
    ) -> OCRResult | None:
        """
        Recognize handwriting from a cropped name image.

        Returns
        -------
        OCRResult | None
        """

        if image is None:

            return None

        variants = self.preprocessor.process(image)

        if not variants:

            return None

        best_result: OCRResult | None = None

        for variant_name, variant in variants.items():

            result = self._run_variant(
                variant,
                variant_name,
            )

            if result is None:

                continue

            if (
                best_result is None
                or result.confidence > best_result.confidence
            ):

                best_result = result

        if best_result is None:

            logger.warning(
                "No handwriting recognized."
            )

            return None

        logger.info(
            "Selected '%s' variant (%.3f): %s",
            best_result.variant,
            best_result.confidence,
            best_result.text,
        )

        return best_result

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    def _run_variant(
        self,
        image: np.ndarray,
        variant: str,
    ) -> OCRResult | None:

        #
        # Paddle expects RGB.
        #

        if len(image.shape) == 2:

            rgb = cv2.cvtColor(
                image,
                cv2.COLOR_GRAY2RGB,
            )

        else:

            rgb = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB,
            )

        try:

            output = self.ocr.predict(rgb)

        except Exception:

            logger.exception(
                "OCR failed on '%s' variant.",
                variant,
            )

            return None

        if not output:

            return None

        texts = []
        confidences = []

        #
        # PaddleOCR v3 returns a list of dictionaries.
        #

        for page in output:

            rec_texts = page.get("rec_texts", [])

            rec_scores = page.get("rec_scores", [])

            for text, score in zip(
                rec_texts,
                rec_scores,
            ):

                text = text.strip()
                
                if len(text) < 2:
                    continue

                if not text:

                    continue

                texts.append(text)

                confidences.append(float(score))

        if not texts:

            return None

        final_text = " ".join(texts)

        average_confidence = (
            sum(confidences)
            / len(confidences)
        )

        logger.debug(
            "[%s] %.3f -> %s",
            variant,
            average_confidence,
            final_text,
        )

        return OCRResult(
            text=final_text,
            confidence=average_confidence,
            variant=variant,
        )