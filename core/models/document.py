"""
===========================================================
OES ID Extractor
Document Model

Author:
    Onyedikachi Nzute

Description
-----------
Represents a single input document throughout the
processing pipeline.

Each processing stage enriches this object with additional
information instead of creating new data structures.
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Document:
    """
    Represents a document being processed.
    """

    # ------------------------------------------------------
    # Source Information
    # ------------------------------------------------------

    path: Path
    extension: str
    file_size: int

    # ------------------------------------------------------
    # Processing State
    # ------------------------------------------------------

    status: str = "Pending"

    # Pending
    # Analyzing
    # Processing
    # Completed
    # Failed
    # Cancelled

    error: str = ""

    # ------------------------------------------------------
    # Analysis Results
    # ------------------------------------------------------

    document_type: str = "Unknown"

    # PDF
    # Image

    page_count: int = 0

    is_scanned: bool = False

    requires_ocr: bool = False

    # ------------------------------------------------------
    # Extraction Results
    # ------------------------------------------------------

    extracted_name: str = ""

    photo: Any = None

    signature: Any = None

    photo_bbox: tuple[int, int, int, int] | None = None

    signature_bbox: tuple[int, int, int, int] | None = None
    
    name_bbox: tuple[int, int, int, int] | None = None
    
    source_image: Any = None

    cropped_photo: Any = None

    cropped_signature: Any = None
    
    name_crop: Any = None


    photo_output_path: Path | None = None

    signature_output_path: Path | None = None
        
    personnel_name: Any = None
    
    output_name: Any = None
    
    raw_ocr_text: str | None = None

    ocr_confidence: float | None = None

    ocr_variant: str | None = None

    # ------------------------------------------------------
    # Processing Metadata
    # ------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------

    @property
    def filename(self) -> str:
        """
        Returns the filename including extension.
        """

        return self.path.name

    @property
    def stem(self) -> str:
        """
        Returns the filename without extension.
        """

        return self.path.stem

    @property
    def parent(self) -> Path:
        """
        Returns the parent directory.
        """

        return self.path.parent

    @property
    def is_pdf(self) -> bool:
        """
        Returns True if this document is a PDF.
        """

        return self.extension == ".pdf"

    @property
    def is_image(self) -> bool:
        """
        Returns True if this document is an image.
        """

        return self.extension in {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".tif",
            ".tiff",
        }

    @property
    def has_photo(self) -> bool:
        """
        Returns True if a personnel photo has been extracted.
        """

        return self.photo is not None

    @property
    def has_signature(self) -> bool:
        """
        Returns True if a signature has been extracted.
        """

        return self.signature is not None

    @property
    def completed(self) -> bool:
        """
        Returns True if processing completed successfully.
        """

        return self.status == "Completed"

    @property
    def failed(self) -> bool:
        """
        Returns True if processing failed.
        """

        return self.status == "Failed"

    # ------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------

    def reset(self) -> None:
        """
        Reset all processing results while preserving the
        source document information.
        """

        self.status = "Pending"
        self.error = ""

        self.document_type = "Unknown"
        self.page_count = 0
        self.is_scanned = False
        self.requires_ocr = False

        self.extracted_name = ""

        self.photo = None
        self.signature = None

        self.metadata.clear()

    def __str__(self) -> str:

        return self.filename

    def __repr__(self) -> str:

        return (
            f"Document("
            f"filename='{self.filename}', "
            f"status='{self.status}', "
            f"type='{self.document_type}')"
        )