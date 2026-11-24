"""Tests for the loading bar of the `mireasy` command (mireasy/loading.py and
mireasy/__main__.py). The bar is drawn in a terminal only, names the library
that is loading, and leaves nothing behind when the start is over.
"""
import importlib
import importlib.util
import io
import os
import pty
import select
import subprocess
import sys
import time

import pytest

from mireasy import loading

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Terminal(io.StringIO):
    """A text stream that says it is a terminal."""

    def isatty(self):
        return True


@pytest.fixture
def two_libraries(tmp_path, monkeypatch):
    """Two small importable modules that stand in for the big libraries."""
    names = {"mireasy_bar_test_one": "first library", "mireasy_bar_test_two": "second library"}
    for name in names:
        (tmp_path / f"{name}.py").write_text("VALUE = 1\n")
        monkeypatch.delitem(sys.modules, name, raising=False)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(loading, "STEPS", names)
    yield list(names)
    for name in names:
        sys.modules.pop(name, None)


def test_bar_names_each_library_when_it_starts_to_load(two_libraries):
    screen = Terminal()
    with loading.loading_bar(screen):
        after_start = screen.getvalue()
        importlib.import_module(two_libraries[0])
        after_one = screen.getvalue()
        importlib.import_module(two_libraries[1])
        after_two = screen.getvalue()

    half = "#" * (loading.WIDTH // 2) + "-" * (loading.WIDTH - loading.WIDTH // 2)
    assert after_start == ("Starting MIReasy. The first start after installing "
                           "can take up to a minute.\n")
    assert after_one.endswith(f"[{'-' * loading.WIDTH}] loading first library\033[K\r")
    assert after_two.endswith(f"[{half}] loading second library\033[K\r")
    assert screen.getvalue().endswith("\r\033[K"), "the bar must be erased at the end"


def test_a_library_is_named_only_once(two_libraries):
    screen = Terminal()
    with loading.loading_bar(screen):
        importlib.import_module(two_libraries[0])
        importlib.reload(sys.modules[two_libraries[0]])
        importlib.import_module(two_libraries[0])
    assert screen.getvalue().count("loading first library") == 1


def test_nothing_is_drawn_when_the_output_is_not_a_terminal(two_libraries):
    hooks = list(sys.meta_path)
    not_a_terminal = io.StringIO()
    with loading.loading_bar(not_a_terminal):
        assert sys.meta_path == hooks
        importlib.import_module(two_libraries[0])
    assert not_a_terminal.getvalue() == ""


def test_no_screen_at_all_is_fine(monkeypatch):
    monkeypatch.setattr(sys, "stdout", None)
    with loading.loading_bar():
        pass


def test_the_import_hook_is_removed_even_when_loading_fails(two_libraries):
    hooks = list(sys.meta_path)
    screen = Terminal()
    with pytest.raises(ModuleNotFoundError):
        with loading.loading_bar(screen):
            assert len(sys.meta_path) == len(hooks) + 1
            importlib.import_module("mireasy_bar_test_missing")
    assert sys.meta_path == hooks
    assert screen.getvalue().endswith("\r\033[K")


def test_the_watched_libraries_are_the_ones_mireasy_loads():
    # Every name in STEPS must be a real top-level package MIReasy depends on,
    # or its step would never light up.
    for name in loading.STEPS:
        assert importlib.util.find_spec(name) is not None, f"{name} is not installed"


def test_command_entry_point_opens_the_shell_with_its_arguments(monkeypatch):
    import mireasy.mireasy as core
    from mireasy.__main__ import main
    seen = []
    monkeypatch.setattr(core, "main", lambda argv=None: seen.append(argv) or 7)
    assert main(["some_folder"]) == 7
    assert seen == [["some_folder"]]


def test_the_command_shows_the_bar_in_a_real_terminal():
    # The real thing: `python -m mireasy` with a terminal (a pty) as its screen.
    master, slave = pty.openpty()
    proc = subprocess.Popen([sys.executable, "-W", "ignore", "-m", "mireasy", "--help"],
                            cwd=REPO, stdin=subprocess.DEVNULL, stdout=slave,
                            stderr=subprocess.DEVNULL)
    os.close(slave)
    shown, deadline = b"", time.time() + 300
    while time.time() < deadline:
        ready, _, _ = select.select([master], [], [], 5)
        if not ready:
            if proc.poll() is not None:
                break
            continue
        try:
            data = os.read(master, 4096)
        except OSError:              # Linux reports the closed terminal this way
            break
        if not data:
            break
        shown += data
    os.close(master)
    assert proc.wait(timeout=60) == 1
    text = shown.decode(errors="replace")
    for step in ("Starting MIReasy", "loading PyTorch", "loading Essentia", "Usage: mireasy"):
        assert step in text, f"{step!r} did not appear on the terminal"
    assert text.index("loading Essentia") < text.index("Usage: mireasy")
