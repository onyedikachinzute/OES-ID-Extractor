"""
===========================================================
OES ID Extractor
Config Shim

Author:
    Onyedikachi Nzute

Description
-----------
The single source of truth for configuration is the
project-root `config.py` (`from config import config`).

This module exists only so that `from utils.config import
config` also works for any code that expects configuration
helpers to live under the `utils` package, without
maintaining two separate settings implementations.
===========================================================
"""

from __future__ import annotations

from config import Config, config

__all__ = ["Config", "config"]
