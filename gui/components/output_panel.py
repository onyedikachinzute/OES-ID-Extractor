"""
===========================================================
OES ID Extractor
Output Panel

Author:
    Onyedikachi Nzute

Description
-----------
Allows the user to view and configure the output
directories for extracted photos and signatures.
===========================================================
"""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from config import config


class OutputPanel(ctk.CTkFrame):
    """
    Panel for configuring output directories.
    """

    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)

        self._create_widgets()
        self._layout_widgets()
        self._load_settings()

    # --------------------------------------------------
    # Widget Creation
    # --------------------------------------------------

    def _create_widgets(self):

        self.title_label = ctk.CTkLabel(
            self,
            text="Output Directories",
            font=ctk.CTkFont(size=18, weight="bold"),
        )

        # ---------------------------
        # Photo Output
        # ---------------------------

        self.photo_label = ctk.CTkLabel(
            self,
            text="Photo Output",
        )

        self.photo_entry = ctk.CTkEntry(
            self,
            width=500,
        )

        self.photo_button = ctk.CTkButton(
            self,
            text="Browse",
            width=100,
            command=self.browse_photo_directory,
        )

        # ---------------------------
        # Signature Output
        # ---------------------------

        self.signature_label = ctk.CTkLabel(
            self,
            text="Signature Output",
        )

        self.signature_entry = ctk.CTkEntry(
            self,
            width=500,
        )

        self.signature_button = ctk.CTkButton(
            self,
            text="Browse",
            width=100,
            command=self.browse_signature_directory,
        )

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def _layout_widgets(self):

        self.grid_columnconfigure(1, weight=1)

        self.title_label.grid(
            row=0,
            column=0,
            columnspan=3,
            padx=10,
            pady=(10, 15),
            sticky="w",
        )

        # Photo

        self.photo_label.grid(
            row=1,
            column=0,
            padx=10,
            pady=5,
            sticky="w",
        )

        self.photo_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
            sticky="ew",
        )

        self.photo_button.grid(
            row=1,
            column=2,
            padx=10,
            pady=5,
        )

        # Signature

        self.signature_label.grid(
            row=2,
            column=0,
            padx=10,
            pady=(5, 10),
            sticky="w",
        )

        self.signature_entry.grid(
            row=2,
            column=1,
            padx=10,
            pady=(5, 10),
            sticky="ew",
        )

        self.signature_button.grid(
            row=2,
            column=2,
            padx=10,
            pady=(5, 10),
        )

    # --------------------------------------------------
    # Settings
    # --------------------------------------------------

    def _load_settings(self):

        self.set_photo_directory(config.photo_output_dir)
        self.set_signature_directory(config.signature_output_dir)

    # --------------------------------------------------
    # Browse
    # --------------------------------------------------

    def browse_photo_directory(self):

        directory = filedialog.askdirectory(
            title="Select Photo Output Folder"
        )

        if directory:
            self.set_photo_directory(directory)

            config.set(
                "photo_output_dir",
                directory,
            )

    def browse_signature_directory(self):

        directory = filedialog.askdirectory(
            title="Select Signature Output Folder"
        )

        if directory:
            self.set_signature_directory(directory)

            config.set(
                "signature_output_dir",
                directory,
            )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def set_photo_directory(self, path: str | Path):

        self.photo_entry.delete(0, "end")
        self.photo_entry.insert(0, str(path))

    def set_signature_directory(self, path: str | Path):

        self.signature_entry.delete(0, "end")
        self.signature_entry.insert(0, str(path))

    def get_photo_directory(self) -> Path:

        return Path(self.photo_entry.get())

    def get_signature_directory(self) -> Path:

        return Path(self.signature_entry.get())