"""Tests for mireasy/separate.py.

Default tests exercise the fast paths: input validation, audio loading and
how the model is loaded (with stand-ins, no model). The real Demucs separation
runs only with MIREASY_RUN_SLOW=1 AND the model already on disk.
"""
import glob
import os
import shutil
import subprocess
import sys
import types

import librosa
import numpy as np
import pytest
import soundfile as sf

from mireasy.separate import separate, _load_audio
from conftest import make_clicks, RUN_SLOW


def _demucs_model_on_disk():
    """Demucs 4.1 keeps htdemucs in the Hugging Face cache, Demucs 4.0 in the torch cache."""
    try:
        import demucs.hf  # noqa: F401
        from huggingface_hub import try_to_load_from_cache
    except ImportError:
        return bool(glob.glob(os.path.join(
            os.path.expanduser("~"), ".cache", "torch", "hub", "checkpoints", "*.th")))
    return isinstance(try_to_load_from_cache("adefossez/HTDemucs", "htdemucs.yaml"), str)


SLOW = pytest.mark.skipif(
    not (RUN_SLOW and _demucs_model_on_disk()),
    reason="set MIREASY_RUN_SLOW=1 (and have htdemucs on disk) to run Demucs",
)


@pytest.fixture
def ffmpeg(monkeypatch):
    """Put the env's ffmpeg on PATH (as `conda activate` does), .m4a
    decoding goes through it. Skips if no ffmpeg is available."""
    env_bin = os.path.dirname(sys.executable)
    if os.path.exists(os.path.join(env_bin, "ffmpeg")):
        monkeypatch.setenv("PATH", env_bin + os.pathsep + os.environ.get("PATH", ""))
    exe = shutil.which("ffmpeg")
    if exe is None:
        pytest.skip("ffmpeg not available")
    return exe


@pytest.fixture
def clicks_48k(tmp_path):
    """3 s stereo click track at 48 kHz (clicks every 0.5 s)."""
    y = make_clicks(np.arange(0.25, 2.75, 0.5), 3.0, sr=48000)
    p = str(tmp_path / "clicks_48k.wav")
    sf.write(p, np.stack([y, y], axis=1), 48000)
    return p


@pytest.fixture
def clicks_m4a(tmp_path, clicks_48k, ffmpeg):
    p = str(tmp_path / "clicks.m4a")
    subprocess.run([ffmpeg, "-loglevel", "error", "-y", "-i", clicks_48k,
                    "-c:a", "aac", p], check=True)
    return p


# ── validation (fast, no model) ─────────────────────────────

def test_separate_rejects_unknown_target(sine_wav):
    # Regression (#1 first-pass): substring matching allowed typos through;
    # validation now happens before any audio/model loading.
    with pytest.raises(ValueError, match="Unknown target source"):
        separate(sine_wav, target_source="drum")


def test_separate_rejects_none_target(sine_wav):
    with pytest.raises(ValueError):
        separate(sine_wav, target_source=None)


def test_separate_rejects_unsupported_extension(tmp_path):
    bad = tmp_path / "audio.txt"
    bad.write_text("nope")
    with pytest.raises(ValueError, match="Unknown target source|Unsupported audio format"):
        separate(str(bad), target_source="drums")


# ── audio loading for the model (fast, no model) ────────────

def test_load_audio_resamples_to_model_rate(clicks_48k):
    # Regression: 48 kHz audio was fed to the 44.1 kHz model unresampled
    wav = _load_audio(clicks_48k, 44100, 2)
    assert wav.dtype.is_floating_point and wav.shape == (2, 3 * 44100)


def test_load_audio_mono_becomes_stereo(sine_wav):
    wav = _load_audio(sine_wav, 44100, 2)
    assert wav.shape[0] == 2
    assert np.array_equal(wav[0].numpy(), wav[1].numpy())


