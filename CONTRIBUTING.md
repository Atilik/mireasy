# Getting help & contributing

Questions, bug reports, and ideas are all welcome — including (especially!)
from people who have never used GitHub before. This page explains how to reach
us for each situation.

## I have a question or something went wrong — what do I do?

The best way to reach us is to **open an issue** on GitHub. An "issue" is just
a public message to the developers — no programming involved:

1. Go to **<https://github.com/Atilik/mireasy/issues>**.
2. If you don't have a (free) GitHub account yet, click **Sign up** and create
   one — it takes two minutes.
3. Click the green **New issue** button.
4. Give it a short title ("Installer stops at step 3", "What does
   syncopation_score mean?") and describe what happened in the message box.
   Plain language is fine.
5. Click **Create**. We get notified and will answer in the same thread —
   you'll get an email when we do.

Because issues are public, other researchers with the same question will find
the answer too — that's why we prefer them over private email.

## Reporting a bug

Everything above, plus — these three things let us fix problems fast:

- **What you did and what you expected** (e.g. "dragged my folder into
  analyze_folder.command, expected a CSV, got the error below").
- **The log file.** mireasy writes one automatically next to the app:
  `install_log.txt` for installation problems, `analyze_log.txt` for analysis
  problems. **Drag the file into the issue's message box** — it attaches
  itself, and it contains the technical details (macOS version, chip, the full
  error) so you don't have to.
- **Your audio format** if the problem concerns a specific file (.wav, .mp3,
  .m4a, …) — but please don't upload copyrighted music itself.

## Requesting a feature

Open an issue and describe the **research use case** rather than the
implementation: "I need measure X per stimulus because my study does Y" helps
us more than "add function X". We maintain this tool for researchers outside
MIR, so knowing *why* shapes *what* we build.

## Contributing code (pull requests)

Developers are welcome — the workflow is standard:

1. **Fork** the repository and create a branch off `main`.
2. Build the environment: `conda env create -f environment.yml` (Apple Silicon
   macOS; see README for platform notes), then
   `conda activate mireasy && python download_models.py`.
3. Make your change. Please match the surrounding code style and keep the
   test suite's design rules:
   - `python run_tests.py` must pass — the default suite is **offline and
     fast** (synthetic audio, no model downloads), and new tests should be too.
   - Anything needing networks or heavy models goes behind the
     `MIREASY_RUN_SLOW=1` gate.
   - New user-facing attributes/metrics need a row in DOCUMENTATION.md — the
     doc-drift tests will remind you.
4. Open a **pull request** against `main` describing what and why. For larger
   changes, open an issue first so we can discuss the approach before you
   invest time.

## Code of conduct

Be kind and constructive; assume good faith. This project serves researchers
from many disciplines — no question is too basic.
