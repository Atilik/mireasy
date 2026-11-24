"""Guards for the GitHub Actions workflow, the platform/Python support claim
lives there. Offline and fast (PyYAML is a demucs dependency, always present).
"""
import os
import tomllib

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "tests.yml")

PYTHONS = ["3.11", "3.12", "3.13", "3.14"]


def _workflow():
    with open(WORKFLOW, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _job(name):
    return _workflow()["jobs"][name]


def _steps(job):
    return _job(job)["steps"]


def _runs(job):
    return "\n".join(s.get("run", "") for s in _steps(job))


def test_workflow_parses_and_triggers_on_main_and_prs():
    wf = _workflow()
    on = wf.get("on", wf.get(True))        # PyYAML reads the bare key `on` as True
    assert "pull_request" in on and on["push"]["branches"] == ["main"]


def test_matrix_covers_the_supported_platforms_and_pythons():
    linux, mac = _job("test-linux"), _job("test-macos")
    assert linux["runs-on"] == "ubuntu-latest"
    assert mac["runs-on"] == "macos-latest"      # floating on purpose
    for job in (linux, mac):
        assert job["strategy"]["matrix"]["python"] == PYTHONS
        assert job["strategy"]["fail-fast"] is False


def test_pushes_to_main_are_never_cancelled_by_later_pushes():
    # With sequential macOS cells a main run takes ~15 min; a second push in
    # that window must queue behind it, not cancel it.
    c = _workflow()["concurrency"]
    assert c["cancel-in-progress"] == "${{ github.event_name == 'pull_request' }}"


def test_macos_jobs_are_requested_one_at_a_time():
    # GitHub's Apple-Silicon runner pool is capacity-constrained: four
    # simultaneous requests got three dropped unstarted on consecutive runs.
    # Sequential requests get served.
    assert _job("test-macos")["strategy"]["max-parallel"] == 1


def test_ci_installs_from_pyproject_and_runs_the_suite():
    for job in ("test-linux", "test-macos"):
        runs = _runs(job)
        assert 'pip install -e ".[test]"' in runs, job
        assert "pip check" in runs, job
        assert "download_models.py" in runs, job
        assert "run_tests.py" in runs, job
    assert "--cov=mireasy" in _runs("test-linux")


def test_ci_keeps_the_models_inside_its_cache_path():
    # The models moved to a per-user cache folder (issue #21); CI pins them back
    # into the checkout so the actions/cache steps (path: mireasy/models) still hit.
    wf = _workflow()
    assert wf["env"]["MIREASY_MODELS_DIR"] == "${{ github.workspace }}/mireasy/models"
    for job in ("test-linux", "test-macos", "slow"):
        cache = [s for s in _steps(job) if s.get("uses", "").startswith("actions/cache")]
        assert cache and "mireasy/models" in cache[0]["with"]["path"], job


def test_ci_is_headless_safe_and_cpu_only_on_linux():
    wf = _workflow()
    assert wf["env"]["MPLBACKEND"] == "Agg"
    assert "download.pytorch.org/whl/cpu" in _runs("test-linux")
    assert "download.pytorch.org/whl/cpu" not in _runs("test-macos")   # mac wheels are already CPU/MPS


def test_slow_tier_runs_the_real_models():
    steps = _steps("slow")
    run_step = [s for s in steps if "run_tests.py" in s.get("run", "")][0]
    assert run_step["env"]["MIREASY_RUN_SLOW"] == "1"
    warm = _runs("slow")
    assert "get_model('htdemucs')" in warm and "Audio2Beats" in warm


def test_both_tiers_upload_coverage():
    # The badge should reflect the real model code paths too, so the slow job
    # measures and uploads as well; Codecov merges the two flags per commit.
    for job, flag in (("test-linux", "fast"), ("slow", "slow")):
        run_step = [s for s in _steps(job) if "run_tests.py" in s.get("run", "")][0]
        assert "--cov=mireasy" in run_step["run"], f"{job} job does not measure coverage"
        uploads = [s for s in _steps(job) if "codecov" in s.get("uses", "")]
        assert len(uploads) == 1 and uploads[0]["with"]["flags"] == flag, \
            f"{job} job must upload coverage once, with flag {flag!r}"


def test_coverage_omits_only_the_gui_modules():
    # play.py / plot.py open Tk windows and cannot run headless; nothing else
    # may be excluded, or the percentage stops meaning what the README implies.
    with open(os.path.join(REPO, "pyproject.toml"), "rb") as f:
        cov = tomllib.load(f)["tool"]["coverage"]["run"]
    assert cov["source"] == ["mireasy"]
    assert sorted(cov["omit"]) == ["mireasy/play.py", "mireasy/plot.py"]
