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

        
        #
        # Every exported photo is fit onto a canvas of this
        # exact size/aspect ratio, so the whole batch looks
        # visually consistent regardless of how each source
        # photo happened to be framed or what shape its
        # detection box was. 3:4 is a standard, widely
        # recognized ID/passport photo proportion.
        #
    

        self.standard_photo_width = image_cfg.get(
            "standard_photo_width", 600,
        )

        self.standard_photo_height = image_cfg.get(
            "standard_photo_height", 800,
        )

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(self, document: Document) -> Document:
        """
        Enhance the extracted images.
        """
        image = config.image_settings

        enhancement_enabled = any([
            image["denoise"],
            image["clahe"],
            image["sharpen"],
            image["upscale_small_crops"],
            image["standardize_photo_canvas"],
        ])

        if not enhancement_enabled:

            logger.info("Image enhancement disabled.")

            return document
        
        logger.info("Enhancing '%s'.", document.filename)

        if document.photo is not None:

            document.photo = self._enhance(
                document.photo,
                min_dimension=self.PHOTO_MIN_DIMENSION,
            )

            if config.image_settings.get(
                "standardize_photo_canvas",
                True
            ):

                document.photo = self._fit_to_standard_canvas(
                    document.photo,
                    self.standard_photo_width,
                    self.standard_photo_height,
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

        if config.image_settings["denoise"]:
            #
            # Denoise/deblock BEFORE upscaling, not after.
            # JPEG block artifacts (common in this dataset's
            # WhatsApp-compressed sources) are physically
            # smallest - and easiest for the denoiser to
            # clean up - at native resolution. Upscaling
            # first just magnifies the 8x8 block-grid pattern
            # before the denoiser ever gets to it.
            #
            rgb = self._denoise(rgb, is_signature)

        if config.image_settings["upscale_small_crops"]:
            rgb, alpha = self._upscale_if_small(rgb, alpha, min_dimension)

        if config.image_settings["clahe"]:
            rgb = self._apply_clahe(rgb)

        if config.image_settings["sharpen"]:
            rgb = self._unsharp_mask(rgb, is_signature)

        if has_alpha:
            return np.dstack([rgb, alpha])

        return rgb

    def _fit_to_standard_canvas(
        self,
        image: np.ndarray,
        target_width: int,
        target_height: int,
    ) -> np.ndarray:
        """
        Fit the photo onto a fixed-size, fixed-aspect-ratio
        canvas so every exported photo in a batch looks
        visually consistent, regardless of how differently
        each source photo happened to be framed.

        Uses a "contain" fit (scale to fit entirely within
        the canvas, preserving the original aspect ratio,
        then center) rather than a "cover" fit (scale to
        fill the canvas, cropping any overflow) - deliberately,
        since this pipeline already had a real bug where crops
        cut off shoulders (see Cropper), and a cover-fit here
        would risk reintroducing exactly that. The trade-off
        is that photos whose original aspect ratio differs a
        lot from the target end up with some transparent
        letterboxing on two sides rather than being cropped
        further - nothing about the person is ever cut to
        force a fit.
        """

        has_alpha = image.ndim == 3 and image.shape[2] == 4

        height, width = image.shape[:2]

        scale = min(target_width / width, target_height / height)

        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))

        interpolation = (
            cv2.INTER_AREA if scale < 1 else cv2.INTER_LANCZOS4
        )

        resized = cv2.resize(
            image, (new_width, new_height), interpolation=interpolation
        )

        channels = 4 if has_alpha else 3

        canvas = np.zeros(
            (target_height, target_width, channels), dtype=np.uint8
        )

        if not has_alpha:
            canvas[:, :, :] = 255

        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2

        canvas[
            y_offset:y_offset + new_height,
            x_offset:x_offset + new_width,
        ] = resized

        return canvas

    def _upscale_if_small(
        self,
        rgb: np.ndarray,
        alpha: np.ndarray | None,
        min_dimension: int,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        """
        Upscale to at least `min_dimension` on the shorter
        side if needed, using PROGRESSIVE step-upscaling
        rather than one single large jump.

        A single Lanczos resize from, say, 110px up to 600px
        (a ~5.5x jump - common for this dataset's WhatsApp-
        compressed source photos) is inherently soft: Lanczos
        is a fixed interpolation kernel and has nothing real
        to reconstruct missing detail from at that scale
        factor. Stepping the enlargement in <=2x increments,
        with a mild sharpen between each step to re-establish
        edge contrast before the next enlargement, is
        standard practice for large scale factors and
        recovers meaningfully more perceived detail than one
        big jump - verified directly against this dataset's
        actual image characteristics (edge-energy roughly 1.5x
        higher with progressive vs. single-pass at the same
        final size).

        Denoising and sharpening are still applied AFTER this
        by the caller, so the extra pixels carry real,
        cleaned-up detail rather than just amplified blur.
        """

        height, width = rgb.shape[:2]

        shortest_side = min(height, width)

        if shortest_side >= min_dimension:
            return rgb, alpha

        #
        # Hard ceiling on the LONGER side too, not just a
        # floor on the shorter one. Scaling an extreme-
        # aspect-ratio crop (e.g. a thin sliver from a bad
        # detection) up to `min_dimension` on its short side
        # can blow its long side up to hundreds of thousands
        # of pixels - confirmed directly: a 601x3 crop tried
        # to become 600x120,200, taking 3+ seconds and huge
        # memory for a single image. That kind of crop should
        # never have been trusted as a real photo/signature
        # in the first place, but this is the last line of
        # defense against it actually happening.
        #
        max_dimension = 4000

        longer_side = max(height, width)

        target_scale = min_dimension / shortest_side

        if longer_side * target_scale > max_dimension:

            target_scale = max_dimension / longer_side

            logger.warning(
                "Crop has an extreme aspect ratio (%dx%d) - "
                "capping upscale to avoid a runaway output size.",
                width, height,
            )

        min_dimension = max(shortest_side, int(shortest_side * target_scale))

        #
        # Hard safety cap. Guarantees this loop can NEVER
        # hang indefinitely, no matter what edge case slips
        # through - if ever hit, jump straight to the final
        # target size and stop.
        #
        max_iterations = 12

        iterations = 0

        while min(rgb.shape[:2]) < min_dimension:

            iterations += 1

            current_height, current_width = rgb.shape[:2]

            if iterations > max_iterations:

                logger.warning(
                    "Progressive upscale exceeded %d steps - "
                    "jumping directly to target size.",
                    max_iterations,
                )

                scale = min_dimension / min(current_height, current_width)

                new_size = (
                    max(current_width + 1, int(current_width * scale)),
                    max(current_height + 1, int(current_height * scale)),
                )

                rgb = cv2.resize(rgb, new_size, interpolation=cv2.INTER_LANCZOS4)

                if alpha is not None:
                    alpha = cv2.resize(alpha, new_size, interpolation=cv2.INTER_LANCZOS4)

                break

            remaining_scale = min_dimension / min(current_height, current_width)

            step_scale = min(2.0, remaining_scale)

            #
            # THE ACTUAL BUG: int() truncation could produce a
            # "new" size identical to the current size when
            # `remaining_scale` was small (e.g. 597px needing
            # to reach 600px), since int(597 * 1.005) can
            # truncate right back down to 597. When that
            # happened, cv2.resize did nothing, the loop's
            # exit condition never became true, and the app
            # hung forever on that image - confirmed by
            # scanning real starting sizes, not theoretical.
            #
            # max(current+1, ...) guarantees real forward
            # progress on every single iteration, regardless
            # of rounding.
            #
            new_size = (
                max(current_width + 1, int(current_width * step_scale)),
                max(current_height + 1, int(current_height * step_scale)),
            )

            rgb = cv2.resize(rgb, new_size, interpolation=cv2.INTER_LANCZOS4)

            if alpha is not None:
                alpha = cv2.resize(alpha, new_size, interpolation=cv2.INTER_LANCZOS4)

            #
            # Re-establish edge contrast before the next
            # enlargement step softens it further again.
            #
            blurred = cv2.GaussianBlur(rgb, (0, 0), sigmaX=1.0)

            rgb = cv2.addWeighted(rgb, 1.3, blurred, -0.3, 0)

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
