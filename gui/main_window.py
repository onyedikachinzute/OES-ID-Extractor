"""
===========================================================
OES ID Extractor
Main Window

Author:
    Onyedikachi Nzute

Description
-----------
Assembles all GUI components into the application's main
content frame and wires user actions through to the
processing pipeline.

The MainWindow contains NO image-processing logic itself.
It only:

- Collects user input (files, folders, output directories)
- Starts/stops a background ProcessingThread
- Forwards Processor progress callbacks to the GUI panels
- Routes application logging into the LogPanel

===========================================================
"""

from __future__ import annotations

import queue
import tkinter.messagebox as messagebox
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from config import config
from core.processor import Processor
from gui.components.control_panel import ControlPanel
from gui.components.file_panel import FilePanel
from gui.components.log_panel import LogPanel
from gui.components.output_panel import OutputPanel
from gui.components.progress_panel import ProgressPanel
from gui.dialogs.about_dialog import AboutDialog
from gui.dialogs.settings_dialog import SettingsDialog
from utils.file import discover_files, make_documents
from utils.logger import LoggerManager, get_logger
from utils.threads import ProcessingThread

logger = get_logger(__name__)


class MainWindow(ctk.CTkFrame):
    """
    Main application content frame.
    """

    def __init__(self, master, **kwargs):

        super().__init__(master, fg_color="transparent", **kwargs)

        self._processing_thread: ProcessingThread | None = None

        self._callback_queue: "queue.Queue" = queue.Queue()

        self._create_widgets()
        self._layout_widgets()
        self._attach_log_handler()

        self._poll_callback_queue()
        self._bind_controls()

        logger.info("Application started.")

    # --------------------------------------------------
    # Widget Creation
    # --------------------------------------------------

    def _create_widgets(self):

        self.menu_bar = self._build_menu_bar()

        self.file_panel = FilePanel(self)

        self.control_panel = ControlPanel(self)

        self.output_panel = OutputPanel(self)

        self.progress_panel = ProgressPanel(self)

        self.log_panel = LogPanel(self)

    def _build_menu_bar(self) -> ctk.CTkFrame:
        """
        A simple in-frame menu bar (CustomTkinter has no
        native menubar styling), offering Settings/About.
        """

        bar = ctk.CTkFrame(self, height=44, fg_color=("gray86", "gray17"))

        title = ctk.CTkLabel(
            bar,
            text="OES ID Card PDF to Req Doc",
            font=ctk.CTkFont(size=16, weight="bold"),
        )

        title.pack(side="left", padx=15, pady=8)

        settings_btn = ctk.CTkButton(
            bar,
            text="Settings",
            width=100,
            command=self._open_settings,
        )

        settings_btn.pack(side="right", padx=(5, 10), pady=8)

        about_btn = ctk.CTkButton(
            bar,
            text="About",
            width=90,
            command=self._open_about,
        )

        about_btn.pack(side="right", padx=5, pady=8)

        return bar

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def _layout_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.menu_bar.grid(
            row=0, column=0, columnspan=2, sticky="ew",
        )

        self.file_panel.grid(
            row=1, column=0, padx=10, pady=(10, 5), sticky="nsew",
        )

        self.output_panel.grid(
            row=1, column=1, padx=10, pady=(10, 5), sticky="nsew",
        )

        self.control_panel.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew",
        )

        self.progress_panel.grid(
            row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew",
        )

        self.log_panel.grid(
            row=4, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="nsew",
        )

    # --------------------------------------------------
    # Logging Integration
    # --------------------------------------------------

    def _attach_log_handler(self):
        """
        Route every application log message into the
        LogPanel, in addition to the file/console handlers
        already configured by LoggerManager.
        """

        LoggerManager.add_handler(self.log_panel.create_handler())

    # --------------------------------------------------
    # Control Bindings
    # --------------------------------------------------

    def _bind_controls(self):

        self.control_panel.bind("add_files", self._on_add_files)
        self.control_panel.bind("add_folder", self._on_add_folder)
        self.control_panel.bind("clear", self._on_clear)
        self.control_panel.bind("start", self._on_start)
        self.control_panel.bind("stop", self._on_stop)

        self.control_panel.disable_stop()

    # --------------------------------------------------
    # File Selection
    # --------------------------------------------------

    def _on_add_files(self):

        extensions = " ".join(
            f"*{ext}" for ext in config.supported_extensions
        )

        paths = filedialog.askopenfilenames(
            title="Select ID Card Documents",
            filetypes=[
                ("Supported Documents", extensions),
                ("All Files", "*.*"),
            ],
        )

        if not paths:
            return

        self.file_panel.add_files([Path(p) for p in paths])

        logger.info("Added %d file(s) via file dialog.", len(paths))

    def _on_add_folder(self):

        folder = filedialog.askdirectory(title="Select Folder")

        if not folder:
            return

        files = discover_files(folder, recursive=True)

        if not files:
            messagebox.showinfo(
                "No Supported Files",
                "No supported PDF/image files were found in that folder.",
            )
            return

        self.file_panel.add_files(files)

        logger.info("Added %d file(s) from folder '%s'.", len(files), folder)

    def _on_clear(self):

        self.file_panel.clear()

        logger.info("Cleared input file list.")

    # --------------------------------------------------
    # Processing
    # --------------------------------------------------

    def _on_start(self):

        input_files = self.file_panel.get_files()

        if not input_files:
            messagebox.showwarning(
                "No Files Selected",
                "Please add at least one PDF or image file first.",
            )
            return

        #
        # Sync output directories chosen in the OutputPanel
        # into the persisted config BEFORE the pipeline (and
        # its Exporter) is constructed, so files land in the
        # right place.
        #
        config.set(
            "photo_output_dir",
            str(self.output_panel.get_photo_directory()),
        )

        config.set(
            "signature_output_dir",
            str(self.output_panel.get_signature_directory()),
        )

        documents = make_documents(input_files)

        if not documents:
            messagebox.showwarning(
                "No Valid Files",
                "None of the selected files could be queued for processing.",
            )
            return

        self.control_panel.set_processing_state(True)

        self.progress_panel.reset()
        self.progress_panel.start()

        processor = Processor(
            progress_callback=self._threadsafe(self.progress_panel.set_progress),
            status_callback=self._threadsafe(self.progress_panel.set_status),
            operation_callback=self._threadsafe(self.progress_panel.set_operation),
            file_callback=self._threadsafe(self.progress_panel.set_file_progress),
        )

        #
        # Reset per-batch state (e.g. duplicate-name
        # counters) so re-running a batch behaves
        # predictably.
        #
        processor.pipeline.namer.reset()

        self._processing_thread = ProcessingThread(
            processor=processor,
            documents=documents,
            on_error=self._threadsafe(self._on_processing_error),
            on_done=self._threadsafe(self._on_processing_done),
        )

        self._processing_thread.start()

        logger.info("Started processing %d document(s).", len(documents))

    def _on_stop(self):

        if self._processing_thread is not None:

            self._processing_thread.request_stop()

            logger.info("Stop requested by user.")

    def _on_processing_done(self):

        self.control_panel.set_processing_state(False)

        self.progress_panel.finish()

        logger.info("Batch processing finished.")

    def _on_processing_error(self, exc: Exception):

        self.control_panel.set_processing_state(False)

        messagebox.showerror(
            "Processing Error",
            f"An unexpected error occurred:\n\n{exc}",
        )

    # --------------------------------------------------
    # Dialogs
    # --------------------------------------------------

    def _open_settings(self):

        dialog = SettingsDialog(self)

        self.wait_window(dialog)

        self.output_panel.set_photo_directory(config.photo_output_dir)
        self.output_panel.set_signature_directory(config.signature_output_dir)

    def _open_about(self):

        AboutDialog(self)

    # --------------------------------------------------
    # Thread Safety Helper
    # --------------------------------------------------

    def _threadsafe(self, func):
        """
        Wrap a callback so it always runs on the Tkinter
        main thread, regardless of which thread invokes it.

        Calling `self.after(...)` directly FROM a background
        thread is not reliably safe in Tkinter - it can raise
        "RuntimeError: main thread is not in main loop"
        intermittently, since it depends on the exact
        interpreter state at the moment of the call. This is
        a race condition: it can appear to work fine for a
        long time and then fail unpredictably in production.

        Instead, the wrapped callback only ever pushes onto a
        thread-safe queue; `_poll_callback_queue`, scheduled
        exclusively via `self.after` from the main thread
        itself, is what actually invokes it.
        """

        def wrapper(*args, **kwargs):
            self._callback_queue.put((func, args, kwargs))

        return wrapper

    def _poll_callback_queue(self):
        """
        Runs on the main thread only. Drains any callbacks
        queued by background threads and invokes them safely.
        """

        try:

            while True:

                func, args, kwargs = self._callback_queue.get_nowait()

                func(*args, **kwargs)

        except queue.Empty:

            pass

        self.after(50, self._poll_callback_queue)

    # --------------------------------------------------
    # Shutdown
    # --------------------------------------------------

    def shutdown(self):

        if self._processing_thread is not None and self._processing_thread.is_alive():
            self._processing_thread.request_stop()
