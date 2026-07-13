"""
===========================================================
OES ID CARD PDF-TO-REQUIREMENT-DOCUMENT EXTRACTOR
Application Entry Point

Author:
    Onyedikachi Nzute

Description
-----------
Launches the fully offline desktop application that scans
uploaded PDF/image files, extracts personnel photos and
signatures, removes their backgrounds, sharpens the photo,
and saves the two final files named after each personnel -
ready for use in ID card production.

SRS Reference (implemented in this codebase)
---------------------------------------------
 1. Scan document for photo, name, signature .... core/detector.py, vision/, ocr/
 2. Auto-crop on detection ....................... core/cropper.py
 3. Remove background from personnel photo ........ core/remover.py
 4. Clarify/sharpen the extracted photo ........... core/enhancer.py
 5. Remove background from personnel signature .... core/remover.py
 6. Produce two final named files per document .... core/exporter.py, core/namer.py
 7. Fully offline desktop application ............. app.py, gui/, models/
 8. Configurable photo/signature output dirs ...... gui/components/output_panel.py
 9. Multi-file batch input with progress bar ...... gui/main_window.py, core/processor.py
10. Official document authorship comment .......... this header, all modules
===========================================================
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path
from download_model import ensure_model_exists

#
# Ensure the application always runs with the project root
# as its working directory, regardless of how it was
# launched (double-click, shortcut, `python main.py` from
# elsewhere, or a frozen PyInstaller executable). This is
# required because config.py resolves settings.json and all
# output/temp/log/model directories relative to the cwd.
#
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent

os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#
# MOVED HERE: Now that working directory is 100% locked to the project root,
# run the check/download for u2net.onnx safely in the exact right directory.
#
ensure_model_exists()


def main() -> int:

    from utils.logger import LoggerManager, get_logger

    LoggerManager.configure()

    logger = get_logger(__name__)

    try:

        from app import App

        logger.info("Launching OES ID Card PDF to Req Doc Extractor.")

        application = App()

        application.mainloop()

        return 0

    except Exception:

        logger.exception("Fatal error during application startup.")

        traceback.print_exc()

        return 1


if __name__ == "__main__":
    sys.exit(main())
