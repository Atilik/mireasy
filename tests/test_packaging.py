"""Guards for pyproject.toml — the `pip install` recipe — and its agreement
with environment.yml (the exact-pinned conda recipe). Offline and fast.
"""
import os
import re
import tomllib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pyproject():
    with open(os.path.join(REPO, "pyproject.toml"), "rb") as f:
        return tomllib.load(f)


def _name(spec):
    """'mir_eval>=0.7' -> 'mir-eval' (PEP 503 normalisation)."""
    m = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", spec)
    return m.group(1).lower().replace("_", "-")


def _env_yml_pip_names():
    names, in_pip = set(), False
    with open(os.path.join(REPO, "environment.yml"), encoding="utf-8") as f:
        for line in f:
            s = line.rstrip("\n")
            if s.strip() == "- pip:":
                in_pip = True
                continue
            if not in_pip:
                continue
            if s.startswith("  - "):          # back at conda-level entries
                break
            item = s.strip()
            if not item.startswith("- "):
                continue                      # comment or blank
            item = item[2:].strip()
            wheel = re.match(r"\./wheels/([A-Za-z0-9_]+)-", item)
            names.add(_name(wheel.group(1)) if wheel else _name(item))
    return names


def test_pyproject_names_the_package_and_entry_point():
    p = _pyproject()["project"]
    assert p["name"] == "mireasy"
    assert p["requires-python"] == ">=3.11"
    assert p["scripts"]["mireasy"] == "mireasy.mireasy:main"


def test_version_is_a_single_source_of_truth():
    import mireasy
    p = _pyproject()
    assert "version" in p["project"]["dynamic"]
    assert p["tool"]["setuptools"]["dynamic"]["version"] == {"attr": "mireasy.__version__"}
    assert re.fullmatch(r"\d+\.\d+\.\d+(\.dev\d+)?", mireasy.__version__), mireasy.__version__


def test_no_git_or_compiled_dependencies():
    deps = _pyproject()["project"]["dependencies"]
    assert not any("git+" in d for d in deps), "a git dependency crept into pyproject.toml"
    assert not any(_name(d) == "madmom" for d in deps)
    bt = [d for d in deps if _name(d) == "beat-this"]
    assert len(bt) == 1 and "https://github.com/CPJKU/beat_this/archive/refs/tags/v1.1.0.zip" in bt[0], \
        "beat_this must install from its tag archive (no git, no compiler)"


def test_essentia_has_a_python_314_rule():
    # Essentia's 3.14 wheels exist only from build dev1438; older Pythons keep
    # the pin we tested. Both markers must be present and complementary.
    ess = [d for d in _pyproject()["project"]["dependencies"] if _name(d) == "essentia-tensorflow"]
    markers = {d.split(";")[1].strip() for d in ess}
    assert markers == {"python_version < '3.14'", "python_version >= '3.14'"}, markers


def test_pyproject_and_environment_yml_list_the_same_packages():
    # Everything pip needs must be in the conda recipe, and anything the conda
    # recipe adds on top must be a declared optional extra (e.g. pytest).
    p = _pyproject()["project"]
    main = {_name(d) for d in p["dependencies"]}
    extras = {_name(d) for group in p["optional-dependencies"].values() for d in group}
    yml = _env_yml_pip_names()
    assert main <= yml, f"in pyproject but missing from environment.yml: {sorted(main - yml)}"
    assert yml - main <= extras, f"in environment.yml but not in pyproject: {sorted(yml - main - extras)}"
