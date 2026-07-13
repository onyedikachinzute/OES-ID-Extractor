"""
===========================================================
OES ID Extractor
Progress Panel

Author:
    Onyedikachi Nzute

Description
-----------
Displays the application's processing progress,
current status and current operation.
===========================================================
"""

from __future__ import annotations

import customtkinter as ctk


class ProgressPanel(ctk.CTkFrame):
    """
    Displays processing progress.
    """

    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)

        self._create_widgets()
        self._layout_widgets()

        self.reset()

    # --------------------------------------------------
    # Widget Creation
    # --------------------------------------------------

    def _create_widgets(self):

        self.title_label = ctk.CTkLabel(
            self,
            text="Progress",
            font=ctk.CTkFont(
                size=18,
                weight="bold",
            ),
        )

        self.progress_bar = ctk.CTkProgressBar(
            self,
        )

        self.progress_label = ctk.CTkLabel(
            self,
            text="0%",
        )

        self.status_title = ctk.CTkLabel(
            self,
            text="Status:",
            font=ctk.CTkFont(weight="bold"),
        )

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
        )

        self.operation_title = ctk.CTkLabel(
            self,
            text="Current Operation:",
            font=ctk.CTkFont(weight="bold"),
        )

        self.operation_label = ctk.CTkLabel(
            self,
            text="Waiting...",
            anchor="w",
        )

        self.file_counter = ctk.CTkLabel(
            self,
            text="0 / 0 Files",
            anchor="e",
        )

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def _layout_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.title_label.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=10,
            pady=(10, 5),
            sticky="w",
        )

        self.progress_bar.grid(
            row=1,
            column=0,
            padx=(10, 5),
            pady=5,
            sticky="ew",
        )

        self.progress_label.grid(
            row=1,
            column=1,
            padx=(5, 10),
        )

        self.status_title.grid(
            row=2,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="w",
        )

        self.status_label.grid(
            row=3,
            column=0,
            padx=20,
            sticky="w",
        )

        self.operation_title.grid(
            row=4,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="w",
        )

        self.operation_label.grid(
            row=5,
            column=0,
            padx=20,
            sticky="w",
        )

        self.file_counter.grid(
            row=5,
            column=1,
            padx=10,
            sticky="e",
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def reset(self):

        self.set_progress(0)

        self.set_status("Ready")

        self.set_operation("Waiting...")

        self.set_file_progress(0, 0)

    def set_progress(self, value: float):
        """
        value must be between 0.0 and 1.0
        """

        value = max(0.0, min(1.0, value))

        self.progress_bar.set(value)

        self.progress_label.configure(
            text=f"{value * 100:.0f}%"
        )

    def set_status(self, text: str):

        self.status_label.configure(
            text=text,
        )

    def set_operation(self, text: str):

        self.operation_label.configure(
            text=text,
        )

    def set_file_progress(
        self,
        current: int,
        total: int,
    ):

        self.file_counter.configure(
            text=f"{current} / {total} Files"
        )

    def start(self):

        self.set_status("Processing")

    def finish(self):

        self.set_progress(1.0)

        self.set_status("Completed")

        self.set_operation(
            "Finished"
        )
        
    def update_progress(self, progress, status, operation, current, total):
        self.after(
            0,
            lambda: (
                self.set_progress(progress),
                self.set_status(status),
                self.set_operation(operation),
                self.set_file_progress(current, total),
            ),
        )

    def cancel(self):

        self.set_status("Cancelled")

        self.set_operation(
            "Processing stopped."
        )