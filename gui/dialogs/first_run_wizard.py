"""
===========================================================
OES ID Extractor
First-Run Setup Wizard

Author:
    Onyedikachi Nzute

Description
-----------
Shown exactly once, the first time the app runs on a given
machine/user account. Lets the user choose where extracted
photos and signatures should be saved, or accept sensible
defaults (the user's Documents folder) and move on.

These folders remain changeable at any time afterward via
Settings -> Photos Folder / Signatures Folder.
===========================================================
"""

from __future__ import annotations

from tkinter import filedialog, messagebox

import customtkinter as ctk

from config import config


class FirstRunWizard(ctk.CTkToplevel):
    """
    One-time setup wizard for output folders.
    """

    def __init__(self, master):

        super().__init__(master)

        self.title("Welcome - First-Time Setup")

        self.transient(master)
        self.grab_set()

        # Prevent closing via the window X without making a
        # choice - first run should end with valid folders
        # set one way or another.
        self.protocol("WM_DELETE_WINDOW", self._use_defaults_and_close)

        self._create_widgets()
        self._layout_widgets()

        #
        # A hardcoded pixel geometry is fragile: Windows DPI
        # scaling (125%/150%, common on laptops) or a
        # different default font can make actual content
        # taller than any fixed guess, silently pushing the
        # action buttons below the visible window with no
        # way to reach them since resizing was disabled.
        # Sizing to the real rendered content instead - and
        # allowing resize as a safety net - means the buttons
        # are always reachable regardless of DPI/font.
        #
        self.update_idletasks()

        width = max(640, self.winfo_reqwidth() + 20)
        height = max(420, self.winfo_reqheight() + 20)

        self.geometry(f"{width}x{height}")
        self.minsize(width, height)
        self.resizable(True, True)

    # --------------------------------------------------
    # Widgets
    # --------------------------------------------------

    def _create_widgets(self):

        self.title_label = ctk.CTkLabel(
            self,
            text="Welcome to OES ID Card PDF to Req Doc",
            font=ctk.CTkFont(size=20, weight="bold"),
        )

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=(
                "Choose where extracted personnel photos and signatures "
                "should be saved.\nYou can change this later at any time "
                "in Settings."
            ),
            justify="left",
            text_color=("gray30", "gray70"),
        )

        self.photo_dir_label = ctk.CTkLabel(self, text="Photos Folder")

        self.photo_dir_entry = ctk.CTkEntry(self, width=380)

        self.photo_dir_browse = ctk.CTkButton(
            self, text="Browse...", width=90,
            command=lambda: self._browse(self.photo_dir_entry, "Select Photos Folder"),
        )

        self.signature_dir_label = ctk.CTkLabel(self, text="Signatures Folder")

        self.signature_dir_entry = ctk.CTkEntry(self, width=380)

        self.signature_dir_browse = ctk.CTkButton(
            self, text="Browse...", width=90,
            command=lambda: self._browse(self.signature_dir_entry, "Select Signatures Folder"),
        )

        self.continue_button = ctk.CTkButton(
            self, text="Continue", command=self._save_and_close,
        )

        self.defaults_button = ctk.CTkButton(
            self, text="Use Defaults", fg_color="transparent",
            border_width=1, command=self._use_defaults_and_close,
        )

        self.photo_dir_entry.insert(0, str(config.photo_output_dir))
        self.signature_dir_entry.insert(0, str(config.signature_output_dir))

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def _layout_widgets(self):

        padx = 24

        self.title_label.pack(padx=padx, pady=(24, 6), anchor="w")
        self.subtitle_label.pack(padx=padx, pady=(0, 20), anchor="w")

        self.photo_dir_label.pack(padx=padx, pady=(6, 2), anchor="w")

        photo_row = ctk.CTkFrame(self, fg_color="transparent")
        photo_row.pack(padx=padx, pady=(0, 12), fill="x")
        self.photo_dir_entry.pack(in_=photo_row, side="left", fill="x", expand=True)
        self.photo_dir_browse.pack(in_=photo_row, side="left", padx=(8, 0))

        self.signature_dir_label.pack(padx=padx, pady=(6, 2), anchor="w")

        sig_row = ctk.CTkFrame(self, fg_color="transparent")
        sig_row.pack(padx=padx, pady=(0, 24), fill="x")
        self.signature_dir_entry.pack(in_=sig_row, side="left", fill="x", expand=True)
        self.signature_dir_browse.pack(in_=sig_row, side="left", padx=(8, 0))

        button_row = ctk.CTkFrame(self, fg_color="transparent")
        button_row.pack(padx=padx, pady=(0, 24), fill="x", side="bottom")
        self.defaults_button.pack(in_=button_row, side="left")
        self.continue_button.pack(in_=button_row, side="right")

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    def _browse(self, entry: ctk.CTkEntry, title: str):

        folder = filedialog.askdirectory(title=title)

        if folder:
            entry.delete(0, "end")
            entry.insert(0, folder)

    def _save_and_close(self):

        photo_dir = self.photo_dir_entry.get().strip()
        signature_dir = self.signature_dir_entry.get().strip()

        if not photo_dir or not signature_dir:
            messagebox.showwarning(
                "Missing Folder",
                "Please choose both folders, or click 'Use Defaults'.",
            )
            return

        try:

            config.set("photo_output_dir", photo_dir)
            config.set("signature_output_dir", signature_dir)

        except OSError as e:
            messagebox.showerror(
                "Invalid Folder",
                f"Could not use that folder:\n\n{e}",
            )
            return

        config.complete_first_run()

        self.destroy()

    def _use_defaults_and_close(self):

        config.complete_first_run()

        self.destroy()
