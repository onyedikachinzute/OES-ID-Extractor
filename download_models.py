from pathlib import Path
import json
import urllib.request
import zipfile
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:

    def __init__(self):

        self.models_dir = Path(config.models_dir)

        self.manifest_path = self.models_dir / "model_manifest.json"

        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:

        if not self.manifest_path.exists():

            raise FileNotFoundError(
                f"Manifest not found:\n{self.manifest_path}"
            )

        with open(self.manifest_path, "r", encoding="utf-8") as f:

            return json.load(f)
    
    def get_model(
        self,
        name: str,
    ) -> dict:

        return self.manifest["models"][name]
    
    def model_path(
        self,
        name: str,
    ) -> Path:

        model = self.get_model(name)

        if model["type"] == "file":

            return self.models_dir / model["filename"]

        elif model["type"] == "zip":

            return self.models_dir / model["folder"]

        elif model["type"] == "huggingface":

            return self.models_dir / model["folder"]

        raise ValueError(
            f"Unknown model type: {model['type']}"
        )
    
    def model_exists(
        self,
        name: str,
    ) -> bool:

        return self.model_path(name).exists()

    def _download_file(
        self,
        url: str,
        destination: Path,
    ) -> None:

        logger.info(
            "Downloading %s",
            destination.name,
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            urllib.request.urlretrieve(
                url,
                destination,
            )

        except Exception:

            logger.exception(
                "Failed downloading %s",
                destination.name,
            )

            raise

        logger.info(
            "Finished downloading %s",
            destination.name,
        )
        
    def _extract_zip(
        self,
        archive: Path,
        destination: Path,
    ) -> None:

        logger.info(
            "Extracting %s",
            archive.name,
        )

        with zipfile.ZipFile(
            archive,
            "r",
        ) as zip_file:

            zip_file.extractall(
                destination,
            )

        archive.unlink(
            missing_ok=True,
        )

        logger.info(
            "Extraction complete."
        )
    
    def ensure_model(
        self,
        name: str,
    ) -> None:

        model = self.get_model(name)

        path = self.model_path(name)

        if path.exists():

            logger.info(
                "'%s' already installed.",
                name,
            )

            return

        logger.info(
            "Installing '%s'...",
            name,
        )

        if model["type"] == "file":

            self._download_file(
                model["url"],
                path,
            )

        else:

            raise ValueError(
                f"Unknown model type: {model['type']}"
            )
            
        
    def ensure_detector_exists(self):

        self.ensure_model(
            "detector",
        )


    def ensure_segmenter_exists(self):

        self.ensure_model(
            "segmenter",
        )


    def ensure_name_detector_exists(self):

        self.ensure_model(
            "name_detector",
        )


    
    def ensure_all_models(self):

        self.ensure_detector_exists()

        self.ensure_segmenter_exists()

        self.ensure_name_detector_exists()
