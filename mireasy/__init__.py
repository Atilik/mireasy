"""
mireasy — an interactive music information retrieval (MIR) toolbox.

Library use (run Python from the repo folder):

    from mireasy import Stimulus, Session, Participant

Interactive shell:

    python -m mireasy <audio_file_or_folder>
"""

# Single source of truth for the version (pyproject.toml reads it statically).
# ".dev0" marks an unreleased build; the first release will be 0.1.0.
__version__ = "0.1.0.dev0"

__all__ = ["Stimulus", "Session", "Participant"]


def __getattr__(name):
    # Lazy exports: `import mireasy.dsp` (and the tests) stays lightweight —
    # the full ML stack (torch, TensorFlow, ...) loads only when one of these
    # classes is first used.
    if name in __all__:
        import importlib
        core = importlib.import_module(".mireasy", __name__)
        return getattr(core, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals()) + __all__)
