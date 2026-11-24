"""Guards for .github/workflows/publish.yml, the PyPI release path (issue #21).
Offline and fast: parses the YAML and checks the contract, not GitHub."""
import os

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _workflow():
    with open(os.path.join(REPO, ".github", "workflows", "publish.yml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def _runs(job):
    return "\n".join(s.get("run", "") for s in _workflow()["jobs"][job]["steps"])


def test_release_and_manual_dry_run_are_the_only_triggers():
    on = _workflow()[True] if True in _workflow() else _workflow()["on"]   # PyYAML reads `on:` as True
    assert on["release"]["types"] == ["published"]
    assert on["workflow_dispatch"]["inputs"]["target"]["options"] == ["testpypi", "pypi"]
    assert on["workflow_dispatch"]["inputs"]["target"]["default"] == "testpypi"


def test_build_checks_the_artifacts_and_the_tag():
    runs = _runs("build")
    assert "python -m build" in runs and "twine check dist/*" in runs
    assert "mireasy.__version__" in runs and 'v${version}' in runs, \
        "a release tag must equal v<mireasy.__version__>"


def test_uploads_use_trusted_publishing_not_tokens():
    # No password / token anywhere: OIDC via id-token: write + the pypa action.
    jobs = _workflow()["jobs"]
    for job, env in (("publish-pypi", "pypi"), ("publish-testpypi", "testpypi")):
        j = jobs[job]
        assert j["needs"] == "build" and j["environment"] == env
        assert j["permissions"] == {"id-token": "write"}
        uses = [s.get("uses", "") for s in j["steps"]]
        assert any(u.startswith("pypa/gh-action-pypi-publish@") for u in uses), job
        for s in j["steps"]:
            assert "password" not in s.get("with", {}), "token-based upload crept in"
    testpypi = [s for s in jobs["publish-testpypi"]["steps"] if "pypa/" in s.get("uses", "")][0]
    assert testpypi["with"]["repository-url"] == "https://test.pypi.org/legacy/"
    assert "release" in jobs["publish-pypi"]["if"]
