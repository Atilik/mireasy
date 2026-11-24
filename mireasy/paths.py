"""Where mireasy keeps the downloaded Essentia model files (~45 MB).

Resolution order of :func:`models_dir` (first match wins):

1. ``$MIREASY_MODELS_DIR``, explicit override (CI uses it to keep the models
   inside its cache path).
2. ``<package>/models``, the pre-0.1 layout, honoured only when it already
   holds the embedding model, so source checkouts that downloaded earlier keep
   working.
3. The per-user cache folder, the default for ``pip install mireasy``:

   ========  =================================================================
   macOS     ``~/Library/Caches/mireasy/models``
   Linux     ``$XDG_CACHE_HOME/mireasy/models`` (default ``~/.cache/mireasy/models``)
   Windows   ``%LOCALAPPDATA%\\mireasy\\models``
   ========  =================================================================

This module has no third-party imports on purpose: the downloader must run
even when the heavy packages are missing or broken.
"""
import os
import sys

_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
EFFNET_FILE = "discogs-effnet-bs64-1.pb"
PACKAGE_MODELS_DIR = os.path.join(_PACKAGE_DIR, "models")
# The five synthetic demo songs shipped with the package (`mireasy --demo`).
SAMPLE_STIMULI_DIR = os.path.join(_PACKAGE_DIR, "sample_stimuli")


def user_cache_dir():
    """The per-user cache folder for mireasy (platform conventions, no deps)."""
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Caches")
    elif sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    else:
        base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return os.path.join(base, "mireasy")


def models_dir():
    """Folder that holds (or will receive) the Essentia model files."""
    override = os.environ.get("MIREASY_MODELS_DIR")
    if override:
        return os.path.abspath(os.path.expanduser(override))
    if os.path.isfile(os.path.join(PACKAGE_MODELS_DIR, EFFNET_FILE)):
        return PACKAGE_MODELS_DIR
    return os.path.join(user_cache_dir(), "models")
