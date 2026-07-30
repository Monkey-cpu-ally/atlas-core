from pathlib import Path

from routes import files


def test_initialize_upload_dir_falls_back_when_default_not_writable(monkeypatch, tmp_path):
    fallback_dir = tmp_path / "uploads"
    blocked_dir = Path("/blocked/uploads")

    monkeypatch.delenv("ATLAS_UPLOAD_DIR", raising=False)
    monkeypatch.setattr(files, "_DEFAULT_UPLOAD_DIR", blocked_dir)
    monkeypatch.setattr(files, "_FALLBACK_UPLOAD_DIR", fallback_dir)

    original_mkdir = Path.mkdir

    def fake_mkdir(self, parents=False, exist_ok=False):
        if self == blocked_dir:
            raise PermissionError("blocked")
        return original_mkdir(self, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)

    resolved = files._initialize_upload_dir()

    assert resolved == fallback_dir
    assert resolved.exists()


def test_initialize_upload_dir_honors_explicit_env(monkeypatch, tmp_path):
    configured_dir = tmp_path / "explicit-uploads"
    monkeypatch.setenv("ATLAS_UPLOAD_DIR", str(configured_dir))

    resolved = files._initialize_upload_dir()

    assert resolved == configured_dir
    assert configured_dir.exists()
