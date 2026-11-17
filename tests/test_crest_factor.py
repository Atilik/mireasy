"""Tests for the crest factor (peak-to-RMS, dB) measure — issue #7."""
import numpy as np
import pytest

from mireasy.dsp import get_crest_factor_db
from conftest import make_sine, SR


def test_sine_is_3_dB():
    # peak/RMS of a sine is sqrt(2) -> 20*log10(sqrt(2)) = 3.0103 dB
    assert get_crest_factor_db(make_sine(duration=1.0)) == pytest.approx(3.0103, abs=0.02)


def test_square_wave_is_0_dB():
    y = np.sign(make_sine(duration=1.0))
    y[y == 0] = 1.0
    assert get_crest_factor_db(y) == pytest.approx(0.0, abs=1e-6)


def test_sparse_transients_score_high():
    y = np.zeros(SR)
    y[::SR // 4] = 1.0                     # four clicks per second, silence between
    assert get_crest_factor_db(y) > 20     # far above any sustained signal


def test_amplitude_invariant():
    quiet, loud = make_sine(amp=0.05), make_sine(amp=0.9)
    assert get_crest_factor_db(quiet) == pytest.approx(get_crest_factor_db(loud), abs=1e-9)


def test_silence_is_nan_and_stereo_is_mixed_to_mono():
    assert np.isnan(get_crest_factor_db(np.zeros(1000)))
    assert np.isnan(get_crest_factor_db(np.zeros(0)))
    stereo = np.stack([make_sine(440), make_sine(220)])        # (2, n) — mireasy layout
    assert np.isfinite(get_crest_factor_db(stereo))