def test_load_audio_m4a(clicks_m4a):
    # Regression: .m4a could not be decoded on the separation path
    wav = _load_audio(clicks_m4a, 44100, 2)
    assert wav.shape[0] == 2
    assert abs(wav.shape[1] - 3 * 44100) < 0.1 * 44100    # AAC adds a little padding


# ── reproducibility contract (fast, no model) ───────────────

def test_separate_disables_random_shifts(sine_wav, monkeypatch):
    # Regression: Demucs's default shifts=1 applies a random 0–0.5 s time
    # shift before separating, so identical input gave slightly different
    # stems, and syncopation scores that drifted a few points between runs.
    # Capture the real call's arguments with a stand-in model + apply_model.
    import torch
    import mireasy.separate as sep

    class FakeModel:
        samplerate, audio_channels = 44100, 2
        sources = ["drums", "bass", "other", "vocals"]
        def eval(self): return self
        def to(self, device): return self

    captured = {}
    def fake_apply_model(model, mix, **kwargs):
        captured.update(kwargs)
        return torch.zeros(1, len(model.sources), *mix.shape[1:])

    monkeypatch.setattr(sep, "_MODEL", FakeModel())
    monkeypatch.setattr(sep, "apply_model", fake_apply_model)
    sep.separate(sine_wav, target_source="drums")
    assert captured.get("shifts") == 0, \
        f"apply_model must be called with shifts=0 for reproducible stems, got {captured}"


# ── loading the model (fast, stand-ins for Demucs and the hub) ──

class _FakeModel:
    samplerate, audio_channels = 44100, 2
    sources = ["drums", "bass", "other", "vocals"]
    def eval(self): return self
    def to(self, device): return self


def _fake_hub(monkeypatch, on_disk):
    """Stand-ins for huggingface_hub and demucs.hf (Demucs 4.1). Returns the
    fake hub module and the list of download calls it received."""
    calls = []

    def hf_hub_download(repo_id, filename, **kwargs):
        calls.append((filename, kwargs))
        if kwargs.get("local_files_only") and not on_disk:
            raise FileNotFoundError(filename)
        return f"/cache/{filename}"

    def get_hf_model(name):
        from huggingface_hub import hf_hub_download     # looked up at call time, as Demucs does
        hf_hub_download("adefossez/HTDemucs", f"{name}.yaml")
        hf_hub_download("adefossez/HTDemucs", "955717e8.safetensors")
        return "model from the hub files"

    hub = types.ModuleType("huggingface_hub")
    hub.hf_hub_download = hf_hub_download
    hf = types.ModuleType("demucs.hf")
    hf.get_hf_model = get_hf_model
    monkeypatch.setitem(sys.modules, "huggingface_hub", hub)
    monkeypatch.setitem(sys.modules, "demucs.hf", hf)
    return hub, calls


def test_model_on_disk_is_loaded_without_asking_the_hub(monkeypatch):
    # Demucs 4.1 asks the Hugging Face hub about its model file on every load.
    # With the file on disk nothing may be asked: every call is disk-only.
    import mireasy.separate as sep
    hub, calls = _fake_hub(monkeypatch, on_disk=True)
    original = hub.hf_hub_download
    monkeypatch.setattr(sep, "get_model", lambda name: pytest.fail("must not go online"))

    assert sep._load_model() == "model from the hub files"
    assert [name for name, _ in calls] == ["htdemucs.yaml", "955717e8.safetensors"]
    assert all(kwargs == {"local_files_only": True} for _, kwargs in calls)
    assert hub.hf_hub_download is original, "the hub's download function was not put back"


def test_model_not_on_disk_is_downloaded_the_usual_way(monkeypatch):
    import mireasy.separate as sep
    hub, calls = _fake_hub(monkeypatch, on_disk=False)
    original = hub.hf_hub_download
    asked = []
    monkeypatch.setattr(sep, "get_model", lambda name: asked.append(name) or "model after download")

    assert sep._load_model() == "model after download"
    assert asked == ["htdemucs"]
    assert hub.hf_hub_download is original, "the hub's download function was not put back"


