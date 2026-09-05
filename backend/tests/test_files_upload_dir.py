import importlib
import sys


def _reload_files_route(monkeypatch, upload_dir):
    monkeypatch.setenv("ATLAS_UPLOAD_DIR", str(upload_dir))
    sys.modules.pop("routes.files", None)
    return importlib.import_module("routes.files")


def test_upload_directory_uses_configured_writable_path(monkeypatch, tmp_path):
    upload_dir = tmp_path / "atlas-uploads"
    files_route = _reload_files_route(monkeypatch, upload_dir)

    assert files_route.UPLOAD_DIR == str(upload_dir.resolve())
    assert upload_dir.is_dir()


def test_stored_file_path_is_confined_to_upload_root(monkeypatch, tmp_path):
    upload_dir = tmp_path / "atlas-uploads"
    files_route = _reload_files_route(monkeypatch, upload_dir)

    expected = upload_dir.resolve() / "file_123.txt"
    assert files_route._stored_file_path("file_123.txt") == str(expected)


def test_default_upload_directory_does_not_require_app_root(monkeypatch, tmp_path):
    monkeypatch.delenv("ATLAS_UPLOAD_DIR", raising=False)
    monkeypatch.delenv("UPLOAD_DIR", raising=False)
    monkeypatch.setattr("tempfile.gettempdir", lambda: str(tmp_path))
    sys.modules.pop("routes.files", None)
    files_route = importlib.import_module("routes.files")

    expected = (tmp_path / "atlas" / "uploads").resolve()
    assert files_route.UPLOAD_DIR == str(expected)
    assert expected.is_dir()
