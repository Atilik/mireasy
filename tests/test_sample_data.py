"""Guards for the bundled sample dataset (sample_stimuli/). Offline and fast.

The samples are the README's "try it right now" path — if they rot, the first
thing a new user touches breaks. They ship as MP3 (issue #15: six times
smaller than WAV for people downloading the repository).
"""
import os
import glob

import numpy as np
import soundfile as sf

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(REPO, "sample_stimuli")

EXPECTED = [
    "01_steady_drums_120bpm.mp3",
    "02_syncopated_drums_95bpm.mp3",
    "03_melody_a_minor_140bpm.mp3",
    "04_chords_c_major_80bpm.mp3",
    "05_quiet_ambient_no_drums.mp3",
]


def test_sample_folder_is_complete():
    present = sorted(os.path.basename(p)
                     for p in glob.glob(os.path.join(SAMPLES, "*.mp3")))
    assert present == EXPECTED
    assert not glob.glob(os.path.join(SAMPLES, "*.wav")), "stray WAVs: samples are MP3 now"
    # regeneration script ships alongside (provenance for the synthetic audio)
    assert os.path.isfile(os.path.join(SAMPLES, "_generate.py"))


def test_sample_files_are_valid_audio():
    for name in EXPECTED:
        y, sr = sf.read(os.path.join(SAMPLES, name))
        assert sr == 44100, name
        assert y.ndim == 1, f"{name} should be mono"
        assert len(y) / sr >= 7.0, f"{name} too short for beat tracking"
        assert np.isfinite(y).all(), name


def test_samples_stay_small():
    # The whole point of MP3 here: the folder must stay well under 1 MB.
    total = sum(os.path.getsize(os.path.join(SAMPLES, n)) for n in EXPECTED)
    assert total < 1_000_000, f"sample_stimuli grew to {total/1e6:.2f} MB"


def test_ambient_sample_is_actually_quiet():
    y, _ = sf.read(os.path.join(SAMPLES, "05_quiet_ambient_no_drums.mp3"))
    assert np.abs(y).max() < 0.2, "the 'quiet' sample lost its low loudness"


def test_readme_documents_the_samples():
    with open(os.path.join(REPO, "README.md"), encoding="utf-8") as f:
        readme = f.read()
    assert "sample_stimuli" in readme
    # the two deliberate teaching caveats must stay documented
    assert "octave error" in readme
    assert "non-rhythmic" in readme
