"""Session / Participant batch paths and shell helpers (issue #22): the Demucs
question for a whole folder (accepted, declined), per-item failures that must
not stop the batch, single-session processing, time-series export with the
session prefix, and the selection edge cases of the shell. All offline: beats
are injected, Demucs and the Essentia models are stand-ins.
"""
import os

import pytest

import mireasy.mireasy as rw
from mireasy.mireasy import Session, Participant
from test_stimulus import fake_models, _fake_separation  # noqa: F401  (fixture re-export)


def _items(obj):
    return obj.items if isinstance(obj, Session) else [s for sess in obj.sessions for s in sess.items]


def _inject_all(obj, inject_rhythm, drums=True):
    for s in _items(obj):
        inject_rhythm(s)
        if not drums:
            s.separated_drums = None
    return _items(obj)


def _analysis_files(out_dir):
    analysis = [d for d in os.listdir(out_dir) if d.startswith("Analysis_")][0]
    return sorted(os.listdir(os.path.join(out_dir, analysis)))


# ── Session: the Demucs question and failing items ──────────

def test_session_declined_separation_skips_syncopation(session_folder, inject_rhythm, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda *a: "n")
    sess = Session(session_folder)
    items = _inject_all(sess, inject_rhythm, drums=False)
    sess._process_all_items()
    assert "Skipping drum separation" in capsys.readouterr().out
    assert all(s.toussaint_syncopation_score is None and s.bpm == 120.0 for s in items)


def test_session_accepted_separation_scores_every_item(session_folder, inject_rhythm, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda *a: "y")
    _fake_separation(monkeypatch)
    sess = Session(session_folder)
    items = _inject_all(sess, inject_rhythm, drums=False)
    sess._process_all_items()
    assert all(s.toussaint_syncopation_score is not None and
               s.toussaint_syncopation_score_meter is not None for s in items)


def test_session_keeps_going_when_one_item_fails(session_folder, inject_rhythm, monkeypatch, capsys):
    sess = Session(session_folder)
    items = _inject_all(sess, inject_rhythm)

    def boom(*a, **k):
        raise RuntimeError("corrupt drums")
    monkeypatch.setattr(items[0], "syncopation_score", boom)
    sess._process_all_items()
    assert "[Skipped syncopation] 01_alpha.wav" in capsys.readouterr().out
    assert items[1].toussaint_syncopation_score is not None


# ── Session: processing and saving ──────────────────────────

def test_session_process_single_item_separates_and_exports_timeseries(
        session_folder, inject_rhythm, fake_models, monkeypatch, tmp_path):
    _fake_separation(monkeypatch)
    sess = Session(session_folder)
    _inject_all(sess, inject_rhythm, drums=False)
    sess.process_and_save(output_path=str(tmp_path), index=2, timeseries=True)
    files = _analysis_files(str(tmp_path))
    assert any(f.endswith(".csv") for f in files)
    assert [f for f in files if f.endswith(".npz")] == ["02_beta_timeseries.npz"]


def test_session_process_all_exports_a_timeseries_per_item(
        session_folder, inject_rhythm, fake_models, tmp_path):
    sess = Session(session_folder)
    _inject_all(sess, inject_rhythm)                    # drums present -> no question asked
    sess.process_and_save(output_path=str(tmp_path), timeseries=True)
    npz = [f for f in _analysis_files(str(tmp_path)) if f.endswith(".npz")]
    assert npz == ["01_alpha_timeseries.npz", "02_beta_timeseries.npz"]


def test_session_process_all_announces_the_batch_once(
        session_folder, inject_rhythm, fake_models, tmp_path, capsys):
    sess = Session(session_folder)
    _inject_all(sess, inject_rhythm)
    sess.process_and_save(output_path=str(tmp_path))
    assert capsys.readouterr().out.count("Processing 2 items...") == 1


def test_session_partial_process_exports_timeseries(session_folder, inject_rhythm, tmp_path):
    sess = Session(session_folder)
    _inject_all(sess, inject_rhythm)
    sess.partial_process_save(output_path=str(tmp_path), rhythm=True, timeseries=True)
    assert len([f for f in _analysis_files(str(tmp_path)) if f.endswith(".npz")]) == 2


