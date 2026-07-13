"""
===========================================================
OES ID Extractor
Log Panel

Author:
    Onyedikachi Nzute

Description
-----------
Displays live application logs.

This panel integrates directly with Python's logging
system through a custom logging.Handler, allowing every
log message written by the application to automatically
appear in the GUI.

Features
--------
• Live log updates
• Thread-safe
• Auto-scroll
• Color coded log levels
• Clear log button
• Read-only log display
===========================================================
"""

from __future__ import annotations

import logging
import queue

import customtkinter as ctk


# ==========================================================
# GUI Logging Handler
# ==========================================================


class GuiLogHandler(logging.Handler):
    """
    Logging handler that forwards log messages to the
    LogPanel.

    Log records can arrive from any thread (the background
    processing thread logs constantly). Calling Tkinter
    widget methods - including `.after()` - directly from a
    non-main thread is not reliably safe and can raise
    "main thread is not in main loop". To avoid that, this
    handler only ever pushes onto a thread-safe queue; the
    LogPanel itself polls that queue from the main thread.
    """

    def __init__(self, panel: "LogPanel"):

        super().__init__()

        self.panel = panel

        self.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S",
            )
        )

    def emit(self, record: logging.LogRecord):

        try:
            message = self.format(record)
            self.panel.enqueue(message, record.levelname)

        except Exception:
            self.handleError(record)


# ==========================================================
# Log Panel
# ==========================================================


class LogPanel(ctk.CTkFrame):
    """
    Live application log viewer.
    """

    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)

        self._queue: "queue.Queue[tuple[str, str]]" = queue.Queue()

        self._create_widgets()
        self._layout_widgets()
        self._configure_tags()

        self._poll_queue()

    # ------------------------------------------------------
    # Widgets
    # ------------------------------------------------------

    def _create_widgets(self):

        self.title_label = ctk.CTkLabel(
            self,
            text="Application Log",
            font=ctk.CTkFont(
                size=18,
                weight="bold",
            ),
        )

        self.clear_button = ctk.CTkButton(
            self,
            text="Clear",
            width=80,
            command=self.clear,
        )

        self.log_box = ctk.CTkTextbox(
            self,
            wrap="word",
        )

        self.log_box.configure(
            state="disabled",
        )

    # ------------------------------------------------------
    # Layout
    # ------------------------------------------------------

    def _layout_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label.grid(
            row=0,
            column=0,
            padx=10,
            pady=(10, 5),
            sticky="w",
        )

        self.clear_button.grid(
            row=0,
            column=1,
            padx=10,
            pady=(10, 5),
            sticky="e",
        )

        self.log_box.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=10,
            pady=(0, 10),
            sticky="nsew",
        )

    # ------------------------------------------------------
    # Configure Tags
    # ------------------------------------------------------

    def _configure_tags(self):

        self.log_box.tag_config(
            "INFO",
            foreground="#4FC3F7",
        )

        self.log_box.tag_config(
            "WARNING",
            foreground="#FFC107",
        )

        self.log_box.tag_config(
            "ERROR",
            foreground="#F44336",
        )

        self.log_box.tag_config(
            "CRITICAL",
            foreground="#D50000",
        )

        self.log_box.tag_config(
            "DEBUG",
            foreground="#9E9E9E",
        )

    # ------------------------------------------------------
    # Internal
    # ------------------------------------------------------

    def _append(
        self,
        message: str,
        level: str,
    ):

        self.log_box.configure(
            state="normal",
        )

        self.log_box.insert(
            "end",
            message + "\n",
            level,
        )

        self.log_box.see("end")

        self.log_box.configure(
            state="disabled",
        )

    # ------------------------------------------------------
    # Public
    # ------------------------------------------------------

    def clear(self):

        self.log_box.configure(
            state="normal",
        )

        self.log_box.delete(
            "1.0",
            "end",
        )

        self.log_box.configure(
            state="disabled",
        )

    def create_handler(self) -> GuiLogHandler:
        """
        Returns a configured logging handler
        for this panel.
        """

        return GuiLogHandler(self)

    # ------------------------------------------------------
    # Thread-safe Queue Delivery
    # ------------------------------------------------------

    def enqueue(self, message: str, level: str) -> None:
        """
        Safe to call from ANY thread. Actual widget updates
        only ever happen on the main thread via _poll_queue.
        """

        self._queue.put((message, level))

    def _poll_queue(self) -> None:
        """
        Runs on the main thread only (scheduled via
        `.after`, always from the main thread itself, which
        is safe). Drains the queue and appends every
        pending message to the log box.
        """

        try:

            while True:

                message, level = self._queue.get_nowait()

                self._append(message, level)

        except queue.Empty:

            pass

        self.after(150, self._poll_queue)