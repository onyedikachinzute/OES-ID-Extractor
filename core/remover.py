"""
===========================================================
OES ID Extractor
Background Remover

Author:
    Onyedikachi Nzute

Description
-----------
Removes backgrounds from extracted personnel photos and
signatures, entirely with classical (non-ML) computer
vision. Fully offline out of the box - no model file to
download, nothing to install beyond OpenCV/NumPy/Pillow.

Why not rembg/U2Net (history)
------------------------------
An earlier version of this module routed both photo and
signature crops through rembg's U2Net model. Two real,
repeated failures came out of that:

  - Signatures: U2Net is trained for whole-object
    photographic saliency segmentation. Run on a 1-3px pen
    stroke, nearly every pixel sits at a matte "edge" as far
    as the model is concerned, producing visible embossed/
    beveled halo artifacts.

  - Photos: U2Net gave low-to-zero confidence on the
    low-contrast pale shirt against white paper, sometimes
    with literally zero signal (not just "low"), scattered
    into fragments disconnected from the face. No amount of
    patching the confidence map recovered it reliably.

ID/passport-style photos and ink signatures both have a
much simpler, more exploitable structure than an arbitrary
photograph: a plain, roughly uniform backdrop that only ever
touches the image border (photos), or dark ink on light
paper (signatures). Classical techniques suited to exactly
that structure - border flood-fill for photos, a darkness
threshold for signatures - turned out to be both more
reliable AND simpler than the ML approach for this specific,
narrow use case.

Responsibilities
----------------
- Remove the backdrop from a personnel photo via border
  flood-fill, keeping the full person (head, neck,
  shoulders, torso) opaque regardless of low-contrast
  clothing
- Remove the background from a signature via an ink-darkness
  threshold
- Update the Document with background-removed images
===========================================================
"""

from __future__ import annotations

import cv2
import numpy as np

from models.document import Document
from utils.logger import get_logger

logger = get_logger(__name__)


