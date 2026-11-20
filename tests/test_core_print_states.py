"""core.py print helpers in every state (issue #22): a fully analysed stimulus,
array- and list-valued attributes, empty collections and collections longer
than the 20-line listing limit. Offline; nothing is computed by a model —
results are injected.
"""
import os
import shutil

import numpy as np

from mireasy.mireasy import Stimulus, Session, Participant


def test_stimulus_print_shows_every_computed_block(sine_wav, inject_rhythm, capsys):
    s = Stimulus(sine_wav)
    inject_rhythm(s)                                    # bpm, beats, meter
    s.toussaint_syncopation_score = 12.3
    s.toussaint_syncopation_score_meter = 4.5
    s.onset_times = np.array([0.5, 1.0, 1.5])
    s._genre_predictions = [("Rock---Classic Rock", 0.9), ("Pop", 0.05)]
    s._voice_instrumental = [("voice", 0.8), ("instrumental", 0.2)]
    s._mood = {"happy": 0.6, "sad": 0.1, "aggressive": 0.1, "relaxed": 0.2}
    s._pitch_freq = np.array([220.0, 221.0, 0.0])
    s._pitch_conf = np.array([0.9, 0.9, 0.1])
    s._compute_spectral_if_needed()
    s.print()
    out = capsys.readouterr().out
    for needle in ("BPM      : 120.0", "Meter    : 4/4", "Sync.    : 12.3", "Sync.(m) : 4.5",
                   "Onsets   : 3 detected", "Genre    : Rock---Classic Rock  (90.0%)",
                   "Vocal    : voice", "Mood     : happy (60%)", "Pitch    : 220.5 Hz",
                   "Centroid :", "Bwidth   :", "Rolloff  :", "Flatness :", "ZCR      :"):
        assert needle in out, needle


def test_stimulus_print_all_summarises_arrays_and_long_lists(sine_wav, inject_rhythm, capsys):
    s = Stimulus(sine_wav)
    inject_rhythm(s)
    s.onset_times = np.arange(5, dtype=float)           # public ndarray attribute
    s.tags = list(range(20))                            # public long list attribute
    s.print_all()
    out = capsys.readouterr().out
    assert "bpm                       : 120.0" in out
    assert "beat_times                : ndarray  shape=(18,)" in out
    assert "onset_times               : ndarray  shape=(5,)" in out
    assert "tags                      : list (len=20)" in out


def test_session_print_empty_and_long(session_folder, sine_wav, tmp_path, capsys):
    sess = Session(session_folder)
    sess.items = []
    sess.print()
    assert "(No songs loaded)" in capsys.readouterr().out

    big = tmp_path / "big"
    big.mkdir()
    for i in range(21):
        shutil.copy(sine_wav, big / f"{i + 1:02d}_song.wav")
    Session(str(big)).print()
    out = capsys.readouterr().out
    assert "[20] 20_song.wav" in out and "... and 1 more." in out and "21_song.wav" not in out


def test_participant_print_empty_and_long(participant_folder, sine_wav, tmp_path, capsys):
    p = Participant(participant_folder)
    p.sessions, p.n_sessions = [], 0
    p.print()
    assert "(No sessions loaded)" in capsys.readouterr().out

    big = tmp_path / "big"
    for i in range(21):
        d = big / f"s{i + 1:02d}"
        d.mkdir(parents=True)
        shutil.copy(sine_wav, d / "song.wav")
    Participant(str(big)).print()
    out = capsys.readouterr().out
    assert "[20] s20  (1 songs)" in out and "... and 1 more." in out and "s21" not in out.split("Sessions:")[1]
