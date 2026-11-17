"""Guards for the documentation site (docs/, Read the Docs, the CI docs job).

The site is built from the repository's own Markdown files, synced by
docs/conf.py at build time; these tests keep the three config surfaces
(pyproject extra, docs/requirements.txt, .readthedocs.yaml) agreeing and make
sure the sync still covers every root document. Offline and fast.
"""
import os
import re
import tomllib

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, "docs")

ROOT_DOCS = ["README.md", "INSTALLATION.md", "DOCUMENTATION.md",
             "CONTRIBUTING.md", "DEPENDENCY_LICENSES.md"]


def _read(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as f:
        return f.read()


def _req_names(text):
    return {re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", line).group(1).lower()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith("#")}


def test_docs_extra_matches_requirements_file():
    with open(os.path.join(REPO, "pyproject.toml"), "rb") as f:
        extra = tomllib.load(f)["project"]["optional-dependencies"]["docs"]
    assert _req_names("\n".join(extra)) == _req_names(_read("docs", "requirements.txt")), \
        "pyproject [docs] extra and docs/requirements.txt list different packages"


def test_readthedocs_config_points_at_our_build():
    cfg = yaml.safe_load(_read(".readthedocs.yaml"))
    assert cfg["version"] == 2
    assert cfg["sphinx"]["configuration"] == "docs/conf.py"
    assert cfg["sphinx"]["fail_on_warning"] is True
    installs = cfg["python"]["install"]
    assert installs == [{"requirements": "docs/requirements.txt"}], \
        "Read the Docs must install only the docs toolchain (runtime deps are mocked)"


def test_conf_syncs_every_root_document_and_mocks_the_heavy_deps():
    conf = _read("docs", "conf.py")
    for name in ROOT_DOCS:
        assert f'"{name}"' in conf, f"docs/conf.py no longer syncs {name} into the site"
    for dep in ("torch", "essentia", "demucs", "beat_this", "librosa", "numpy"):
        assert f'"{dep}"' in conf, f"{dep} missing from autodoc_mock_imports"
    assert 'html_theme = "pydata_sphinx_theme"' in conf
    assert os.path.isfile(os.path.join(DOCS, "_static", "css", "custom.css"))


def test_api_pages_cover_the_public_objects():
    pages = {"index", "stimulus", "session", "participant", "functions", "modules"}
    present = {f[:-3] for f in os.listdir(os.path.join(DOCS, "api")) if f.endswith(".md")}
    assert pages <= present, f"missing API pages: {sorted(pages - present)}"
    body = "".join(_read("docs", "api", f"{p}.md") for p in pages)
    for obj in ("mireasy.mireasy.Stimulus", "mireasy.mireasy.Session",
                "mireasy.mireasy.Participant", "mireasy.mireasy.mireasy",
                "mireasy.rhythm", "mireasy.dsp", "mireasy.separate", "mireasy.genre"):
        assert obj in body, f"{obj} is not documented in the API pages"


def test_ci_builds_the_docs_with_warnings_as_errors():
    wf = yaml.safe_load(_read(".github", "workflows", "tests.yml"))
    runs = "\n".join(s.get("run", "") for s in wf["jobs"]["docs"]["steps"])
    assert "docs/requirements.txt" in runs
    assert re.search(r"sphinx\s+-W\s+--keep-going", runs), "docs job must fail on warnings"
