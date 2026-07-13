"""
===========================================================
OES ID Extractor
Application Shell

Author:
    Onyedikachi Nzute

Description
-----------
Defines the top-level CustomTkinter application window
(chrome, sizing, theme). All actual UI content and wiring
lives in gui/main_window.py - this module only owns the
outer OS-level window.

Responsibilities
----------------
- Configure CustomTkinter appearance/theme from settings
- Create and size the root window
- Host the MainWindow content frame
- Handle graceful shutdown

===========================================================
"""

from __future__ import annotations

import customtkinter as ctk

from config import config
from gui.main_window import MainWindow
from utils.logger import get_logger

logger = get_logger(__name__)


class App(ctk.CTk):
    """
    Root application window.
    """

    def __init__(self):

        super().__init__()

        gui_cfg = config.gui_settings

        theme = gui_cfg.get("theme", "dark")

        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")

        self.title(
            "OES ID Card PDF to Req Doc — Photo & Signature Extractor"
        )

        width = gui_cfg.get("window_width", 1200)
        height = gui_cfg.get("window_height", 700)

        self.geometry(f"{width}x{height}")
        self.minsize(1000, 620)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_window = MainWindow(self)

        self.main_window.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if config.is_first_run:
            self.after(150, self._show_first_run_wizard)

    def _show_first_run_wizard(self):

        from gui.dialogs.first_run_wizard import FirstRunWizard

        wizard = FirstRunWizard(self)

        self.wait_window(wizard)

        # Folders may have changed during setup - refresh the
        # main window's Output panel to reflect them.
        self.main_window.output_panel.set_photo_directory(
            config.photo_output_dir
        )

        self.main_window.output_panel.set_signature_directory(
            config.signature_output_dir
        )

    # --------------------------------------------------
    # Shutdown
    # --------------------------------------------------

    def _on_close(self) -> None:

        logger.info("Application closing.")

        try:
            self.main_window.shutdown()
        except Exception:
            logger.exception("Error during shutdown.")

        self.destroy()
