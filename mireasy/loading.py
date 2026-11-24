"""A loading bar for the start of the ``mireasy`` command.

Starting MIReasy takes a few seconds, and up to a minute the first time after
installing, because the analysis libraries are large. The bar shows which one
is loading, so the wait does not look like a crash. It is drawn only in a
terminal, never when the output goes to a file or to another program.
"""
import contextlib
import sys

# The libraries that take the time at start, and the name shown for each.
STEPS = {
    "librosa": "audio tools",
    "matplotlib": "plots",
    "torch": "PyTorch",
    "beat_this": "beat tracker",
    "demucs": "Demucs",
    "essentia": "Essentia",
}
WIDTH = 24


class _Watcher:
    """An import hook that loads nothing itself. It only reports when one of
    the libraries in STEPS starts to load."""

    def __init__(self, on_start):
        self._waiting = dict(STEPS)
        self._on_start = on_start

    def find_spec(self, fullname, path=None, target=None):
        label = self._waiting.pop(fullname, None)
        if label is not None:
            self._on_start(label)
        return None


@contextlib.contextmanager
def loading_bar(stream=None):
    """Show a loading bar on ``stream`` (default: the screen) while the body runs."""
    stream = sys.stdout if stream is None else stream
    if stream is None or not stream.isatty():
        yield
        return

    started = []

    def draw(label):
        started.append(label)
        filled = WIDTH * (len(started) - 1) // len(STEPS)
        bar = "#" * filled + "-" * (WIDTH - filled)
        # "\033[K" erases the rest of the line. The last "\r" leaves the cursor
        # at the start, so a message printed by a library replaces the bar.
        stream.write(f"\r  [{bar}] loading {label}\033[K\r")
        stream.flush()

    stream.write("Starting MIReasy. The first start after installing can take up to a minute.\n")
    stream.flush()
    watcher = _Watcher(draw)
    sys.meta_path.insert(0, watcher)
    try:
        yield
    finally:
        sys.meta_path.remove(watcher)
        stream.write("\r\033[K")
        stream.flush()
