"""
===========================================================
OES ID Extractor
Configuration Manager

Author:
    Onyedikachi Nzute

Description
-----------
Loads and validates the application's settings and exposes
configuration values throughout the application.

Where settings actually live
------------------------------
This is the single most important thing to get right for a
packaged desktop app: the live, WRITABLE settings file lives
in a per-user application-data directory, never next to the
executable itself.

    Windows : %APPDATA%\\OES ID Extractor\\settings.json
    macOS   : ~/Library/Application Support/OES ID Extractor/
    Linux   : ~/.config/OES ID Extractor/

If the app is installed to "C:\\Program Files\\..." (the
normal install location on Windows), writing next to the
executable requires admin rights and silently fails for a
standard user - which would have broken every "change my
output folder" action in Settings, and even first launch
itself once packaged. Reading/writing only in the user's own
per-user app-data folder avoids that entirely and needs no
elevated permissions.

On first run (no settings file yet at that location), this
seeds a fresh one from built-in defaults - copying a
bundled template settings.json next to the app if one is
present (useful for development), otherwise using in-code
defaults. Either way, a `first_run` flag is set so the GUI
can show a one-time setup wizard for the photo/signature
output folders.

All project-wide paths should be accessed through this class
instead of hardcoding directories.
===========================================================
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from enum import Enum
APP_DIR_NAME = "OES ID Extractor"


def _user_config_dir() -> Path:
    """
    Per-user, per-OS writable application-data directory.
    """

    if sys.platform == "win32":

        base = os.environ.get("APPDATA")

        if base:
            return Path(base) / APP_DIR_NAME

        return Path.home() / "AppData" / "Roaming" / APP_DIR_NAME

    if sys.platform == "darwin":

        return Path.home() / "Library" / "Application Support" / APP_DIR_NAME

    return Path.home() / ".config" / APP_DIR_NAME.lower().replace(" ", "_")


def _default_documents_dir() -> Path:
    """
    A sensible, discoverable default location for the actual
    exported photos/signatures - the user's Documents folder,
    which exists and is writable out of the box on Windows,
    macOS, and Linux without any special-casing.
    """

    documents = Path.home() / "Documents"

    if documents.exists():
        return documents

    return Path.home()


def _default_settings() -> dict:

    docs = _default_documents_dir() / APP_DIR_NAME

    return {
        "first_run": True,
        "processing_mode": "full",
        "photo_output_dir": str(docs / "Photos"),
        "signature_output_dir": str(docs / "Signatures"),
        "temp_dir": str(_user_config_dir() / "temp"),
        "log_dir": str(_user_config_dir() / "logs"),
        "models_dir": str(_user_config_dir() / "models"),
        "tesseract_cmd": "",
        "supported_extensions": [
            ".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff",
        ],
        "image": {
            "dpi": 300,
            "photo_padding": 20,
            "signature_padding": 10,
            
            
            "sharpen": True,
            "clahe": True,
            "denoise": True,
            "upscale_small_crops": True,
            
            "standardize_photo_canvas": True,
            "standard_photo_width": 600,
            "standard_photo_height": 800,
        },
        
        "ocr": {
            "enabled": True,
            "language": "eng",
        },
        "background_removal": {
            "enabled": True,
        },
                
        "gui": {
            "theme": "dark",
            "window_width": 1200,
            "window_height": 700,
        },
    }

class ProcessingMode(Enum):
    """
    Enum for processing modes.
    """

    FULL = "full"
    CROP_ONLY = "crop_only"

class Config:
    """
    Global configuration manager.
    """

    def __init__(self):

        self.config_dir = _user_config_dir()

        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.settings_file = self.config_dir / "settings.json"

        self.settings = self._load_or_create_settings()

        self.processing_mode = ProcessingMode(
            self.settings.get("processing_mode", "full")
        )
        # --------------------------------------------------
        # Vision
        # --------------------------------------------------
        
        self.yolo_model = "detector.pt"
        self.segment_model = "segment.pt"
        
        self.max_processing_dimension = 1600

        self.yolo_confidence = 0.35

        self.min_contour_area = 500

        self.signature_min_aspect_ratio = 2.0

        self.signature_max_aspect_ratio = 12.0
        
        self.segmentation_confidence = 0.35
        self.segmentation_imgsz = 960
        self.device = 0

        self._initialize_paths()

    # ------------------------------------------------------
    # Loading / first-run seeding
    # ------------------------------------------------------

    def _load_or_create_settings(self) -> dict:

        if self.settings_file.exists():

            with open(self.settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # Fill in any keys added by a newer app version
            # without discarding the user's existing choices.
            defaults = _default_settings()

            for key, value in settings.items():

                if (
                    key in defaults
                    and isinstance(defaults[key], dict)
                    and isinstance(value, dict)
                ):
                    defaults[key].update(value)

                else:
                    defaults[key] = value
                    
            self._write_settings(defaults)

            return defaults

        #
        # First run at this machine/user account: seed from
        # a bundled template if one ships alongside the app
        # (handy in development), otherwise pure in-code
        # defaults.
        #
        settings = _default_settings()

        bundled_template = self._bundled_template_path()

        if bundled_template and bundled_template.exists():

            try:

                with open(bundled_template, "r", encoding="utf-8") as f:
                    template = json.load(f)

                for key in (
                    "image", "ocr", "background_removal", "gui",
                    "supported_extensions",
                ):
                    if key in template:
                        settings[key] = template[key]

            except (json.JSONDecodeError, OSError):
                pass

        settings["first_run"] = True

        self._write_settings(settings)

        return settings

    def _bundled_template_path(self) -> Path | None:

        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent / "settings.json"

        return Path(__file__).resolve().parent / "settings.json"

    def _write_settings(self, settings: dict) -> None:

        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

    # ------------------------------------------------------
    # Paths
    # ------------------------------------------------------

    def _initialize_paths(self):

        self.photo_output_dir = Path(self.settings["photo_output_dir"])

        self.signature_output_dir = Path(self.settings["signature_output_dir"])

        self.temp_dir = Path(self.settings["temp_dir"])

        self.log_dir = Path(self.settings["log_dir"])

        #
        # Directory holding offline model assets (yolo.pt,
        # haarcascade.xml). Background removal no longer
        # needs a model file - see core/remover.py.
        #
        print("CONFIG FILE:", __file__)
        self.models_dir = Path(
            self.settings.get("models_dir", str(self.config_dir / "models"))
        )
        
        # --------------------------------------------------
        # Development override
        # --------------------------------------------------

        project_root = Path(__file__).resolve().parent

        development_models = project_root / "models"
        print("PROJECT ROOT:", project_root)
        print("DEV MODELS:", development_models)
        print("EXISTS:", development_models.exists())

        logger = __import__("logging").getLogger(__name__)

        print(f"config.py = {Path(__file__).resolve()}")
        print(f"project_root = {project_root}")
        print(f"development_models = {development_models}")
        print(f"exists = {development_models.exists()}")
        print("=" * 60)
        print("models_dir =", self.models_dir)
        print("=" * 60)


        if development_models.exists():

            self.models_dir = development_models
    
    

        for directory in (
            self.photo_output_dir,
            self.signature_output_dir,
            self.temp_dir,
            self.log_dir,
            self.models_dir,
        ):

            try:
                directory.mkdir(parents=True, exist_ok=True)

            except OSError as e:
                raise OSError(
                    f"Could not create required directory '{directory}': {e}\n"
                    f"If this is a chosen output folder, pick a different "
                    f"location in Settings."
                ) from e

    # ------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------

    @property
    def is_first_run(self) -> bool:

        return bool(self.settings.get("first_run", False))

    def complete_first_run(self) -> None:

        self.set("first_run", False)

    @property
    def supported_extensions(self):

        return self.settings["supported_extensions"]

    @property
    def image_settings(self):

        return self.settings["image"]

    @property
    def gui_settings(self):

        return self.settings["gui"]

    @property
    def ocr_settings(self):

        return self.settings["ocr"]

    @property
    def background_settings(self):

        return self.settings["background_removal"]

    def save(self):

        self._write_settings(self.settings)

    def get(self, key: str, default: Any = None):

        return self.settings.get(key, default)

    def set(self, key: str, value: Any):

        self.settings[key] = value

        self.save()

        self._initialize_paths()


config = Config()

