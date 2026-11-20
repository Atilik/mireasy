"""Stimulus paths the main suite reached only indirectly (issue #22): lazy beat
detection through every beat property, lazy classification through every
classifier property, batch helpers that have to run the separation themselves,
the time-series export, and the thin GUI/plot wrappers.

All offline and fast: BEAT THIS!, Demucs and the Essentia models are stand-ins.
"""
import csv
import os

import numpy as np
import pytest

import mireasy.mireasy as rw
from mireasy.mireasy import Stimulus
from conftest import make_clicks, SR
from test_stimulus import fake_models, _fake_separation  # noqa: F401  (fixture re-export)


def _saved(out_dir):
    """(csv rows, npz file names) written to the Analysis folder in out_dir."""
    analysis = [d for d in os.listdir(out_dir) if d.startswith("Analysis_")][0]
    folder = os.path.join(out_dir, analysis)
    names = os.listdir(folder)
    rows = []
    for csv_name in [n for n in names if n.endswith(".csv")]:
        with open(os.path.join(folder, csv_name)) as f:
            rows = list(csv.DictReader(f))
    return rows, [n for n in names if n.endswith(".npz")]


# ── lazy beat detection ──────────────────────────────────────

@pytest.fixture
def fake_beat_this(monkeypatch):
    """Stand-in for BEAT THIS!: a steady 120 BPM grid in 4/4."""
    bt = np.arange(0.5, 9.5, 0.5)

    def fake_detect_beats(y, sr, hop_length=512):
        frames = (bt * sr / hop_length).astype(int)
        positions = np.array([(i % 4) + 1 for i in range(len(bt))])
        return bt, frames, positions, 4

    monkeypatch.setattr(rw, "detect_beats", fake_detect_beats)
    return bt


@pytest.mark.parametrize("first", ["beat_times", "beat_positions", "meter", "beat_frames", "bpm"])
def test_every_beat_property_triggers_detection(sine_wav, fake_beat_this, first):
    # Whichever beat attribute is touched first must run the detector and fill
    # all five results consistently.
    s = Stimulus(sine_wav)
    assert getattr(s, first) is not None
    assert s.bpm == 120.0 and s.meter == 4
    assert len(s.beat_times) == len(s.beat_frames) == len(s.beat_positions) == len(fake_beat_this)
    assert s.BPM == s.bpm


def test_onset_detection_mixes_stereo_drums_and_resamples(sine_wav):
    # Demucs stems are stereo and may come back at another rate than the song.
    s = Stimulus(sine_wav)
    mono = make_clicks(np.arange(0.5, 9.5, 0.5), 10.0, sr=48000)
    s.separated_drums = np.stack([mono, mono])
    s.separated_drums_sr = 48000
    onsets = s.onset_detection()
    assert onsets is not None and len(onsets) >= 15


# ── lazy classification through the properties ──────────────

@pytest.mark.parametrize("prop, expected", [
    ("genre_top5", [("Rock---Classic Rock", 0.9), ("Pop", 0.05)]),
    ("voice_instrumental", "voice"),
    ("mood", {"happy": 0.6, "sad": 0.1, "aggressive": 0.1, "relaxed": 0.2}),
    ("key", "A"),
    ("scale", "minor"),
])
def test_each_classifier_property_runs_classify_once(sine_wav, fake_models, prop, expected):
    s = Stimulus(sine_wav)
    assert getattr(s, prop) == expected
    assert fake_models.count("classify_all") == 1 and fake_models.count("key") == 1


def test_classify_reports_no_voiced_frames(sine_wav, fake_models, monkeypatch, capsys):
    monkeypatch.setattr(rw, "_detect_pitch_crepe",
                        lambda p: (np.array([0.0, 0.1]), np.array([220.0, 221.0]), np.array([0.1, 0.2])))
    Stimulus(sine_wav).classify()
    assert "(no voiced frames)" in capsys.readouterr().out


