from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

from download_models import ModelManager


#
# Ensure the application always runs from its own directory.
#
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent

os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))





def main() -> int:

    from utils.logger import LoggerManager, get_logger

    LoggerManager.configure()

    logger = get_logger(__name__)
    
    #
    # Ensure all required AI models exist before importing the
    # rest of the application.
    #
    ModelManager().ensure_all_models()

    try:

        from app import App

        logger.info(
            "Launching OES ID Card PDF to Requirement Document Extractor."
        )

        application = App()

        application.mainloop()

        return 0

    except Exception:

        logger.exception(
            "Fatal error during application startup."
        )

        traceback.print_exc()

        return 1


if __name__ == "__main__":

    sys.exit(main())