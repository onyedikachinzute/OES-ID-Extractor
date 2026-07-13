"""
===========================================================
OES ID Extractor
Document Model - Re-export Shim

Author:
    Onyedikachi Nzute

Description
-----------
The canonical Document model lives in core/models/document.py
(it is a core, pipeline-specific model, unlike the generic
vision Detection model in models/detection.py).

Most of the codebase imports it as `from models.document
import Document`. This shim keeps that import path working
without duplicating the class definition in two places.
===========================================================
"""

from __future__ import annotations

from core.models.document import Document

__all__ = ["Document"]