def test_std_properties(sine_wav, fake_models):
    s = Stimulus(sine_wav)
    assert s.pitch_conf_std == pytest.approx(0.0)       # fake confidences are [0.9, 0.9]
    s.onset_times = np.array([1.0])
    assert s.onset_ioi_std == 0.0                       # one onset -> no intervals
    for name in ("spectral_centroid_std", "spectral_bandwidth_std", "spectral_rolloff_std",
                 "spectral_flatness_std", "zcr_std"):
        assert getattr(s, name) >= 0.0, name


# ── saving and batch helpers ─────────────────────────────────

def test_save_timeseries_defaults_to_cwd(sine_wav, inject_rhythm, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = Stimulus(sine_wav)
    inject_rhythm(s)
    s.save_timeseries()
    _, npz = _saved(str(tmp_path))
    assert len(npz) == 1 and npz[0].endswith("_timeseries.npz")


def test_process_and_save_separates_itself_and_exports_timeseries(
        sine_wav, inject_rhythm, fake_models, monkeypatch, tmp_path):
    _fake_separation(monkeypatch)
    s = Stimulus(sine_wav)
    inject_rhythm(s)
    s.separated_drums = None                            # batch mode must separate without asking
    s.process_and_save(output_path=str(tmp_path), timeseries=True)
    rows, npz = _saved(str(tmp_path))
    assert rows[0]["genre"] == "Rock---Classic Rock" and rows[0]["syncopation_score"] != ""
    assert len(npz) == 1


def test_partial_process_separates_and_skips_missing_pitch_model(
        sine_wav, inject_rhythm, monkeypatch, tmp_path, capsys):
    _fake_separation(monkeypatch)

    def no_crepe(path):
        raise FileNotFoundError("model file crepe-medium-1.pb not installed")
    monkeypatch.setattr(rw, "_detect_pitch_crepe", no_crepe)

    s = Stimulus(sine_wav)
    inject_rhythm(s)
    s.separated_drums = None
    s.partial_process_save(output_path=str(tmp_path), syncopation=True, pitch=True, timeseries=True)
    out = capsys.readouterr().out
    assert "Skipped pitch" in out
    rows, npz = _saved(str(tmp_path))
    assert rows[0]["syncopation_score"] != "" and "pitch_median_hz" not in rows[0]
    assert len(npz) == 1


# ── GUI / plot wrappers delegate to play.py / plot.py ───────

def test_gui_and_plot_wrappers_delegate(sine_wav, inject_rhythm, monkeypatch):
    calls = []
    for name in ("_play_interactive", "_sonify_beats", "_sonify_beats_and_onsets",
                 "_plot_spectrogram", "_plot_beats", "_plot_waveform", "_plot_beats_and_onsets"):
        monkeypatch.setattr(rw, name, lambda *a, _n=name, **k: calls.append(_n))
    s = Stimulus(sine_wav)
    inject_rhythm(s)                                    # beats + drums, so no prompt anywhere
    s.play(x=(0, 1))
    s.plot(scale="log")
    s.plot_beats()
    s.plot_waveform()
    s.sonify_beats()
    s.onset_times = None
    s.plot_onsets()                                     # detects onsets first
    s.onset_times = None
    s.sonify_onsets()                                   # detects onsets first
    assert calls == ["_play_interactive", "_plot_spectrogram", "_plot_beats", "_plot_waveform",
                     "_sonify_beats", "_plot_beats_and_onsets", "_sonify_beats_and_onsets"]
    assert s.onset_times is not None


def test_sonify_onsets_returns_quietly_when_separation_declined(sine_wav, inject_rhythm, monkeypatch):
    called = []
    monkeypatch.setattr(rw, "_sonify_beats_and_onsets", lambda *a, **k: called.append(1))
    monkeypatch.setattr("builtins.input", lambda *a: "n")
    s = Stimulus(sine_wav)
    inject_rhythm(s)
    s.separated_drums = None                            # forces the Demucs question
    assert s.sonify_onsets() is None and called == []


def test_help_and_print_all_print_something_useful(sine_wav, capsys):
    s = Stimulus(sine_wav)
    s.help()
    s.print_all()
    out = capsys.readouterr().out
    assert "crest" in out.lower() and "All Attributes" in out
