# Installing MIReasy

Four steps, about 10 minutes. You will paste a few lines into the Terminal;
every line is given below. Nothing is installed outside the MIReasy folder
except Python itself, so removing MIReasy later means deleting one folder.

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

Then open a new Terminal and check: `python3.12 --version` should print `Python 3.12.x`.

## Step 2 — Download MIReasy

On the MIReasy GitHub page, click the green **Code** button → **Download ZIP**,
then double-click the ZIP. You get a folder called **`mireasy-main`** — that
folder is MIReasy. Put it wherever you like (Documents, for example), and keep
it there: the installation lives inside it.

If you use git: `git clone https://github.com/Atilik/mireasy.git` does the same.

## Step 3 — Install

1. Open the **Terminal** (Mac: ⌘-space, type "Terminal", Return).
2. Type `cd ` (with a space), **drag the `mireasy-main` folder into the Terminal
   window**, and press Return. The Terminal is now "inside" the folder.
3. Run these four lines, one at a time, waiting for each to finish:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
python download_models.py
```

What they do: the first two create a private Python environment inside the
folder and switch to it (the prompt now starts with `(.venv)`); the third
installs MIReasy and everything it needs (about 2 GB, a few minutes of
scrolling text); the fourth fetches the pretrained models (about 45 MB) that
power the genre, mood, key and pitch measures.

## Step 4 — Check that it works

Still in the same Terminal window:

```bash
python run_tests.py
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

Open a Terminal, go to the `mireasy-main` folder (the `cd ` + drag trick from
Step 3), then:

```bash
source .venv/bin/activate
mireasy /path/to/your/audio/
```

You can drag your audio folder into the Terminal instead of typing its path.
Results land in an `Analysis_…` folder next to your current location.

## Updating, reinstalling, removing

- **Update:** download the new ZIP, replace the old folder, and repeat Step 3.
- **Reinstall:** delete the `.venv` folder inside `mireasy-main` (it is
  hidden; in Terminal: `rm -rf .venv`) and repeat Step 3.
- **Remove MIReasy completely:** delete the `mireasy-main` folder. That's all —
  the environment and the models were inside it.

## If something goes wrong

- `python3.12: command not found`: Step 1 did not finish, or the Terminal was
  open before Python was installed — close and reopen it.
- `CERTIFICATE_VERIFY_FAILED` while downloading models (Mac): run the
  `Install Certificates.command` from Step 1, then `python download_models.py` again.
- The model download stopped halfway: run `python download_models.py` again;
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
