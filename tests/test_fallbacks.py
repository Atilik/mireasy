"""Fallback and error paths across the small modules (issue #22): the beat-grid
edge cases in rhythm.py, BEAT THIS! returning nothing, the legacy notebook
plot/sonify helpers, Demucs device selection, stereo input to the spectral
functions, missing model files, a failing model download, and the two package
entry points. Offline and fast; models and devices are stand-ins.
"""
import runpy
import sys

import numpy as np
import pytest

from conftest import make_clicks, make_sine, SR
from mireasy import dsp, rhythm


# ── rhythm: grid edge cases ─────────────────────────────────

def test_onset_at_the_very_end_of_a_bar_rounds_into_the_next_bar():
    # Bars at 0, 4, 8 s (positions 1-4). An onset at 3.99 s rounds to slot 16
    # of bar 0, i.e. slot 0 of bar 1; one at 7.99 s would land beyond the last
    # complete bar and is dropped.
    bt = np.arange(0.0, 9.0, 1.0)
    bp = np.array([(i % 4) + 1 for i in range(len(bt))])
    grid, num_bars = rhythm._pattern_from_beats_and_onsets(bt, [3.99, 7.99], beat_positions=bp)
    assert num_bars == 2
    assert grid[16] == 1 and grid[:16].sum() == 0 and grid[17:].sum() == 0


def test_fallback_grid_rounds_late_onsets_into_the_next_beat():
    # No beat positions: beats grouped in fours. 0.99 s -> beat 1 slot 0;
    # 3.99 s would roll past the last grid beat and is dropped.
    bt = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    grid, num_bars = rhythm._pattern_from_beats_and_onsets(bt, [0.99, 3.99])
    assert num_bars == 1
    assert grid[4] == 1 and grid.sum() == 1


def test_syncopation_score_mixes_stereo_drums():
    bt = np.arange(0.5, 9.5, 0.5)
    mono = make_clicks(bt, 10.0)
    score, onsets = rhythm.syncopation_score(bt, np.stack([mono, mono]), SR)
    assert 0.0 <= score <= 100.0 and len(onsets) >= 15


def test_meter_defaults_to_4_when_no_beat_falls_between_downbeats():
    positions, meter = rhythm._derive_positions_and_meter([10.0, 11.0], [0.0, 1.0])
    assert meter == 4 and list(positions) == [1, 2]


def test_unsupported_beats_per_bar_falls_back_to_4():
    # Five beats between two downbeats: the toolbox only scores 2/4, 3/4 and 4/4.
    bt = np.arange(0.0, 6.0, 1.0)
    positions, meter = rhythm._derive_positions_and_meter(bt, [0.0, 5.0])
    assert meter == 4 and list(positions[:5]) == [1, 2, 3, 4, 5]


def test_get_bpm_zero_interval_returns_zero():
    assert rhythm.get_bpm(np.array([1.0, 1.0, 1.0])) == 0


def test_detect_beats_with_a_silent_tracker_returns_empty_results(monkeypatch):
    monkeypatch.setattr(rhythm, "_get_beat_this_model", lambda: (lambda y, sr: ([], [])))
    beats, frames, positions, meter = rhythm.detect_beats(make_sine(duration=1.0), SR)
    assert len(beats) == len(frames) == len(positions) == 0 and meter == 4


def test_detect_beats_derives_frames_positions_and_meter(monkeypatch):
    bt = np.arange(0.5, 4.5, 0.5)
    monkeypatch.setattr(rhythm, "_get_beat_this_model", lambda: (lambda y, sr: (bt, bt[::4])))
    beats, frames, positions, meter = rhythm.detect_beats(make_sine(duration=5.0), SR)
    assert np.array_equal(beats, bt) and len(frames) == len(bt)
    assert meter == 4 and list(positions[:4]) == [1, 2, 3, 4]


def test_legacy_notebook_helpers_plot_and_sonify(monkeypatch):
    import matplotlib
    matplotlib.use("Agg")
    shown, played = [], []
    monkeypatch.setattr(rhythm.plt, "show", lambda: shown.append(1))
    monkeypatch.setattr(rhythm, "display", lambda widget: played.append(widget))
    y = make_clicks([0.5, 1.0, 1.5], 2.0)
    rhythm.plot_detected_beats(y, SR, np.array([0.5, 1.0, 1.5]))
    rhythm.plt.close("all")
    rhythm.sonify_beats(y, SR, np.array([0.5, 1.0, 1.5]))
    assert shown == [1] and len(played) == 1


# ── separate: device selection ──────────────────────────────

@pytest.fixture
def fake_demucs(monkeypatch):
    import torch
    import mireasy.separate as sep

    class FakeModel:
        samplerate, audio_channels = 44100, 2
        sources = ["drums", "bass", "other", "vocals"]
        devices = []
        def eval(self): return self
        def to(self, device):
            self.devices.append(str(device))
            return self

    monkeypatch.setattr(sep, "_MODEL", FakeModel())
    monkeypatch.setattr(sep, "apply_model",
                        lambda model, mix, **kw: torch.zeros(1, len(model.sources), *mix.shape[1:]))
    return sep, FakeModel


