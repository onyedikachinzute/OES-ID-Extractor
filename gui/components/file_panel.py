"""
===========================================================
OES ID Extractor
File Panel

Author:
    Onyedikachi Nzute

Description
-----------
Displays and manages the list of files selected for
processing.
===========================================================
"""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk


class FilePanel(ctk.CTkFrame):
    """
    Panel containing the selected input files.
    """

    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)

        self.files: list[Path] = []

        self._create_widgets()
        self._layout_widgets()

    def _create_widgets(self):

        self.title_label = ctk.CTkLabel(
            self,
            text="Input Files",
            font=ctk.CTkFont(size=18, weight="bold"),
        )

        self.file_list = ctk.CTkTextbox(
            self,
            height=220,
        )

        self.file_list.configure(state="disabled")

    def _layout_widgets(self):

        self.grid_columnconfigure(0, weight=1)

        self.title_label.grid(
            row=0,
            column=0,
            padx=10,
            pady=(10, 5),
            sticky="w",
        )

        self.file_list.grid(
            row=1,
            column=0,
            padx=10,
            pady=(0, 10),
            sticky="nsew",
        )

    # ----------------------------------------------------
    # Public API
    # ----------------------------------------------------

    def add_files(self, paths: list[Path]):

        for path in paths:
            if path not in self.files:
                self.files.append(path)

        self.refresh()

    def clear(self):

        self.files.clear()
        self.refresh()

    def refresh(self):

        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")

        if not self.files:
            self.file_list.insert("end", "No files selected.\n")
        else:
            for file in self.files:
                self.file_list.insert(
                    "end",
                    f"{file.name}\n",
                )

        self.file_list.configure(state="disabled")

    def get_files(self) -> list[Path]:

        return self.files.copy()