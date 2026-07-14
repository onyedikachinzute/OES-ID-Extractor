"""
===========================================================
OES ID Extractor
YOLO Model Test

Author:
    Onyedikachi Nzute

Description
-----------
Loads the trained YOLO model and runs inference on a
single image.

This file is ONLY for testing that the model is working
correctly before integrating it into the application.

Usage
-----
python test_yolo.py path/to/image.jpg
===========================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2

from vision.yolo_model import YOLOModel


def main() -> None:

    if len(sys.argv) != 2:

        print(
            "Usage:\n"
            "    python test_yolo.py image.jpg"
        )
        return

    image_path = Path(sys.argv[1])

    if not image_path.exists():

        print(f"Image not found: {image_path}")
        return

    print(f"\nLoading image: {image_path}")

    image = cv2.imread(str(image_path))

    if image is None:

        print("OpenCV could not read the image.")
        return

    model = YOLOModel()

    if model.model is None:

        print("\nYOLO model failed to load.")
        return

    print("\nModel loaded successfully.")
    print("Running inference...\n")

    detections = model.predict(image)

    if not detections:

        print("No detections.")
        return

    print(f"Found {len(detections)} detections:\n")

    for i, det in enumerate(detections, start=1):

        x, y, w, h = det.bbox

        print(f"Detection #{i}")
        print(f"  Class      : {det.class_name}")
        print(f"  Confidence : {det.confidence:.3f}")
        print(f"  BoundingBox: ({x}, {y}, {w}, {h})")
        print()

        # Draw rectangle

        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2,
        )

        cv2.putText(
            image,
            f"{det.class_name} {det.confidence:.2f}",
            (x, max(20, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

    output = image_path.with_name(
        image_path.stem + "_detections.jpg"
    )

    cv2.imwrite(str(output), image)

    print(f"Annotated image saved to:\n{output}")


if __name__ == "__main__":
    main()