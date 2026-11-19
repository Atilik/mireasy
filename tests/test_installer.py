"""Guards for the install recipe and the repo's documentation contract.

The double-click `.command` launchers were removed on 2026-10-18 (maintainers
prefer the command-line workflow), so what remains here checks that
`environment.yml` still installs without a compiler or git, and that the docs
keep describing the real moving parts. All offline and fast.
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(name):
    with open(os.path.join(REPO, name), encoding="utf-8") as f:
        return f.read()


def test_env_yml_is_compile_free_and_git_free():
    # Regression: git-URL deps need git, which fresh Macs lack, and compiled
    # deps broke on user machines (madmom, since removed). Since 2026-11-19
    # BEAT THIS! comes from PyPI in BOTH recipes (issue #21: PyPI rejects
    # direct-URL dependencies); nothing may need git, a compiler, a URL, or a
    # wheel bundled in the repository.
    yml = _read("environment.yml")
    assert "git+" not in yml, "a git dependency crept back into environment.yml"
    assert "madmom" not in yml and "cython" not in yml, \
        "madmom (or its build dep cython) crept back into environment.yml"
    assert "beat-this==" in yml, "environment.yml must pin beat-this from PyPI"
    for name in ("environment.yml", "pyproject.toml"):
        assert "@ https://" not in _read(name), f"{name} has a direct-URL dependency again"
    assert "./wheels" not in yml and not os.path.isdir(os.path.join(REPO, "wheels")), \
        "the bundled-wheels folder was removed on 2026-11-17; nothing should reference it"


def test_installation_md_mentions_the_moving_parts():
    # pip + venv is the main route (2026-11-17, his decision); conda is the
    # alternative for people who already use it.
    s = _read("INSTALLATION.md")
    for needle in ("python.org", 'install -e ".[test]"',
                   "Install Certificates.command",      # python.org Mac gotcha
                   "externally-managed-environment",    # the case that needs a venv
                   "download_models.py", "run_tests.py", "mireasy sample_stimuli/",
                   "conda env create -f environment.yml", "conda activate mireasy",
                   "Apple Silicon", "macOS 15"):
        assert needle in s, f"INSTALLATION.md no longer mentions: {needle}"


def test_readme_links_installation_md():
    assert "INSTALLATION.md" in _read("README.md")


def test_contributing_md_covers_the_basics():
    s = _read("CONTRIBUTING.md")
    for needle in ("github.com/Atilik/mireasy/issues", "New issue",
                   "pull request", "MIREASY_RUN_SLOW"):
        assert needle in s, f"CONTRIBUTING.md no longer mentions: {needle}"
    assert "CONTRIBUTING.md" in _read("README.md"), \
        "README no longer points to CONTRIBUTING.md"


def test_dependency_licenses_md_covers_every_direct_dep():
    s = _read("DEPENDENCY_LICENSES.md")
    for dep in ("beat_this", "demucs", "essentia", "librosa",
                "mir_eval", "pyloudnorm", "numpy", "scipy", "torch",
                "matplotlib", "sounddevice"):
        assert dep in s, f"DEPENDENCY_LICENSES.md misses dependency: {dep}"
    for flag in ("AGPL-3.0", "CC BY-NC-SA"):
        assert flag in s, f"DEPENDENCY_LICENSES.md lost the {flag} flag"
