import importlib
import sys
from pathlib import Path


MODULE_NAME = "utils.filesystem"


def _import_filesystem_module(monkeypatch, tmp_path):
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "bootstrap-uploads"))
    sys.modules.pop(MODULE_NAME, None)
    return importlib.import_module(MODULE_NAME)


def test_initialize_upload_dir_uses_configured_directory(monkeypatch, tmp_path):
    filesystem = _import_filesystem_module(monkeypatch, tmp_path)
    configured_dir = tmp_path / "configured-uploads"

    monkeypatch.setenv("UPLOAD_DIR", str(configured_dir))
    resolved_dir = Path(filesystem.initialize_upload_dir())

    assert resolved_dir == configured_dir
    assert resolved_dir.is_dir()


def test_initialize_upload_dir_falls_back_when_configured_directory_is_not_writable(monkeypatch, tmp_path):
    filesystem = _import_filesystem_module(monkeypatch, tmp_path)
    configured_dir = tmp_path / "blocked-uploads"
    fallback_dir = tmp_path / "atlas-uploads"
    original_mkdir = Path.mkdir

    def fake_mkdir(self, parents=False, exist_ok=False):
        if self == configured_dir:
            raise PermissionError("blocked")
        return original_mkdir(self, parents=parents, exist_ok=exist_ok)

    monkeypatch.setenv("UPLOAD_DIR", str(configured_dir))
    monkeypatch.setattr(filesystem.tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr(Path, "mkdir", fake_mkdir)

    resolved_dir = Path(filesystem.initialize_upload_dir())

    assert resolved_dir == fallback_dir
    assert resolved_dir.is_dir()