def test_demucs_without_the_hub_loads_as_before(monkeypatch):
    # Demucs 4.0 has no demucs.hf module: one file in the torch cache.
    import mireasy.separate as sep
    monkeypatch.setitem(sys.modules, "demucs.hf", None)      # makes the import fail
    monkeypatch.setattr(sep, "get_model", lambda name: f"{name} from the torch cache")
    assert sep._load_model() == "htdemucs from the torch cache"


def test_the_model_is_loaded_once_and_reused(sine_wav, monkeypatch):
    import torch
    import mireasy.separate as sep
    loads = []
    monkeypatch.setattr(sep, "_MODEL", None)
    monkeypatch.setattr(sep, "_load_model", lambda: loads.append(1) or _FakeModel())
    monkeypatch.setattr(sep, "apply_model",
                        lambda model, mix, **kw: torch.zeros(1, len(model.sources), *mix.shape[1:]))
    sep.separate(sine_wav, target_source="drums")
    sep.separate(sine_wav, target_source="drums")
    assert loads == [1]


# ── full separation (slow, model required) ──────────────────

@pytest.mark.skipif(not (RUN_SLOW and os.environ.get("CI")),
                    reason="only for the slow tier on CI")
def test_on_ci_the_demucs_model_is_on_disk():
    # Without the model the tests below only skip, and a skip is not a failure.
    # On CI that would let the slow tier pass without testing any separation,
    # so there a missing model must be an error.
    assert _demucs_model_on_disk(), \
        "htdemucs is not on disk, so the Demucs tests would be skipped (see 'Warm model caches')"


@SLOW
def test_model_on_disk_loads_without_any_internet_lookup(monkeypatch):
    # The real thing: with htdemucs on disk, loading it must not look up a
    # single internet address (Demucs 4.1 would ask huggingface.co).
    import socket
    import mireasy.separate as sep
    asked = []
    lookup = socket.getaddrinfo

    def spy(host, *args, **kwargs):
        asked.append(host)
        return lookup(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", spy)
    assert sep._load_model() is not None
    assert asked == []


@SLOW
def test_separate_drums_end_to_end(click_wav):
    target, accompaniment, sr = separate(click_wav, target_source="drums")
    assert isinstance(target, np.ndarray) and target.ndim == 1
    assert isinstance(accompaniment, np.ndarray) and accompaniment.ndim == 1
    assert len(target) == len(accompaniment)
    assert sr > 0


@SLOW
def test_separate_48k_at_model_rate(clicks_48k):
    target, accompaniment, sr = separate(clicks_48k, target_source="drums")
    assert sr == 44100 and len(target) == 3 * 44100
    # The stems must add back up to the input, proves rate and timing are
    # right, independent of which stem Demucs puts the clicks in
    mix, _ = librosa.load(clicks_48k, sr=44100, mono=True)
    assert np.corrcoef(mix, target + accompaniment)[0, 1] > 0.9


@SLOW
def test_separate_m4a(clicks_m4a):
    target, accompaniment, sr = separate(clicks_m4a, target_source="drums")
    assert sr == 44100 and len(target) == len(accompaniment) > 0


@SLOW
def test_separate_loop_stable_and_reproducible(click_wav):
    # Two regressions in one: (1) torch used to be pinned to 1 thread over a
    # segfault fear in loops, re-verified stable multi-threaded; (2) stems
    # used to differ between runs because of Demucs's random-shift default
    # (shifts=1). With shifts=0 the same input must give the same stem,
    # bit for bit, that is what makes the syncopation score repeatable.
    import torch
    assert torch.get_num_threads() > 1        # the pin must stay gone
    a, _, _ = separate(click_wav, target_source="drums")
    b, _, _ = separate(click_wav, target_source="drums")
    assert a.shape == b.shape
    assert np.array_equal(a, b), \
        f"stems differ between identical runs (max |diff| {np.abs(a - b).max():.3g})"