class BackgroundRemover:
    """
    Removes backgrounds from extracted images using
    classical (non-ML) computer vision.
    """

    def __init__(self):
        pass

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def process(self, document: Document) -> Document:
        """
        Remove backgrounds from all extracted images.
        """

        logger.info(
            "Removing backgrounds from '%s'.",
            document.filename,
        )

        document.photo = self._process_photo(document.cropped_photo)

        document.signature = self._process_signature(document.cropped_signature)

        return document

    # ------------------------------------------------------
    # Internal - Photo (border flood-fill)
    # ------------------------------------------------------

    def _process_photo(self, image: np.ndarray | None) -> np.ndarray | None:

        if image is None:
            logger.warning("No photo available for background removal.")
            return None

        try:
            return self._remove_photo_background(image)

        except Exception:
            logger.exception("Failed removing background from photo.")
            return image

    def _remove_photo_background(self, image: np.ndarray) -> np.ndarray:
        """
        Remove a plain studio-style backdrop from a
        personnel photo via border flood-fill.

        Approach
        --------
        1. Denoise (bilateral filter - smooths flat regions
           while preserving real edges).
        2. Flood-fill from many seed points along the image
           border, using FIXED_RANGE so each candidate pixel
           is compared against its ORIGINAL seed color, not
           the previously-filled neighbor - this is what
           prevents "drift" through gradients into the
           subject (floating-range flood fill will happily
           walk a smooth white-to-skin gradient all the way
           into the face).
        3. Keep only the SINGLE LARGEST connected foreground
           blob. This is what makes the result robust to
           low-contrast clothing: once the person is one
           connected foreground region (which they always
           are, since a body has no internal gaps), there is
           no per-pixel confidence to lose partway down the
           torso. It also discards small disconnected
           artifacts (stray print/scan border marks) that
           are technically non-white but aren't part of the
           person.
        4. Fill any small holes fully enclosed within that
           blob for a clean, solid result.
        """

        height, width = image.shape[:2]

        blurred = cv2.bilateralFilter(image, 9, 75, 75)

        mask = np.zeros((height + 2, width + 2), np.uint8)

        tolerance = (14, 14, 14)

        flags = (
            4
            | cv2.FLOODFILL_MASK_ONLY
            | cv2.FLOODFILL_FIXED_RANGE
            | (255 << 8)
        )

        seed_points = []

        seed_points += [(x, 0) for x in range(0, width, 8)]
        seed_points += [(x, height - 1) for x in range(0, width, 8)]
        seed_points += [(0, y) for y in range(0, height, 8)]
        seed_points += [(width - 1, y) for y in range(0, height, 8)]

        work = blurred.copy()

        for point in seed_points:

            if mask[point[1] + 1, point[0] + 1] == 0:

                cv2.floodFill(
                    work, mask, point, (0, 0, 0),
                    tolerance, tolerance, flags,
                )

        background_mask = mask[1:-1, 1:-1]

        alpha = np.where(background_mask > 0, 0, 255).astype(np.uint8)

        alpha = self._keep_largest_component(alpha)

        alpha = self._fill_small_holes(alpha)

        alpha = self._smooth_contour(alpha)

        alpha = self._refine_edge(alpha)

        rgb = self._decontaminate_edge(image, alpha)

        return np.dstack([rgb, alpha])

    def _smooth_contour(self, alpha: np.ndarray) -> np.ndarray:
        """
        Round off pixel-staircase jaggedness in the boundary
        CURVE itself.

        This is a different problem from spur removal
        (handled by keeping only the largest component): a
        flood-filled boundary follows individual pixel steps
        exactly, which looks visibly jagged/rough once
        upscaled for printing, even where there are no stray
        artifacts at all. Blurring the binary mask and
        re-thresholding rounds that pixel-level staircase
        into a smooth curve while leaving real large-scale
        shape (neck/shoulder concavities) intact.
        """

        blurred = cv2.GaussianBlur(alpha, (0, 0), sigmaX=2.5)

        return (blurred > 128).astype(np.uint8) * 255

    def _refine_edge(self, alpha: np.ndarray) -> np.ndarray:
        """
        Produce a tight, well-defined anti-aliased edge from
        the hard 0/255 mask, using a signed distance
        transform rather than a plain Gaussian blur.

        A plain blur spreads the transition band width based
        on kernel size alone and gets progressively softer
        after later upscaling, producing the washed-out,
        "not well defined" edge this replaces. A distance
        transform gives an exact, controllable transition
        width (about 2px here) regardless of image size.
        """

        binary = (alpha > 128).astype(np.uint8)

        dist_inside = cv2.distanceTransform(binary, cv2.DIST_L2, 5)

        dist_outside = cv2.distanceTransform(1 - binary, cv2.DIST_L2, 5)

        signed_distance = dist_inside - dist_outside

        half_band = 1.5

        refined = np.clip(
            (signed_distance + half_band) / (2 * half_band), 0, 1
        ) * 255.0

        return refined.astype(np.uint8)

    def _decontaminate_edge(
        self,
        image: np.ndarray,
        alpha: np.ndarray,
    ) -> np.ndarray:
        """
        For the thin soft-edge band, reverse the white blend
        baked into the original scan's own anti-aliasing at
        the photo's printed border:

            observed = alpha * subject + (1 - alpha) * white

        Left alone, a semi-transparent edge pixel keeps its
        pale, near-white observed color even though alpha
        says "mostly opaque" - producing a whitish glow/
        fringe around hair and shoulders once composited on
        anything other than white. This recovers the true
        edge color instead.
        """

        rgb = image.astype(np.float32)

        alpha_fraction = alpha.astype(np.float32) / 255.0

        edge_mask = (alpha > 5) & (alpha < 250)

        alpha_safe = np.where(
            edge_mask, np.clip(alpha_fraction, 0.12, 1.0), 1.0
        )[:, :, None]

        white = 255.0

        decontaminated = np.clip(
            (rgb - (1 - alpha_safe) * white) / alpha_safe, 0, 255
        )

        return np.where(
            edge_mask[:, :, None], decontaminated, rgb
        ).astype(np.uint8)

    def _keep_largest_component(self, alpha: np.ndarray) -> np.ndarray:

        binary = (alpha > 128).astype(np.uint8)

        n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        if n_labels <= 1:
            return alpha

        largest_label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))

        return np.where(labels == largest_label, 255, 0).astype(np.uint8)

    def _fill_small_holes(self, alpha: np.ndarray) -> np.ndarray:

        height, width = alpha.shape[:2]

        inverse = (alpha == 0).astype(np.uint8)

        n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            inverse, connectivity=8
        )

        #
        # Label 0 in `labels` at the image corner is the true
        # exterior background - everything else disconnected
        # from it, below a sane size, is a hole to fill.
        #
        exterior_label = labels[0, 0]

        max_hole_area = height * width * 0.02

        filled = alpha.copy()

        for label in range(1, n_labels):

            if label == exterior_label:
                continue

            if stats[label, cv2.CC_STAT_AREA] < max_hole_area:
                filled[labels == label] = 255

        return filled

    # ------------------------------------------------------
    # Internal - Signature (ink-darkness threshold)
    # ------------------------------------------------------

    def _process_signature(self, image: np.ndarray | None) -> np.ndarray | None:

        if image is None:
            logger.warning("No signature available for background removal.")
            return None

        try:
            return self._remove_signature_background(image)

        except Exception:
            logger.exception("Failed removing background from signature.")
            return image

    def _remove_signature_background(self, image: np.ndarray) -> np.ndarray:
        """
        Derive alpha directly from ink darkness against the
        (assumed light/white) paper background, using an
        Otsu threshold computed per-image so it adapts to
        each scan's actual ink/paper contrast.
        """

        if image.ndim == 3 and image.shape[2] == 4:
            bgr = image[:, :, :3]
        else:
            bgr = image

        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        #
        # Otsu is computed on a lightly blurred copy (a
        # touch more robust to scan grain when picking the
        # split point), but alpha itself is derived from the
        # RAW grayscale - blurring a 1-2px-thin ink stroke
        # dilutes it with surrounding white pixels, capping
        # its peak alpha well below full opacity.
        #
        otsu_threshold, _ = cv2.threshold(
            cv2.GaussianBlur(gray, (3, 3), 0),
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )

        background_reference = min(250.0, otsu_threshold + 40.0)

        alpha = np.clip(
            (background_reference - gray.astype(np.float32))
            / background_reference,
            0,
            1,
        ) * 255.0

        alpha = np.clip(alpha * 1.15, 0, 255).astype(np.uint8)

        darkened = np.clip(bgr.astype(np.float32) * 0.92, 0, 255).astype(
            np.uint8
        )

        return np.dstack([darkened, alpha])
