"""
===========================================================
OES ID Extractor
Detection Model

Author:
    Onyedikachi Nzute

Description
-----------
Represents a single object detected by the vision system.
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Detection:
    """
    Represents a single object detected by the vision
    system.
    """

    class_id: int

    class_name: str

    confidence: float

    #
    # (x, y, width, height)
    #
    bbox: tuple[int, int, int, int]

    @property
    def x(self) -> int:
        return self.bbox[0]

    @property
    def y(self) -> int:
        return self.bbox[1]

    @property
    def width(self) -> int:
        return self.bbox[2]

    @property
    def height(self) -> int:
        return self.bbox[3]

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    @property
    def center(self) -> tuple[int, int]:
        return (
            self.x + self.width // 2,
            self.y + self.height // 2,
        )

    @property
    def area(self) -> int:
        return self.width * self.height
    
    @property
    def xyxy(self) -> tuple[int, int, int, int]:
        """
        Bounding box in (x1, y1, x2, y2) format.
        """
        return (
            self.x,
            self.y,
            self.right,
            self.bottom,
        )