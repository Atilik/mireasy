# Installing MIReasy

MIReasy works with Linux and Mac (Apple Silicon, macOS 15 or newer), and you need 3 GB of free disk space. Windows is not supported for now.

## Step 1: Install Python

MIReasy needs Python 3.11 to 3.14 (3.12 recommended). Python 3.15 does not work yet.

- **Mac:** download the **[Python 3.12 installer](https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg)** from python.org, open it, and click through with the default choices.
- **Terminal/Linux:**

  ```bash
  sudo apt update
  sudo apt install python3.12 python3.12-venv python3-tk ffmpeg libportaudio2
  ```

## Step 2: Install MIReasy

Open the **Terminal** and run these two lines, one at a time:

```bash
pip3 install https://github.com/Atilik/mireasy/archive/refs/heads/main.zip
mireasy-download-models
```

The first line installs MIReasy and everything it needs (about 2 GB, a few minutes). The second downloads the models for the genre, mood and pitch measures (about 45 MB).

**Linux note:** Ubuntu's system Python refuses to install packages directly ("externally-managed-environment"). Create a private environment first, then run the two lines above inside it:

```bash
python3.12 -m venv ~/mireasy-env
source ~/mireasy-env/bin/activate
```

Repeat the `source` line in every new Terminal before using MIReasy.

## Step 3: Try it

```bash
mireasy --demo
```

This opens the five test songs that come with MIReasy. Type `session.print()` to list the songs, `stimulus.bpm` for the tempo of the first one, or `session.process_and_save(".")` to write a CSV with every measure. Leave with `exit()`.

For your own audio:

```bash
mireasy /path/to/your/audio/
```

You can drag your audio folder into the Terminal instead of typing its path. The first analysis takes longer, because the beat tracker and Demucs download their own models once (about 160 MB). [Using MIReasy](guide.md) explains everything you can do from here.

## Updating and removing

- **Update:** `pip3 install --force-reinstall --no-deps https://github.com/Atilik/mireasy/archive/refs/heads/main.zip`
- **Remove:** `pip3 uninstall mireasy`

## If something goes wrong

- `python3: command not found`: close the Terminal and open it again.
- `error: externally-managed-environment`: on a Mac, use the python.org Python from Step 1. On Linux, follow the Linux note in Step 2.
- `requires a different Python`: your Python is too new or too old. Install Python 3.12 from Step 1, open a new Terminal, and try again.
- `.m4a` files are not read: install ffmpeg (`brew install ffmpeg` on a Mac). WAV, MP3, FLAC and OGG work without it.
- Anything else: copy the error text and open an issue at <https://github.com/Atilik/mireasy/issues>. [CONTRIBUTING.md](CONTRIBUTING.md) shows how.

## For developers

```bash
git clone https://github.com/Atilik/mireasy.git
cd mireasy
pip install -e ".[test]"
mireasy-download-models
python run_tests.py
```

With conda, `conda env create -f environment.yml` installs the exact tested versions of the dependencies. Then run `conda activate mireasy` and `pip install -e .` in the folder.
