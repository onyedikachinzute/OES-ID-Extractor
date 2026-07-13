"""
===========================================================
OES ID Extractor
Logging System

Author:
    Onyedikachi Nzute

Description
-----------
Provides a centralized logging system for the entire
application.

Features
--------
• Daily log files
• Per-session log files
• Console logging
• Thread-safe
• Per-module loggers
• UTF-8 support

Usage
-----
from utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Application started.")
===========================================================
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from config import config


class LoggerManager:
    """
    Creates and manages application loggers.
    """

    _configured = False
    _session_file: Path | None = None

    @classmethod
    def configure(cls) -> None:
        """
        Configure the application's logging system.
        """

        if cls._configured:
            return

        # --------------------------------------------------
        # Create log directories
        # --------------------------------------------------

        session_dir = Path(config.log_dir) / "sessions"
        session_dir.mkdir(parents=True, exist_ok=True)

        # --------------------------------------------------
        # Log file paths
        # --------------------------------------------------

        cls._session_file = (
            session_dir
            / f"session_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
        )

        log_file = (
            Path(config.log_dir)
            / f"{datetime.now():%Y-%m-%d}.log"
        )

        # --------------------------------------------------
        # Formatter
        # --------------------------------------------------

        formatter = logging.Formatter(
            fmt=(
                "[%(asctime)s] "
                "[%(levelname)-8s] "
                "[%(name)s] "
                "%(message)s"
            ),
            datefmt="%H:%M:%S",
        )

        # --------------------------------------------------
        # Root Logger
        # --------------------------------------------------

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Prevent duplicate handlers if configure()
        # is ever called again.
        root_logger.handlers.clear()

        # --------------------------------------------------
        # Handlers
        # --------------------------------------------------

        daily_handler = logging.FileHandler(
            log_file,
            encoding="utf-8",
        )

        session_handler = logging.FileHandler(
            cls._session_file,
            encoding="utf-8",
        )

        console_handler = logging.StreamHandler()

        # --------------------------------------------------
        # Apply formatter
        # --------------------------------------------------

        daily_handler.setFormatter(formatter)
        session_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # --------------------------------------------------
        # Register handlers
        # --------------------------------------------------

        root_logger.addHandler(daily_handler)
        root_logger.addHandler(session_handler)
        root_logger.addHandler(console_handler)

        cls._configured = True

    @classmethod
    def session_file(cls) -> Path | None:
        """
        Returns the current session log file.
        """

        return cls._session_file
    
    @classmethod
    def add_handler(cls, handler: logging.Handler) -> None:
        """
        Register an additional logging handler.
        """

        LoggerManager.configure()

        logging.getLogger().addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger.

    Parameters
    ----------
    name:
        Usually __name__.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    LoggerManager.configure()
    return logging.getLogger(name)

