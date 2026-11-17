# Installing MIReasy

Three steps, about 10 minutes. You will paste a few lines into the Terminal;
every line is given below.

## What you need

| | |
|---|---|
| **Mac** | Apple Silicon (M1 or newer), macOS 15 or newer. Check via ** → About This Mac**. Intel Macs are not supported. |
| **Linux** | Ubuntu 22.04 or newer (other distributions should work). |
| **Windows** | Not supported for now. |
| **Also** | ~3 GB of free disk space and an internet connection. |

## Step 1 — Install Python

MIReasy needs Python 3.11 or newer (3.12 recommended).

- **Mac:** download the installer from **<https://www.python.org/downloads/macos/>**
  ("macOS 64-bit universal2 installer" for Python 3.12), open it, and click
  through with the default choices. **At the end a Finder window opens:
  double-click `Install Certificates.command` in it.** Without this step
  Python cannot download the analysis models later.
- **Linux:**

  ```bash
  sudo apt update
  sudo apt install python3.12 python3.12-venv python3-tk ffmpeg libportaudio2
  ```

Then open a new Terminal and check: `python3 --version` should print `Python 3.12.x`.

## Step 2 — Download MIReasy

On the MIReasy GitHub page, click the green **Code** button → **Download ZIP**,
then double-click the ZIP. You get a folder called **`mireasy-main`** — that
folder is MIReasy. Put it wherever you like (Documents, for example) and keep
it there: the installation points at it.

If you use git: `git clone https://github.com/Atilik/mireasy.git` does the same.

## Step 3 — Install

1. Open the **Terminal** (Mac: ⌘-space, type "Terminal", Return).
2. Type `cd ` (with a space), **drag the `mireasy-main` folder into the Terminal
   window**, and press Return. The Terminal is now "inside" the folder.
3. Run these two lines, one at a time:

```bash
pip3 install -e ".[test]"
python3 download_models.py
```

The first line installs MIReasy and everything it needs (about 2 GB, a few
minutes of scrolling text). The second fetches the pretrained models (about
45 MB) that power the genre, mood, key and pitch measures.

**Linux note:** Ubuntu's system Python refuses to install packages directly
("externally-managed-environment"). Create a private environment first, then
run the two lines above inside it:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

(Repeat `source .venv/bin/activate` in every new Terminal before using MIReasy.)

## Check that it works

Still in the same Terminal window:

```bash
python3 run_tests.py
```

This should end with a line like `… passed` and no failures. Then try MIReasy
on the five test songs that come with it:

```bash
mireasy sample_stimuli/
```

You are in the MIReasy shell. Type `session.print()` to list the songs,
`stimulus.bpm` for the tempo of the first one, or
`session.process_and_save(".")` to write a CSV with every measure. Leave with
`exit()`. [README.md](README.md) explains everything you can do from here.

## Every day after that

Open a Terminal and run MIReasy on your audio — from any folder:

```bash
mireasy /path/to/your/audio/
```

You can drag your audio folder into the Terminal instead of typing its path.
Results land in an `Analysis_…` folder next to your current location.

## Updating, reinstalling, removing

- **Update:** download the new ZIP, replace the old `mireasy-main` folder, and
  run the two lines of Step 3 again.
- **Reinstall:** run the two lines of Step 3 again.
- **Remove:** `pip3 uninstall mireasy`, then delete the `mireasy-main` folder.
  (The libraries MIReasy installed — torch, librosa, … — stay in your Python;
  they are harmless.)

## If something goes wrong

- `python3: command not found` or an old version: Step 1 did not finish, or
  the Terminal was open before Python was installed — close and reopen it.
- `error: externally-managed-environment` (Mac with Homebrew's Python): use the
  python.org Python from Step 1, or follow the Linux note in Step 3.
- `CERTIFICATE_VERIFY_FAILED` while downloading models (Mac): run the
  `Install Certificates.command` from Step 1, then `python3 download_models.py` again.
- The model download stopped halfway: run `python3 download_models.py` again;
  it only fetches what is missing.
- `.m4a` files are not read: install ffmpeg (`brew install ffmpeg` on a Mac with
  Homebrew; Linux got it in Step 1). WAV, MP3, FLAC and OGG work without it.
- Anything else: copy the error text from the Terminal and open an issue at
  <https://github.com/Atilik/mireasy/issues> — [CONTRIBUTING.md](CONTRIBUTING.md)
  shows how, step by step.

## Using conda instead

If you already work with conda or Miniconda, the repository ships an
`environment.yml` with the exact tested versions (it also brings ffmpeg along):

```bash
conda env create -f environment.yml
conda activate mireasy
python download_models.py
python -m mireasy sample_stimuli/
```

Everything else in this guide applies unchanged.
