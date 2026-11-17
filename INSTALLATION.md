# Installing MIReasy

Four steps, about 15 minutes, no programming knowledge needed. You will type a
few lines into the Terminal; every line you need is given below, ready to copy.

## What you need

| | |
|---|---|
| **Mac** | Apple Silicon (M1 or newer) with macOS 15 or newer. Check via ** → About This Mac**. Intel Macs are not supported. |
| **Linux** | Ubuntu 22.04 or newer (other distributions should work). |
| **Windows** | Not supported directly; use WSL2 and follow the Linux steps. |
| **Also** | ~6 GB of free disk space, an internet connection, and your computer password. |

## Step 1 — Install Miniconda

Miniconda is the scientific Python that MIReasy runs on.

- **Mac:** download **<https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg>**,
  open it, and click Continue / Agree / Install through all the screens.
- **Linux:** in a terminal, run the two lines below and answer "yes" to the questions.

  ```bash
  curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  bash Miniconda3-latest-Linux-x86_64.sh
  ```

Afterwards **close and reopen the Terminal**. Typing `conda --version` should
now print a version number.

## Step 2 — Download MIReasy

On the MIReasy GitHub page, click the green **Code** button → **Download ZIP**,
then double-click the ZIP. You get a folder called **`mireasy-main`** — that
folder is MIReasy. Put it wherever you like (Documents, for example).

If you use git: `git clone https://github.com/Atilik/mireasy.git` does the same.

## Step 3 — Create the environment

1. Open the **Terminal** (Mac: ⌘-space, type "Terminal", Return).
2. Type `cd ` (with a space), **drag the `mireasy-main` folder into the Terminal
   window**, and press Return. The Terminal is now "inside" the folder.
3. Run these three lines, one at a time, waiting for each to finish:

```bash
conda env create -f environment.yml
conda activate mireasy
python download_models.py
```

What to expect:

- The first line downloads and installs everything (about 5 GB). A long wall of
  scrolling text for 5–15 minutes is normal. Keep the laptop open and plugged in.
- If conda asks you to accept its Terms of Service
  ([anaconda.com/legal](https://anaconda.com/legal)), accept.
- The third line fetches the pretrained models (about 45 MB) that power the
  genre, mood, key and pitch measures. Without them MIReasy still runs, but
  those columns stay empty.

## Step 4 — Check that it works

Still in the same Terminal window:

```bash
python run_tests.py
```

This should end with a line like `… passed` and no failures. Then try MIReasy
on the five test songs that come with it:

```bash
python -m mireasy sample_stimuli/
```

You are in the MIReasy shell. Type `session.print()` to list the songs,
`stimulus.bpm` for the tempo of the first one, or
`session.process_and_save(".")` to write a CSV with every measure. Leave with
`exit()`. [README.md](README.md) explains everything you can do from here.

## Every day after that

Open a Terminal, go to the `mireasy-main` folder (the `cd ` + drag trick from
Step 3), then:

```bash
conda activate mireasy
python -m mireasy /path/to/your/audio/
```

You can also drag your audio folder into the Terminal instead of typing its
path. Results land in an `Analysis_…` folder next to your current location.

## Updating, reinstalling, removing

- **Update:** download the new ZIP and replace the old `mireasy-main` folder.
  The environment usually keeps working; if it does not, reinstall.
- **Reinstall:** `conda env create` refuses to overwrite an existing
  environment, so remove it first and repeat Step 3:

  ```bash
  conda env remove -n mireasy
  ```

- **Remove MIReasy completely:** run the line above, then delete the
  `mireasy-main` folder. Nothing else was installed on your computer.

## If something goes wrong

- `conda: command not found` right after Step 1: close and reopen the Terminal.
- The model download failed (no internet, or a server hiccup): run
  `python download_models.py` again later; it only fetches what is missing.
- Linux only, if audio playback complains: `sudo apt install libportaudio2`.
- Anything else: copy the error text from the Terminal and open an issue at
  <https://github.com/Atilik/mireasy/issues> — [CONTRIBUTING.md](CONTRIBUTING.md)
  shows how, step by step.

## For Python developers

MIReasy is a normal pip-installable package (Python 3.11–3.14, tested on Ubuntu
and macOS). In an environment of your choice, from the repository folder:

```bash
pip install -e ".[test]"
python download_models.py
python run_tests.py
```

On Linux install `ffmpeg` and `libportaudio2` with your package manager first;
the conda route in Step 3 brings them along automatically.
