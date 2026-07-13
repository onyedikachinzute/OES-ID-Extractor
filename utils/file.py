"""
===========================================================
OES ID Extractor
File Utilities

Author:
    Onyedikachi Nzute

Description
-----------
Filesystem helpers shared across the application: turning
user-selected paths into Document objects, discovering
supported files inside a folder, and loading plain image
files (JPG/PNG/TIFF/BMP) into OpenCV arrays.

Responsibilities
----------------
- Build Document objects from raw file paths
- Recursively discover supported files inside a folder
- Load a non-PDF image file into an OpenCV BGR array
- Validate that a path is a supported, existing file
===========================================================
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from config import config
from core.models.document import Document
from utils.logger import get_logger

logger = get_logger(__name__)


# --------------------------------------------------------
# Document Construction
# --------------------------------------------------------

def make_document(path: str | Path) -> Document:
    """
    Build a fresh Document for a single input file.
    """

    path = Path(path)

    return Document(
        path=path,
        extension=path.suffix.lower(),
        file_size=path.stat().st_size if path.exists() else 0,
    )


def make_documents(paths: list[str | Path]) -> list[Document]:
    """
    Build Document objects for a list of input files,
    skipping anything unsupported or missing.
    """

    documents: list[Document] = []

    for path in paths:

        path = Path(path)

        if not is_supported(path):

            logger.warning(
                "Skipping unsupported/missing file: %s",
                path,
            )

            continue

        documents.append(make_document(path))

    return documents


# --------------------------------------------------------
# Discovery
# --------------------------------------------------------

def is_supported(path: str | Path) -> bool:
    """
    Return True if `path` exists, is a file, and has a
    supported extension.
    """

    path = Path(path)

    if not path.is_file():
        return False

    return path.suffix.lower() in config.supported_extensions


def discover_files(folder: str | Path, recursive: bool = True) -> list[Path]:
    """
    Find every supported file inside `folder`.
    """

    folder = Path(folder)

    if not folder.is_dir():

        logger.warning("Not a directory: %s", folder)

        return []

    pattern_iter = folder.rglob("*") if recursive else folder.glob("*")

    files = sorted(
        p for p in pattern_iter
        if p.is_file() and p.suffix.lower() in config.supported_extensions
    )

    logger.info(
        "Discovered %d supported file(s) in '%s'.",
        len(files),
        folder,
    )

    return files


# --------------------------------------------------------
# Image Loading
# --------------------------------------------------------

def load_image(path: str | Path) -> np.ndarray:
    """
    Load a plain image file (JPG/PNG/BMP/TIFF) as an
    OpenCV BGR array.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.

    RuntimeError
        If the file exists but could not be decoded as
        an image.
    """

    path = Path(path)

    if not path.exists():

        raise FileNotFoundError(f"Image not found: {path}")

    #
    # np.fromfile + cv2.imdecode handles non-ASCII paths
    # correctly on Windows, unlike cv2.imread directly.
    #
    data = np.fromfile(str(path), dtype=np.uint8)

    image = cv2.imdecode(data, cv2.IMREAD_COLOR)

    if image is None:

        raise RuntimeError(f"Could not decode image: {path}")

    logger.info(
        "Loaded image '%s' (%dx%d).",
        path.name,
        image.shape[1],
        image.shape[0],
    )

    return image