def test_gpu_true_without_cuda_falls_back_to_cpu(sine_wav, fake_demucs, monkeypatch, capsys):
    sep, FakeModel = fake_demucs
    monkeypatch.setattr(sep.torch.cuda, "is_available", lambda: False)
    sep.separate(sine_wav, target_source="drums", gpu=True)
    assert "falling back to CPU" in capsys.readouterr().out and FakeModel.devices[-1] == "cpu"


def test_gpu_true_with_cuda_moves_the_model_to_cuda(sine_wav, fake_demucs, monkeypatch):
    # No GPU on the test machine: torch.device("cuda") is only a label here, and
    # the stand-in model records where it was asked to go.
    sep, FakeModel = fake_demucs
    monkeypatch.setattr(sep.torch.cuda, "is_available", lambda: True)
    sep.separate(sine_wav, target_source="drums", gpu=True)
    assert FakeModel.devices[-1] == "cuda"


def test_gpu_given_as_device_name_is_used_verbatim(sine_wav, fake_demucs):
    sep, FakeModel = fake_demucs
    sep.separate(sine_wav, target_source="drums", gpu="cpu")
    assert FakeModel.devices[-1] == "cpu"


# ── dsp: stereo input and the unimplemented filter ─────────

def test_filter_dispatches_bell_to_the_not_implemented_stub():
    with pytest.raises(NotImplementedError):
        dsp.filter(np.zeros(1000), "bell", 1000)


def test_spectral_functions_accept_stereo_input():
    y = np.stack([make_sine(440, 1.0), make_sine(220, 1.0)])
    assert dsp.spectral_irregularity(y, SR) >= 0.0
    feats = dsp.compute_spectral_features(y, SR)
    assert feats["zcr"].ndim == 1 and len(feats["spectral_centroid"]) == len(feats["zcr"])


# ── genre: missing model files, odd head labels ─────────────

def test_model_loaders_name_the_download_command_when_files_are_missing(tmp_path, monkeypatch, sine_wav):
    from mireasy import genre
    monkeypatch.setenv("MIREASY_MODELS_DIR", str(tmp_path))       # empty folder
    monkeypatch.setattr(genre, "_embedding_model", None)
    monkeypatch.setattr(genre, "_head_models", {})
    monkeypatch.setattr(genre, "_head_classes", {})
    monkeypatch.setattr(genre, "_crepe_model", None)
    for attempt in (genre._get_embedding_model,
                    lambda: genre._get_head_model("genre"),
                    lambda: genre.detect_pitch_crepe(sine_wav)):
        with pytest.raises(FileNotFoundError, match="mireasy-download-models"):
            attempt()


def test_mood_falls_back_when_a_head_does_not_name_its_mood(monkeypatch):
    from mireasy import genre
    monkeypatch.setattr(genre, "_classify",
                        lambda name, path, top_n=5, embeddings=None: [("other", 0.7), ("x", 0.3)])
    moods = genre._classify_mood_from_embeddings("song.wav", embeddings=None)
    assert set(moods) == {"happy", "sad", "aggressive", "relaxed"}
    assert all(v == pytest.approx(0.3) for v in moods.values())


# ── download_models: offline paths ──────────────────────────

def test_download_streams_to_a_part_file_then_renames(tmp_path, monkeypatch):
    from mireasy import download_models as dm

    class FakeResponse:
        headers = {"Content-Length": "6"}
        chunks = [b"abc", b"def", b""]
        def read(self, n): return self.chunks.pop(0)
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(dm.urllib.request, "urlopen", lambda url, timeout=60: FakeResponse())
    dest = tmp_path / "model.pb"
    dm.download("https://example.invalid/model.pb", str(dest))
    assert dest.read_bytes() == b"abcdef" and not (tmp_path / "model.pb.part").exists()


def test_failed_download_is_reported_and_exits_1(tmp_path, monkeypatch, capsys):
    from mireasy import download_models as dm
    monkeypatch.setenv("MIREASY_MODELS_DIR", str(tmp_path))

    def boom(url, dest):
        raise OSError("no network")
    monkeypatch.setattr(dm, "download", boom)
    assert dm.main() == 1
    out = capsys.readouterr().out
    assert "FAILED: no network" in out and "✗" in out and str(tmp_path) in out


def test_present_files_are_skipped_without_network(tmp_path, monkeypatch, capsys):
    from mireasy import download_models as dm
    monkeypatch.setenv("MIREASY_MODELS_DIR", str(tmp_path))
    monkeypatch.setattr(dm, "download", lambda url, dest: pytest.fail("must not download"))
    for _, name in dm.FILES:
        (tmp_path / name).write_bytes(b"x")
    assert dm.main() == 0
    out = capsys.readouterr().out
    assert out.count("[skip]") == len(dm.FILES) and "✓ All" in out


# ── package entry points ────────────────────────────────────

def test_package_dir_lists_the_lazy_exports():
    import mireasy
    assert {"Stimulus", "Session", "Participant"} <= set(dir(mireasy))


def test_python_m_mireasy_without_arguments_prints_usage(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["mireasy"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("mireasy", run_name="__main__", alter_sys=True)
    assert exc.value.code == 1 and "Usage: mireasy" in capsys.readouterr().out
