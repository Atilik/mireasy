"""Sphinx configuration for the MIReasy documentation site.

Design: the site's pages live in this folder (index, installation, guide,
measures, references) and are the single home of the long documentation; the
repository README is a short pointer to them. Two documents stay at the
repository root because GitHub surfaces them there (CONTRIBUTING,
DEPENDENCY_LICENSES); those are copied in at build time, unchanged except for
link fixes. The API pages are generated from the code's docstrings.

The heavy runtime dependencies (torch, Essentia, ...) are mocked, so the site
builds in seconds on Read the Docs / CI without installing them.
"""
import os
import re
import shutil
import sys

DOCS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DOCS)
sys.path.insert(0, REPO)

from mireasy import __version__  # noqa: E402  (lightweight: no heavy imports)

# ── Project ──────────────────────────────────────────────────────────────────
project = "MIReasy"
author = "Mehmet Atilay Kucukoglu"
copyright = "2026, Mehmet Atilay Kucukoglu"
release = __version__
version = ".".join(__version__.split(".")[:2])

GITHUB = "https://github.com/Atilik/mireasy"

# ── Source files synced from the repository root ─────────────────────────────
# (published name, repository file). Everything else is written in docs/.
SYNCED = {
    "CONTRIBUTING.md": "CONTRIBUTING.md",
    "DEPENDENCY_LICENSES.md": "DEPENDENCY_LICENSES.md",
}

# Top-level pages of the site (the navigation itself is the toctree in index.md).
PAGES = ["index", "installation", "guide", "measures", "references",
         "CONTRIBUTING", "DEPENDENCY_LICENSES", "ai_usage"]

# A link whose label is plain text, or a badge: a link whose label is an image.
_LINK = re.compile(r"(?<!!)\[((?:[^\[\]]|!\[[^\]]*\]\([^)]*\))*)\]\(([^)\s]+)\)")


def _fix_links(text):
    """Keep links between the synced docs working; send everything else that
    points into the repository (folders, LICENSE.md, scripts, ...) to GitHub."""
    local = {name.lower() for name in SYNCED.values()}

    def repl(m):
        label, target = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|#)", target):
            return m.group(0)
        path, _, anchor = target.partition("#")
        anchor = f"#{anchor}" if anchor else ""
        if path.lower() == "readme.md":
            return f"[{label}](index.md{anchor})"
        if path.lower() in local:
            return m.group(0)
        kind = "tree" if path.endswith("/") else "blob"
        return f"[{label}]({GITHUB}/{kind}/main/{path}{anchor})"

    return _LINK.sub(repl, text)


def _sync_sources():
    for published, source in SYNCED.items():
        with open(os.path.join(REPO, source), encoding="utf-8") as f:
            text = _fix_links(f.read())
        with open(os.path.join(DOCS, published), "w", encoding="utf-8") as f:
            f.write(text)


_sync_sources()

# ── Sphinx ───────────────────────────────────────────────────────────────────
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3

# Runtime dependencies are not needed to document the API.
autodoc_mock_imports = [
    "numpy", "scipy", "torch", "torchaudio", "librosa", "soundfile",
    "sounddevice", "pyloudnorm", "mir_eval", "demucs", "essentia",
    "beat_this", "matplotlib", "IPython",
]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autoclass_content = "class"
napoleon_numpy_docstring = True
napoleon_google_docstring = True
napoleon_use_rtype = False

copybutton_prompt_text = r">>> |\$ "
copybutton_prompt_is_regexp = True

# ── Theme (same family as librosa's docs), light-purple palette ──────────────
html_theme = "pydata_sphinx_theme"
html_title = "MIReasy"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_show_sourcelink = False
html_context = {"default_mode": "light"}      # the palette is designed light-first
# The top-level pages have no sub-pages: drop their (empty) left sidebar so
# they read full-width with just the "On this page" outline at right.
html_sidebars = {name: [] for name in PAGES}
html_theme_options = {
    "logo": {"text": "MIReasy"},
    "icon_links": [
        {"name": "GitHub", "url": GITHUB, "icon": "fa-brands fa-github"},
    ],
    "navbar_align": "left",
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "show_nav_level": 2,
    "secondary_sidebar_items": ["page-toc"],
    "footer_start": ["copyright"],
    "footer_end": [],
    "show_prev_next": False,
}
