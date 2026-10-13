# Installing MIReasy

Unfortunatelly MIReasy is Mac only.
There are 4 steps for installing MIReasy.
Total time: **10–20 minutes waiting**.

## Before you start — will it run on your Mac?

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
   **`mireasy-main`** appears — that folder is mireasy.
   *(Re-downloading later? Delete the old `mireasy-main` folder first.)*

## Step 3: Run the installer

Open the `mireasy-main` folder and **double-click `install.command`**.

> **macOS will block it the first time, this is expected.** macOS shows:
> *"Apple could not verify 'install.command' is free of malware…"*
>
> 1. Click **Done**. ⚠️ **Not "Move to Trash"**, that deletes the installer
>    (if that happens, just re-do Step 2).
> 2. Open ** → System Settings → Privacy & Security**, scroll down to
>    *"'install.command' was blocked…"* and click **Open Anyway**, then
>    confirm with your password or Touch ID.
>    *(This entry only appears right after the blocked attempt in point 1.)*
> 3. A Terminal window opens. If macOS asks whether Terminal may access your
>    **Downloads** folder, click **Allow**.

You only do this unblock **once per `.command` file**.

## Step 4: Wait for the checkmark

The installer window prints what it is doing. While it runs:

- Please keep your laptop **open and plugged in**. A long wall of scrolling text for
  5–15 minutes is **expected**.
- The installer accepts conda's standard Terms of Service
  ([anaconda.com/legal](https://anaconda.com/legal)). Conda requires this for
  automated installs and it tells you so on screen.

You are done when it prints:

```
✓✓✓  mireasy is ready!  ✓✓✓
```

---

## Using MIReasy (every day)

Two buttons described in [HOW_TO_RUN.md](HOW_TO_RUN.md):

- **`analyze_folder.command`**: analyze everything automatically → CSV.
- **`run_mireasy.command`**: explore interactively.

Both: double-click (same one-time unblock as Step 3), **drag your audio folder
into the window** and press Return. Results land in an **`Analysis_…`** folder in
`mireasy-main`.

## If anything goes wrong

Every run writes a file called **`install_log.txt`** inside `mireasy-main`.
Open a new email or issue to the mireasy author, **send `install_log.txt`**, it contains everything needed to help you. 
You can alwayssafely re-run `install.command`. It shouldn't break an existing installation.

**If double-clicking opens the file in a text editor instead of running it**
(or nothing happens): open **Terminal** (⌘-space, type "Terminal", Return),
type `zsh ` (with a space), **drag `install.command` into the Terminal
window**, and press Return. This should work.

---

<details>
<summary><b>Appendix: manual installation (for terminal users)</b></summary>

```bash
git clone https://github.com/Atilik/mireasy.git
cd mireasy
conda env create -f environment.yml
conda activate mireasy
python download_models.py     # optional: enables genre/mood/pitch features
python run_tests.py           # should finish with "… passed" and no failures
python -m mireasy /path/to/audio/
```

Requirements: conda and git. Nothing compiles — the two non-PyPI dependencies
install from prebuilt wheels in `wheels/` (see `wheels/README.md`).
See README.md for the full feature documentation.
</details>
