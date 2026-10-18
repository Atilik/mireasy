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
    # Regression: madmom compiled on user machines (failed on a fresh macOS 26:
    # SDK/linker mismatch), and git-URL deps need git, which fresh Macs lack.
    # Both now ship as bundled wheels.
    yml = _read("environment.yml")
    assert "git+" not in yml, "a git dependency crept back into environment.yml"
    for wheel in ("wheels/madmom-0.17.dev0-cp311-cp311-macosx_11_0_arm64.whl",
                  "wheels/beat_this-1.1.0-py3-none-any.whl"):
        assert f"./{wheel}" in yml, f"environment.yml no longer installs {wheel}"
        assert os.path.isfile(os.path.join(REPO, wheel)), f"{wheel} missing from repo"


def test_installation_md_mentions_the_moving_parts():
    s = _read("INSTALLATION.md")
    for needle in ("Miniconda", "environment.yml", "conda env create",
                   "conda activate mireasy", "download_models.py",
                   "run_tests.py", "python -m mireasy",
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
    for dep in ("beat_this", "madmom", "demucs", "essentia", "librosa",
                "mir_eval", "pyloudnorm", "numpy", "scipy", "torch",
                "matplotlib", "sounddevice"):
        assert dep in s, f"DEPENDENCY_LICENSES.md misses dependency: {dep}"
    for flag in ("AGPL-3.0", "CC BY-NC-SA"):
        assert flag in s, f"DEPENDENCY_LICENSES.md lost the {flag} flag"
