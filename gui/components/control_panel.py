"""
===========================================================
OES ID Extractor
Control Panel

Author:
    Onyedikachi Nzute

Description
-----------
Contains the primary application controls.

This panel is responsible only for displaying buttons and
dispatching user actions via callbacks. It does not contain
any business logic.
===========================================================
"""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


class ControlPanel(ctk.CTkFrame):
    """
    Main application control panel.
    """

    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)

        self._callbacks: dict[str, Callable] = {}

        self._create_widgets()
        self._layout_widgets()

    # ------------------------------------------------------
    # Widget Creation
    # ------------------------------------------------------

    def _create_widgets(self):

        self.add_files_button = ctk.CTkButton(
            self,
            text="Add Files",
            width=130,
            command=lambda: self._execute("add_files"),
        )

        self.add_folder_button = ctk.CTkButton(
            self,
            text="Add Folder",
            width=130,
            command=lambda: self._execute("add_folder"),
        )

        self.clear_button = ctk.CTkButton(
            self,
            text="Clear",
            width=100,
            command=lambda: self._execute("clear"),
        )

        self.start_button = ctk.CTkButton(
            self,
            text="Start",
            width=140,
            command=lambda: self._execute("start"),
        )

        self.stop_button = ctk.CTkButton(
            self,
            text="Stop",
            width=140,
            fg_color="#C62828",
            hover_color="#B71C1C",
            command=lambda: self._execute("stop"),
        )

    # ------------------------------------------------------
    # Layout
    # ------------------------------------------------------

    def _layout_widgets(self):

        self.grid_columnconfigure(5, weight=1)

        self.add_files_button.grid(
            row=0,
            column=0,
            padx=(10, 5),
            pady=10,
        )

        self.add_folder_button.grid(
            row=0,
            column=1,
            padx=5,
            pady=10,
        )

        self.clear_button.grid(
            row=0,
            column=2,
            padx=5,
            pady=10,
        )

        self.start_button.grid(
            row=0,
            column=6,
            padx=(5, 5),
            pady=10,
        )

        self.stop_button.grid(
            row=0,
            column=7,
            padx=(5, 10),
            pady=10,
        )

    # ------------------------------------------------------
    # Callback Registration
    # ------------------------------------------------------

    def bind(self, action: str, callback: Callable):
        """
        Register a callback for a control action.

        Available actions:

        - add_files
        - add_folder
        - clear
        - start
        - stop
        """

        self._callbacks[action] = callback

    def _execute(self, action: str):

        callback = self._callbacks.get(action)

        if callback is not None:
            callback()

    # ------------------------------------------------------
    # Button State Management
    # ------------------------------------------------------

    def enable_start(self):

        self.start_button.configure(
            state="normal",
        )

    def disable_start(self):

        self.start_button.configure(
            state="disabled",
        )

    def enable_stop(self):

        self.stop_button.configure(
            state="normal",
        )

    def disable_stop(self):

        self.stop_button.configure(
            state="disabled",
        )

    def set_processing_state(self, processing: bool):
        """
        Update button states based on whether the
        application is currently processing files.
        """

        if processing:

            self.disable_start()
            self.enable_stop()

            self.add_files_button.configure(state="disabled")
            self.add_folder_button.configure(state="disabled")
            self.clear_button.configure(state="disabled")

        else:

            self.enable_start()
            self.disable_stop()

            self.add_files_button.configure(state="normal")
            self.add_folder_button.configure(state="normal")
            self.clear_button.configure(state="normal")