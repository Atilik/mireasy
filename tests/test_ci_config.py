"""Guards for the GitHub Actions workflow — the platform/Python support claim
lives there. Offline and fast (PyYAML is a demucs dependency, always present).
"""
import os

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "tests.yml")


def _workflow():
    with open(WORKFLOW, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _steps(job):
    return _workflow()["jobs"][job]["steps"]


def _runs(job):
    return "\n".join(s.get("run", "") for s in _steps(job))


def test_workflow_parses_and_triggers_on_main_and_prs():
    wf = _workflow()
    on = wf.get("on", wf.get(True))        # PyYAML reads the bare key `on` as True
    assert "pull_request" in on and on["push"]["branches"] == ["main"]


def test_matrix_covers_the_supported_platforms_and_pythons():
    m = _workflow()["jobs"]["test"]["strategy"]["matrix"]
    assert m["os"] == ["ubuntu-latest", "macos-latest"]
    assert m["python"] == ["3.11", "3.12", "3.13", "3.14"]
    assert _workflow()["jobs"]["test"]["strategy"]["fail-fast"] is False


def test_ci_installs_from_pyproject_and_runs_the_suite():
    runs = _runs("test")
    assert 'pip install -e ".[test]"' in runs
    assert "pip check" in runs
    assert "download_models.py" in runs
    assert "run_tests.py" in runs and "--cov=mireasy" in runs


def test_ci_is_headless_safe_and_cpu_only_on_linux():
    wf = _workflow()
    assert wf["env"]["MPLBACKEND"] == "Agg"
    assert "download.pytorch.org/whl/cpu" in _runs("test")


def test_slow_tier_runs_the_real_models():
    steps = _steps("slow")
    run_step = [s for s in steps if "run_tests.py" in s.get("run", "")][0]
    assert run_step["env"]["MIREASY_RUN_SLOW"] == "1"
    warm = _runs("slow")
    assert "get_model('htdemucs')" in warm and "Audio2Beats" in warm
