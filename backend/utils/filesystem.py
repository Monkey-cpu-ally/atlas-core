import logging
import os
import tempfile
from pathlib import Path


logger = logging.getLogger(__name__)


def initialize_upload_dir() -> str:
    configured_dir = Path(os.environ.get("UPLOAD_DIR", "/app/uploads"))
    try:
        configured_dir.mkdir(parents=True, exist_ok=True)
        return str(configured_dir)
    except PermissionError:
        fallback_dir = Path(tempfile.gettempdir()) / "atlas-uploads"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        logger.warning(
            "Upload directory %s is not writable; using fallback %s",
            configured_dir,
            fallback_dir,
        )
        return str(fallback_dir)