# ── Session: shell helpers ──────────────────────────────────

def test_session_call_without_index_lists_and_returns_itself(session_folder, capsys):
    sess = Session(session_folder)
    assert sess() is sess
    assert "Session Summary" in capsys.readouterr().out


def test_session_call_by_name_focuses_the_match(session_folder, capsys):
    sess = Session(session_folder)
    sess._shell_ns = {}
    sess("beta")
    assert sess._shell_ns["stimulus"].audio_file_name == "02_beta.wav"


def test_session_help_and_boxplot_delegate(session_folder, monkeypatch, capsys):
    plotted = []
    monkeypatch.setattr(rw, "_plot_session_boxplots", lambda s: plotted.append(s))
    sess = Session(session_folder)
    sess.help()
    sess.boxplot()
    assert "Session Help" in capsys.readouterr().out and plotted == [sess]


# ── Participant ─────────────────────────────────────────────

def test_participant_skips_a_session_folder_that_fails_to_load(participant_folder, monkeypatch, capsys):
    real = rw.Session

    class Flaky(real):
        def __init__(self, folder_path, sr=44100):
            if folder_path.endswith("sess_b"):
                raise RuntimeError("corrupt folder")
            super().__init__(folder_path, sr=sr)

    monkeypatch.setattr(rw, "Session", Flaky)
    p = Participant(participant_folder)
    assert p.n_sessions == 1
    assert "[Skipped] sess_b: corrupt folder" in capsys.readouterr().out


def test_participant_process_one_session_with_timeseries(
        participant_folder, inject_rhythm, fake_models, tmp_path):
    p = Participant(participant_folder)
    _inject_all(p, inject_rhythm)
    path = p.process_and_save(output_path=str(tmp_path), index=1, timeseries=True)
    assert path.endswith(".csv")
    npz = [f for f in _analysis_files(str(tmp_path)) if f.endswith(".npz")]
    assert npz == ["sess_a_sess_a_song_timeseries.npz"]      # session prefix keeps songs apart


def test_participant_process_accepts_the_legacy_argument_order(
        participant_folder, inject_rhythm, fake_models, tmp_path):
    p = Participant(participant_folder)
    _inject_all(p, inject_rhythm)
    path = p.process_and_save(2, str(tmp_path))                # old signature: (index, output_path)
    assert path.startswith(str(tmp_path)) and path.endswith(".csv")


def test_participant_declined_separation_skips_syncopation(participant_folder, inject_rhythm, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("builtins.input", lambda *a: "n")
    p = Participant(participant_folder)
    items = _inject_all(p, inject_rhythm, drums=False)
    p.process_and_save(output_path=str(tmp_path))
    assert "Skipping drum separation" in capsys.readouterr().out
    assert all(s.toussaint_syncopation_score is None for s in items)


def test_participant_process_all_exports_prefixed_timeseries(
        participant_folder, inject_rhythm, fake_models, tmp_path):
    p = Participant(participant_folder)
    _inject_all(p, inject_rhythm)
    p.process_and_save(output_path=str(tmp_path), timeseries=True)
    npz = [f for f in _analysis_files(str(tmp_path)) if f.endswith(".npz")]
    assert npz == ["sess_a_sess_a_song_timeseries.npz", "sess_b_sess_b_song_timeseries.npz"]


def test_participant_partial_without_groups_prints_the_hint(participant_folder, tmp_path, capsys):
    p = Participant(participant_folder)
    p.partial_process_save(output_path=str(tmp_path))
    assert "No feature group selected" in capsys.readouterr().out


def test_participant_selection_edge_cases(participant_folder, capsys):
    p = Participant(participant_folder)
    with pytest.raises(TypeError):
        p[1.5]
    assert p[7] is p.sessions[0]                        # out of range -> first, with a warning
    assert "out of range" in capsys.readouterr().out
    with pytest.raises(ValueError, match="Ambiguous"):
        p["sess"]                                       # matches both sess_a and sess_b


def test_participant_call_help_and_print(participant_folder, capsys):
    p = Participant(participant_folder)
    assert p() is p
    p.help()
    p.print()
    out = capsys.readouterr().out
    assert "Participant Summary" in out and "Participant Help" in out
