"""
===========================================================
OES ID Extractor
About Dialog

Author:
    Onyedikachi Nzute

Description
-----------
Displays application information including version,
author, technologies, and licensing information.
===========================================================
"""

from __future__ import annotations

import platform
import sys

import customtkinter as ctk


class AboutDialog(ctk.CTkToplevel):
    """
    About dialog for the application.
    """

    APP_NAME = "OES ID Extractor"

    VERSION = "1.0.0"

    AUTHOR = "Onyedikachi Nzute"

    DESCRIPTION = (
        "A fully offline desktop application for extracting "
        "employee photographs, signatures and names from "
        "PDFs and scanned identity documents."
    )

    TECHNOLOGIES = [
        "Python",
        "CustomTkinter",
        "OpenCV",
        "PyMuPDF",
        "Tesseract OCR",
        "ONNX Runtime",
        "Rembg",
        "Pillow",
    ]

    LICENSE = "Private - OES Energy Services"

    def __init__(self, master):

        super().__init__(master)

        self.title("About OES ID Extractor")

        self.transient(master)

        self.grab_set()

        self._create_widgets()

        self._layout_widgets()

        self.update_idletasks()

        width = max(620, self.winfo_reqwidth() + 20)
        height = max(650, self.winfo_reqheight() + 20)

        self.geometry(f"{width}x{height}")
        self.minsize(width, height)
        self.resizable(True, True)

    # ------------------------------------------------------
    # Widgets
    # ------------------------------------------------------

    def _create_widgets(self):

        self.title_label = ctk.CTkLabel(
            self,
            text=self.APP_NAME,
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )

        self.version_label = ctk.CTkLabel(
            self,
            text=f"Version {self.VERSION}",
        )

        self.author_title = ctk.CTkLabel(
            self,
            text="Author",
            font=ctk.CTkFont(
                weight="bold",
            ),
        )

        self.author_label = ctk.CTkLabel(
            self,
            text=self.AUTHOR,
        )

        self.description_title = ctk.CTkLabel(
            self,
            text="Description",
            font=ctk.CTkFont(
                weight="bold",
            ),
        )

        self.description_box = ctk.CTkTextbox(
            self,
            height=90,
        )

        self.description_box.insert(
            "1.0",
            self.DESCRIPTION,
        )

        self.description_box.configure(
            state="disabled",
        )

        self.tech_title = ctk.CTkLabel(
            self,
            text="Technologies",
            font=ctk.CTkFont(
                weight="bold",
            ),
        )

        self.tech_box = ctk.CTkTextbox(
            self,
            height=140,
        )

        self.tech_box.insert(
            "1.0",
            "\n".join(self.TECHNOLOGIES),
        )

        self.tech_box.configure(
            state="disabled",
        )

        self.system_title = ctk.CTkLabel(
            self,
            text="Runtime Information",
            font=ctk.CTkFont(
                weight="bold",
            ),
        )

        runtime = (
            f"Python : {platform.python_version()}\n"
            f"Platform : {platform.system()} {platform.release()}\n"
            f"Architecture : {platform.machine()}\n"
            f"Executable : {sys.executable}"
        )

        self.system_box = ctk.CTkTextbox(
            self,
            height=100,
        )

        self.system_box.insert(
            "1.0",
            runtime,
        )

        self.system_box.configure(
            state="disabled",
        )

        self.license_title = ctk.CTkLabel(
            self,
            text="License",
            font=ctk.CTkFont(
                weight="bold",
            ),
        )

        self.license_label = ctk.CTkLabel(
            self,
            text=self.LICENSE,
        )

        self.close_button = ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
        )

    # ------------------------------------------------------
    # Layout
    # ------------------------------------------------------

    def _layout_widgets(self):

        padx = 20

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        row = 0

        self.title_label.grid(
            row=row,
            column=0,
            pady=(20, 5),
        )

        row += 1

        self.version_label.grid(
            row=row,
            column=0,
            pady=(0, 25),
        )

        sections = [

            (self.author_title, self.author_label),

            (self.description_title,
             self.description_box),

            (self.tech_title,
             self.tech_box),

            (self.system_title,
             self.system_box),

            (self.license_title,
             self.license_label),

        ]

        for title, widget in sections:

            row += 1

            title.grid(
                row=row,
                column=0,
                padx=padx,
                sticky="w",
            )

            row += 1

            widget.grid(
                row=row,
                column=0,
                padx=padx,
                pady=(5, 15),
                sticky="ew",
            )

        row += 1

        self.close_button.grid(
            row=row,
            column=0,
            padx=20,
            pady=(10, 20),
            sticky="ew",
        )