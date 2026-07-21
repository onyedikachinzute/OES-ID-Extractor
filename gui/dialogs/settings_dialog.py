"""
===========================================================
OES ID Extractor
Settings Dialog

Author:
    Onyedikachi Nzute

Description
-----------
Allows the user to configure application settings.

Changes are written directly to the application's
configuration system.
===========================================================
"""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from config import config, ProcessingMode


class SettingsDialog(ctk.CTkToplevel):
    """
    Application settings dialog.
    """

    def __init__(self, master):

        super().__init__(master)

        self.title("Settings")

        self.transient(master)
        self.grab_set()

        self._create_widgets()
        self._layout_widgets()
        self._load_settings()

        self.update_idletasks()

        width = max(700, self.winfo_reqwidth() + 20)
        height = max(650, self.winfo_reqheight() + 20)

        self.geometry(f"{width}x{height}")
        self.minsize(width, height)
        self.resizable(True, True)


    # --------------------------------------------------
    # Widgets
    # --------------------------------------------------

    def _create_widgets(self):

        self.title_label = ctk.CTkLabel(
            self,
            text="Application Settings",
            font=ctk.CTkFont(
                size=22,
                weight="bold",
            ),
        )

        #
        # Output folders
        #

        self.photo_dir_label = ctk.CTkLabel(
            self,
            text="Photos Folder",
        )

        self.photo_dir_entry = ctk.CTkEntry(self)

        self.photo_dir_browse = ctk.CTkButton(
            self,
            text="Browse...",
            width=90,
            command=self._browse_photo_dir,
        )

        self.signature_dir_label = ctk.CTkLabel(
            self,
            text="Signatures Folder",
        )

        self.signature_dir_entry = ctk.CTkEntry(self)

        self.signature_dir_browse = ctk.CTkButton(
            self,
            text="Browse...",
            width=90,
            command=self._browse_signature_dir,
        )

        #
        # Theme
        #

        self.theme_label = ctk.CTkLabel(
            self,
            text="Appearance",
        )

        self.theme_menu = ctk.CTkOptionMenu(
            self,
            values=[
                "System",
                "Light",
                "Dark",
            ],
        )
        
        self.processing_mode_label = ctk.CTkLabel(
            self,
            text="Processing Mode",
        )
        
        self.processing_modes = {
            "Full Processing": ProcessingMode.FULL,
            "Crop Only (Debug)": ProcessingMode.CROP_ONLY,
        }
        
        self.processing_mode_menu = ctk.CTkOptionMenu(
            self,
            values=list(self.processing_modes.keys()),
            command=self._processing_mode_changed
        )


        #
        # DPI
        #

        self.dpi_label = ctk.CTkLabel(
            self,
            text="PDF DPI",
        )

        self.dpi_entry = ctk.CTkEntry(self)

        #
        # Padding
        #

        self.photo_padding_label = ctk.CTkLabel(
            self,
            text="Photo Padding",
        )

        self.photo_padding_entry = ctk.CTkEntry(self)

        self.signature_padding_label = ctk.CTkLabel(
            self,
            text="Signature Padding",
        )

        self.signature_padding_entry = ctk.CTkEntry(self)

        #
        # Switches
        #

        self.clahe_switch = ctk.CTkSwitch(
            self,
            text="Enable CLAHE",
        )

        self.sharpen_switch = ctk.CTkSwitch(
            self,
            text="Enable Sharpening",
        )

        self.ocr_switch = ctk.CTkSwitch(
            self,
            text="Enable OCR",
        )

        self.bg_switch = ctk.CTkSwitch(
            self,
            text="Enable Background Removal",
        )

        #
        # OCR Language
        #

        self.language_label = ctk.CTkLabel(
            self,
            text="OCR Language",
        )

        self.language_entry = ctk.CTkEntry(self)

        #
        # Buttons
        #

        self.save_button = ctk.CTkButton(
            self,
            text="Save",
            command=self.save,
        )

        self.cancel_button = ctk.CTkButton(
            self,
            text="Cancel",
            command=self.destroy,
        )

    # --------------------------------------------------
    # Folder Browsing
    # --------------------------------------------------

    def _browse_photo_dir(self):

        folder = filedialog.askdirectory(title="Select Photos Folder")

        if folder:
            self.photo_dir_entry.delete(0, "end")
            self.photo_dir_entry.insert(0, folder)

    def _browse_signature_dir(self):

        folder = filedialog.askdirectory(title="Select Signatures Folder")

        if folder:
            self.signature_dir_entry.delete(0, "end")
            self.signature_dir_entry.insert(0, folder)

    # --------------------------------------------------
    # Processing Mode
    # --------------------------------------------------

    def _processing_mode_changed(self, choice: str):
        """
        Enable or disable controls depending on the
        selected processing mode.
        """

        crop_only = (
            self.processing_modes[choice]
            == ProcessingMode.CROP_ONLY
        )

        state = "disabled" if crop_only else "normal"

        self.bg_switch.configure(
            state=state
        )

        self.sharpen_switch.configure(
            state=state
        )
        
        self.clahe_switch.configure(
            state=state
        )
        
    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def _layout_widgets(self):

        padx = 20

        self.grid_columnconfigure(1, weight=1)

        self.title_label.grid(
            row=0,
            column=0,
            columnspan=3,
            pady=(20, 30),
        )

        row = 1

        for label, entry, browse in (
            (self.photo_dir_label, self.photo_dir_entry, self.photo_dir_browse),
            (self.signature_dir_label, self.signature_dir_entry, self.signature_dir_browse),
        ):

            label.grid(row=row, column=0, padx=padx, pady=8, sticky="w")
            entry.grid(row=row, column=1, padx=(padx, 5), pady=8, sticky="ew")
            browse.grid(row=row, column=2, padx=(0, padx), pady=8, sticky="ew")

            row += 1

        widgets = [

            (self.theme_label, self.theme_menu),
            
            (self.processing_mode_label,
             self.processing_mode_menu),

            (self.dpi_label, self.dpi_entry),

            (self.photo_padding_label,
             self.photo_padding_entry),

            (self.signature_padding_label,
             self.signature_padding_entry),

            (self.language_label,
             self.language_entry),

        ]

        for label, widget in widgets:

            label.grid(
                row=row,
                column=0,
                padx=padx,
                pady=8,
                sticky="w",
            )

            widget.grid(
                row=row,
                column=1,
                padx=padx,
                pady=8,
                sticky="ew",
            )

            row += 1

        self.clahe_switch.grid(
            row=row,
            column=0,
            columnspan=2,
            padx=padx,
            pady=6,
            sticky="w",
        )

        row += 1

        self.sharpen_switch.grid(
            row=row,
            column=0,
            columnspan=2,
            padx=padx,
            pady=6,
            sticky="w",
        )

        row += 1

        self.ocr_switch.grid(
            row=row,
            column=0,
            columnspan=2,
            padx=padx,
            pady=6,
            sticky="w",
        )

        row += 1

        self.bg_switch.grid(
            row=row,
            column=0,
            columnspan=2,
            padx=padx,
            pady=6,
            sticky="w",
        )

        row += 1

        self.save_button.grid(
            row=row,
            column=0,
            padx=20,
            pady=30,
            sticky="ew",
        )

        self.cancel_button.grid(
            row=row,
            column=1,
            padx=20,
            pady=30,
            sticky="ew",
        )

    # --------------------------------------------------
    # Settings
    # --------------------------------------------------

    def _load_settings(self):

        image = config.image_settings
        ocr = config.ocr_settings

        self.photo_dir_entry.insert(
            0,
            str(config.photo_output_dir),
        )

        self.signature_dir_entry.insert(
            0,
            str(config.signature_output_dir),
        )

        self.theme_menu.set(
            config.gui_settings["theme"].title()
        )
        
        for text, mode in self.processing_modes.items():

            if mode == config.processing_mode:

                self.processing_mode_menu.set(text)

                break
        
        self._processing_mode_changed(
            self.processing_mode_menu.get()
        )

        self.dpi_entry.insert(
            0,
            str(image["dpi"]),
        )

        self.photo_padding_entry.insert(
            0,
            str(image["photo_padding"]),
        )

        self.signature_padding_entry.insert(
            0,
            str(image["signature_padding"]),
        )

        self.language_entry.insert(
            0,
            ocr["language"],
        )

        if image["clahe"]:
            self.clahe_switch.select()

        if image["sharpen"]:
            self.sharpen_switch.select()

        if ocr["enabled"]:
            self.ocr_switch.select()

        if config.background_settings["enabled"]:
            self.bg_switch.select()

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(self):

        from tkinter import messagebox

        photo_dir = self.photo_dir_entry.get().strip()
        signature_dir = self.signature_dir_entry.get().strip()

        if not photo_dir or not signature_dir:
            messagebox.showwarning(
                "Missing Folder",
                "Please set both the photos and signatures folders.",
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

        config.settings["gui"]["theme"] = \
            self.theme_menu.get().lower()

        import customtkinter as ctk
        ctk.set_appearance_mode(self.theme_menu.get())
        
        config.processing_mode = self.processing_modes[
            self.processing_mode_menu.get()
        ]

        config.settings["processing_mode"] = (
            config.processing_mode.value
        )

        config.settings["image"]["dpi"] = \
            int(self.dpi_entry.get())

        config.settings["image"]["photo_padding"] = \
            int(self.photo_padding_entry.get())

        config.settings["image"]["signature_padding"] = \
            int(self.signature_padding_entry.get())

        config.settings["image"]["clahe"] = \
            bool(self.clahe_switch.get())

        config.settings["image"]["sharpen"] = \
            bool(self.sharpen_switch.get())

        config.settings["ocr"]["enabled"] = \
            bool(self.ocr_switch.get())

        config.settings["ocr"]["language"] = \
            self.language_entry.get()

        config.settings["background_removal"]["enabled"] = \
            bool(self.bg_switch.get())

        print("Before save:")
        print(config.settings)
        config.save()

        self.destroy()