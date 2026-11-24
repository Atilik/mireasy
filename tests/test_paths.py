"""Where the Essentia models live (mireasy/paths.py), the piece that makes a
non-editable `pip install mireasy` work (issue #21). Offline and fast."""
import os
import sys

from mireasy import paths


def test_env_override_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("MIREASY_MODELS_DIR", str(tmp_path / "anywhere"))
    assert paths.models_dir() == str(tmp_path / "anywhere")


def test_env_override_expands_the_home_tilde(monkeypatch):
    monkeypatch.setenv("MIREASY_MODELS_DIR", "~/mireasy-models")
    assert paths.models_dir() == os.path.expanduser("~/mireasy-models")


def test_package_folder_is_used_only_when_it_already_holds_the_models(monkeypatch, tmp_path):
    monkeypatch.delenv("MIREASY_MODELS_DIR", raising=False)
    pkg = tmp_path / "models"
    pkg.mkdir()
    monkeypatch.setattr(paths, "PACKAGE_MODELS_DIR", str(pkg))
    assert paths.models_dir() != str(pkg)              # empty folder: not chosen
    (pkg / paths.EFFNET_FILE).write_bytes(b"x")
    assert paths.models_dir() == str(pkg)              # pre-0.1 layout: kept


def test_user_cache_follows_platform_conventions(monkeypatch, tmp_path):
    monkeypatch.delenv("MIREASY_MODELS_DIR", raising=False)
    monkeypatch.setattr(paths, "PACKAGE_MODELS_DIR", str(tmp_path / "nope"))

    monkeypatch.setattr(sys, "platform", "darwin")
    assert paths.models_dir() == os.path.expanduser("~/Library/Caches/mireasy/models")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    assert paths.models_dir() == os.path.expanduser("~/.cache/mireasy/models")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))
    assert paths.models_dir() == str(tmp_path / "xdg" / "mireasy" / "models")

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    assert paths.models_dir() == str(tmp_path / "local" / "mireasy" / "models")


def test_genre_resolves_model_files_through_paths(monkeypatch, tmp_path):
    # genre.py must look in models_dir() at call time, not in a path frozen at import.
    from mireasy import genre
    monkeypatch.setenv("MIREASY_MODELS_DIR", str(tmp_path))
    assert genre._model_path("x.pb") == str(tmp_path / "x.pb")
