import io
from pathlib import Path

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from routes import files as files_routes


def test_resolve_upload_dir_honors_configured_path(tmp_path, monkeypatch):
    target = tmp_path / "uploads"
    monkeypatch.setenv("UPLOAD_DIR", str(target))

    resolved = Path(files_routes._resolve_upload_dir())

    assert resolved == target
    assert target.is_dir()


@pytest.mark.asyncio
async def test_upload_file_preserves_413_for_oversized_upload(monkeypatch):
    monkeypatch.setattr(files_routes, "MAX_FILE_SIZE", 1)
    upload = UploadFile(filename="too-big.txt", file=io.BytesIO(b"xx"))

    with pytest.raises(HTTPException) as exc:
        await files_routes.upload_file(upload)

    assert exc.value.status_code == 413
