# Using MIReasy

## 🚀 Getting Started

Open a terminal and launch the tool with the path to an audio file, a session folder,
or a participant folder:

```bash
# Load a single song:
mireasy /path/to/song.wav

# Load a session (folder of audio files):
mireasy /path/to/session_folder/

# Load a participant (folder containing session folders):
mireasy /path/to/participant_folder/
```

This drops you into an interactive Python shell pre-loaded with your data. Leave it with `exit()` or Ctrl-D.

Prefer scripts or notebooks? See [Measures](measures.md): `from mireasy import Stimulus, Session, Participant`.

---

## 📖 The Hierarchy

`mireasy` structures your data into three levels depending on the folder you pass:

1. **Participant**: A folder containing multiple *Session* folders.
2. **Session**: A folder containing multiple *Stimulus* audio files.
3. **Stimulus**: A single audio file (e.g., a `.wav` or `.mp3`).

When you load a folder, `mireasy` automatically gives you variables (`participant`, `session`, `stimulus`) to interact with your data immediately.

---

## 💻 Using the Interactive Shell

Type the following commands directly into the terminal once `mireasy` is launched:

### Navigating Data
- `participant(1)`: Focus on the 1st session. Updates the `session` and `stimulus` variables.
- `participant("baseline")`: Focus on a session containing "baseline" in its folder name.
- `session(3)`: Focus on the 3rd song in the current session. Updates the `stimulus` variable.
- `session("beatles")`: Focus on a song containing "beatles" in its filename.

### Viewing Info
- `stimulus.help()`: List all available attributes and methods for the current song.
- `session.help()`: List all available methods for the session.
- `participant.help()`: List all available methods for the participant.
- `stimulus.print()`: Print a summary of the current song (loudness, BPM, syncopation, key, etc.).
- `session.print()`: List the songs in the current session.
- `participant.print()`: List the sessions loaded for this participant.

### Interactive Player & Viz
- **`stimulus.play()`**
  Launch the interactive unified player. You can switch between Waveform, Mel, Log, Linear, and Pitch views. Click **Beats** or **Onsets** to visualize and sonify rhythm markers directly over the audio playback.
- `stimulus.plot()`: Spectrogram window (`scale='mel'` by default, or `'linear'` / `'log'`).
- `session.boxplot()`: Boxplots of BPM, LUFS, and syncopation across the session.

### Getting Metrics
Access properties on-the-fly. If a metric hasn't been computed yet, `mireasy` computes it on first access (model-based metrics take a few seconds).
```python
>>> stimulus.bpm
120.5
>>> stimulus.key
'C#'
>>> stimulus.scale
'minor'
>>> stimulus.syncopation_score()
31
```

The syncopation score goes from 0 to 100. It separates the drums first if needed.

### Exporting Data
- `stimulus.process_and_save("output_folder")`
  Computes ALL available metrics (beats, syncopation, loudness, genre, mood, key, etc.) for the specific song and saves them to a CSV file.
- `session.process_and_save("output_folder")`
  Computes ALL available metrics for every song in the session and saves them to a CSV file.
- `participant.process_and_save("output_folder")`
  Does the same, but loops through every session folder, adding a `session` column to the final CSV.
- `stimulus.partial_process_save(rhythm=True, pitch=True)`
  Computes only the selected feature groups (`rhythm`, `syncopation`, `genre`, `pitch`, `key`, `spectral`) instead of everything. `rhythm` is beats/BPM only (fast); `syncopation` runs Demucs separation + scoring (slow). Available on `session` and `participant` too.

Results are written to `output_folder/Analysis_DD-MM-YYYY/mireasy_HH-MM-SS.csv` (the exact path is printed after saving).

### Aggregate Metrics
- `session.average_fluctuation` / `session.average_irregularity`: Mean fluctuation / spectral irregularity across the session's songs.
- `participant.average_fluctuation` / `participant.average_irregularity`: Same, across every song in every session.

---

## 🛠 Advanced Features

### Separation & Syncopation
Syncopation requires isolating the drums with Demucs. The first time you ask for a syncopation score, `mireasy` asks for confirmation (`Proceed? [Y/n]`): on a CPU, separation takes roughly as long as the song itself.
```python
>>> stimulus.syncopation_score()
```

### Pitch Tracking
The pitch view mode in `stimulus.play()` runs CREPE pitch detection.
```python
>>> stimulus.pitch_time
>>> stimulus.pitch_freq
```

---

## 🧪 Running Tests

```bash
# Fast suite: synthetic audio only (~15 s with classifier models installed)
python run_tests.py

# Also run the slow model tests (BEAT THIS! beat detection, Demucs separation
# if the htdemucs checkpoint is already cached)
MIREASY_RUN_SLOW=1 python run_tests.py
```

Tests that need the Essentia classifier models skip automatically while those
files are absent, run `mireasy-download-models` (or `python download_models.py`
in the repository) to activate them.
