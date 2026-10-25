# Installing MIReasy

Unfortunately MIReasy is Mac only.
There are 4 steps for installing MIReasy.
Total time: **10-20 minutes waiting**.

## Before you start - will it run on your Mac?

Click the **menu (top-left) → About This Mac** and check:

| You need | 
|---|
| An Apple Silicon chip (M1, M2, M3, M4 …) |
| macOS 15 (Sequoia) or newer | 
| ~6 GB free space, internet, and your Mac password | 

---

## Step 1: Install Miniconda (the scientific Python)

1. Download: **<https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg>**
2. Open the downloaded file and click **Continue / Agree / Install** through all the screens.

## Step 2: Download mireasy

1. On the MIReasy GitHub page, click the green **`<> Code`** button → **Download ZIP**.
2. In your **Downloads** folder, double-click the ZIP. A folder named
   **`mireasy-main`** appears - that folder is mireasy.
   *(Re-downloading later? Delete the old `mireasy-main` folder first.)*

## Step 3: Create the environment

Open **Terminal** (⌘-space, type "Terminal", Return). Type `cd ` (with a space),
**drag the `mireasy-main` folder into the Terminal window**, and press Return.
Then run these lines one at a time:

```bash
conda env create -f environment.yml
conda activate mireasy
python download_models.py     # optional: enables genre/mood/pitch features
```

- The first line installs everything. Please keep your laptop **open and plugged in**. A long wall of scrolling text for
  5–15 minutes is **expected**.
- If conda asks you to accept its Terms of Service
  ([anaconda.com/legal](https://anaconda.com/legal)), accept.

## Step 4: Check it works

```bash
python run_tests.py           # should finish with "… passed" and no failures
python -m mireasy /path/to/audio/
```

---

## Using MIReasy (every day)

In every new Terminal window: `conda activate mireasy`, then
`python -m mireasy /path/to/audio/`.
See README.md for the full feature documentation.

## If anything goes wrong

Open an issue at <https://github.com/Atilik/mireasy/issues> and paste the error
message from the Terminal. [CONTRIBUTING.md](CONTRIBUTING.md) explains how.
