"""Tests for the model downloader (mireasy/download_models.py, installed as the
`mireasy-download-models` command) and the root download_models.py wrapper.

Network tests, gated behind MIREASY_RUN_SLOW=1 like the model tests, so the
default suite stays offline-safe. Catches upstream URL rot at essentia.upf.edu
before a fresh user does.
"""
import importlib.util
import io
import json
import os
import urllib.request
from contextlib import redirect_stdout

import pytest

from conftest import RUN_SLOW

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NETWORK = pytest.mark.skipif(
    not RUN_SLOW, reason="set MIREASY_RUN_SLOW=1 to run network tests")


def test_root_script_is_a_wrapper_around_the_package_command():
    # The installation page documents `python download_models.py`; the real code is
    # the package module, so the two can never drift apart.
    spec = importlib.util.spec_from_file_location(
        "download_models_wrapper", os.path.join(REPO, "download_models.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from mireasy import download_models as dm
    assert mod.main is dm.main


def test_downloader_lists_all_files_genre_expects():
    # Offline consistency check: every model genre.py will look for must be
    # in the download list (drift here = FileNotFoundError for fresh users)
    from mireasy import download_models as dm
    from mireasy import genre, paths
    listed = {name for _, name in dm.FILES}
    expected = {paths.EFFNET_FILE, genre._CREPE_FILE}
    for base in genre._HEAD_FILES.values():
        expected.add(f"{base}.pb")
        expected.add(f"{base}.json")
    assert expected <= listed


def test_downloader_imports_without_the_heavy_stack():
    # The command must work even when torch/essentia are broken: importing it
    # must not pull them in.
    import subprocess
    import sys
    out = subprocess.run(
        [sys.executable, "-c",
         "import sys, mireasy.download_models; "
         "print(sorted(m for m in ('essentia', 'torch', 'tensorflow', 'librosa') if m in sys.modules))"],
        capture_output=True, text=True, cwd=REPO, check=True)
    assert out.stdout.strip() == "[]", out.stdout


@NETWORK
def test_all_model_urls_alive():
    from mireasy import download_models as dm
    for path, name in dm.FILES:
        req = urllib.request.Request(f"{dm.BASE}/{path}", method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as resp:
            assert resp.status == 200, name
            assert int(resp.headers.get("Content-Length", 0)) > 0, name


@NETWORK
def test_download_and_skip_logic(tmp_path, monkeypatch):
    # Real download of the smallest file (a label .json), then the skip path.
    # The destination follows $MIREASY_MODELS_DIR, exactly like a user override.
    from mireasy import download_models as dm
    monkeypatch.setenv("MIREASY_MODELS_DIR", str(tmp_path))
    monkeypatch.setattr(dm, "FILES", [f for f in dm.FILES if f[1].endswith(".json")][:1])

    buf = io.StringIO()
    with redirect_stdout(buf):
        assert dm.main() == 0
    name = dm.FILES[0][1]
    assert "[get ]" in buf.getvalue() and str(tmp_path) in buf.getvalue()
    with open(tmp_path / name) as f:
        assert "classes" in json.load(f)          # valid Essentia label file

    buf = io.StringIO()
    with redirect_stdout(buf):
        assert dm.main() == 0                     # second run: skip, still ok
    assert "[skip]" in buf.getvalue()
