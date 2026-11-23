"""Guards for the bundled sample dataset (mireasy/sample_stimuli/). Offline and fast.

The samples are the documentation's "try it right now" path — if they rot, the first
thing a new user touches breaks. They ship as MP3 (issue #15: six times
smaller than WAV for people downloading the repository) and live inside the
package since 2026-11-19 so `mireasy --demo` works after `pip install mireasy`
(issue #21).
"""
import os
import glob

import numpy as np
import soundfile as sf

from mireasy.paths import SAMPLE_STIMULI_DIR

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = SAMPLE_STIMULI_DIR

EXPECTED = [
    "01_steady_drums_120bpm.mp3",
    "02_syncopated_drums_95bpm.mp3",
    "03_melody_a_minor_140bpm.mp3",
    "04_chords_c_major_80bpm.mp3",
    "05_quiet_ambient_no_drums.mp3",
]


def test_samples_live_inside_the_package_and_ship_in_the_wheel():
    assert SAMPLES == os.path.join(REPO, "mireasy", "sample_stimuli")
    assert not os.path.exists(os.path.join(REPO, "sample_stimuli")), \
        "the sample folder moved into the package; no second copy at the root"
    import tomllib
    with open(os.path.join(REPO, "pyproject.toml"), "rb") as f:
        data = tomllib.load(f)["tool"]["setuptools"]["package-data"]["mireasy"]
    assert "sample_stimuli/*.mp3" in data


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


def test_site_home_documents_the_samples():
    # The "try it right now" walkthrough moved from the README to the site's
    # home page (docs/index.md) on 2026-11-23.
    with open(os.path.join(REPO, "docs", "index.md"), encoding="utf-8") as f:
        home = f.read()
    assert "sample_stimuli" in home and "mireasy --demo" in home
    # the two deliberate teaching caveats must stay documented
    assert "octave error" in home
    assert "non-rhythmic" in home
