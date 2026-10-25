# MIReasy: Music Analysis Toolbox

[![tests](https://github.com/Atilik/mireasy/actions/workflows/tests.yml/badge.svg)](https://github.com/Atilik/mireasy/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/Atilik/mireasy/branch/main/graph/badge.svg)](https://codecov.io/gh/Atilik/mireasy)


**Easy to use, accessible, and reproducible Music Information Retrieval (MIR) for researchers outside of MIR.**

MIReasy is built for researchers outside of MIR who need established audio measures for their stimuli.
MIReasy gives you tempo, loudness, syncopation, key, pitch, genre, mood, and more without 
writing any code. Drag and drop an audio folder or file of an experiment and it extracts the information 
using established MIR tools and produces a CSV with one row per stimulus through one interface. 
Please see the **References** section at the end for more information on the incorporated methodologies. 

**All analysis runs locally on your computer.** The internet is needed only to install the
software and download the analysis models once. Your audio files and your results never
leave your machine.

You can work in two ways: an interactive shell to load, analyze, and visualize audio —
individually, by session (folder of songs), or by participant (folder of sessions) — or from
your own Python scripts and notebooks ([DOCUMENTATION.md](DOCUMENTATION.md)).

**Jump to:** [Quick example](#-quick-example-what-do-i-actually-get) ·
[Features](#features) · [Setup](INSTALLATION.md) ·
[Getting help](#-getting-help) · [References](#-references)

---

## 🏁 Quick example: what do I actually get?

> *"I have 40 music stimuli for an experiment. I want the tempo, loudness, and
> spectral brightness of each one. What do I do?"*

**From the terminal** (after Setup below):

```bash
conda activate mireasy
cd /path/to/mireasy
python -c 'from mireasy import mireasy; mireasy("/path/to/my_stimuli").process_and_save(".")'
```

You get a CSV with one row per stimulus and 44 columns of measures. `bpm` is your
tempo, `loudness_lufs` your loudness, and `spectral_centroid_mean` your spectral
brightness.

**Try it right now:** the repo ships [`sample_stimuli/`](sample_stimuli/) —
five fully synthetic test "songs" (no copyrighted audio; tempo and key are in
the filenames so you can check the tool). Analyzing that folder gives:

| filename | bpm | syncopation_score | key | scale | loudness_lufs | spectral_centroid_mean | … |
|---|---|---|---|---|---|---|---|
| 01_steady_drums_120bpm.wav | 120.0 | 52 | F# | minor | −20.2 | 4505 | … |
| 02_syncopated_drums_95bpm.wav | 187.5 † | 61 | F# | major | −17.3 | 4449 | … |
| 03_melody_a_minor_140bpm.wav | 142.9 | 44 | A | minor | −17.3 | 974 | … |
| 04_chords_c_major_80bpm.wav | 81.1 | 38 | C | major | −16.7 | 787 | … |
| 05_quiet_ambient_no_drums.wav | 25.6 ‡ | 0 | A | major | −31.2 | 557 | … |

(…plus genre, mood, pitch, and more — 44 columns in total, grouped by topic;
see [DOCUMENTATION.md](DOCUMENTATION.md) for every column's meaning.)

The sample set is deliberately imperfect, because real results are too:
**†** file 02 shows a *double-time octave error* (187.5 ≈ 2 × 95) — a known
behavior of beat trackers on off-beat-heavy material; **‡** beat-based measures
are not meaningful for non-rhythmic audio like file 05, and the key of
drums-only files (01, 02) is likewise noise. Knowing which measures apply to
which stimuli is part of using MIR responsibly.

---

## Features

- **Rhythm & Syncopation**: Beat and downbeat tracking using BEAT THIS!, tempo estimation (BPM), and Toussaint syncopation scoring.
- **Stem Separation**: Drum separation using Demucs.
- **Timbre & Dynamics**: LUFS loudness, RMS energy, spectral irregularity, and fluctuation strength.
- **Harmony & Pitch**: Key and scale extraction (Essentia), and frame-level pitch tracking (CREPE).
- **Genre & Mood**: Pre-trained deep learning classifiers for genre, danceability, mood, and voice/instrumental detection (Essentia).
- **Interactive Player**: A built-in GUI player (`play()`) to view waveforms, spectrograms (linear/log/mel), and pitch contours, while sonifying detected beats and onsets over the audio.
- **Batch Processing**: Automatic process and save everything as CSV (`process_and_save()`).

---

## 🛠️ How to Setup mireasy

> ### 🖱️ Never used a terminal? Start here → **[INSTALLATION.md](INSTALLATION.md)**
> A step-by-step guide that assumes zero experience.

**Supported platforms:** Apple Silicon Macs (M1 or newer) on macOS 15+.
Intel Macs are not supported. Linux is expected to work but is untested — for
audio playback, install PortAudio (`sudo apt install libportaudio2`). Windows
is not supported natively (use WSL2).

**Quickstart for terminal users** (needs [conda](https://docs.conda.io/en/latest/miniconda.html)
and git; nothing compiles — the one non-PyPI dependency ships as a prebuilt
wheel in `wheels/`):

```bash
git clone https://github.com/Atilik/mireasy.git
cd mireasy
conda env create -f environment.yml
conda activate mireasy
python download_models.py     # optional: enables genre/mood/pitch features
python run_tests.py           # should finish with "… passed" and no failures
python -m mireasy /path/to/audio/
```

**Notes**
- Reinstalling? `conda env remove -n mireasy` first — `conda env create` won't
  overwrite an existing environment.
- On first analysis run, the beat tracker (BEAT THIS!) and Demucs download
  their own checkpoints automatically (~100 MB, one time) — so the first song
  takes longer and needs an internet connection.

---

## 🚀 Getting Started

Open a terminal, activate the environment, and go to the repo folder (the one containing
this `README.md`). Then launch the tool with the path to an audio file, a session folder,
or a participant folder:

```bash
conda activate mireasy
cd /path/to/mireasy           # the repo folder

# Load a single song:
python -m mireasy /path/to/song.wav

# Load a session (folder of audio files):
python -m mireasy /path/to/session_folder/

# Load a participant (folder containing session folders):
python -m mireasy /path/to/participant_folder/
```

This drops you into an interactive Python shell pre-loaded with your data. Leave it with `exit()` or Ctrl-D.

Prefer scripts or notebooks? See [DOCUMENTATION.md](DOCUMENTATION.md) — `from mireasy import Stimulus, Session, Participant`.

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
- `participant(1)` — Focus on the 1st session. Updates the `session` and `stimulus` variables.
- `participant("baseline")` — Focus on a session containing "baseline" in its folder name.
- `session(3)` — Focus on the 3rd song in the current session. Updates the `stimulus` variable.
- `session("beatles")` — Focus on a song containing "beatles" in its filename.

### Viewing Info
- `stimulus.help()` — List all available attributes and methods for the current song.
- `session.help()` — List all available methods for the session.
- `participant.help()` — List all available methods for the participant.
- `stimulus.print()` — Print a summary of the current song (loudness, BPM, syncopation, key, etc.).
- `session.print()` — List the songs in the current session.
- `participant.print()` — List the sessions loaded for this participant.

### Interactive Player & Viz
- **`stimulus.play()`**
  Launch the interactive unified player. You can switch between Waveform, Mel, Log, Linear, and Pitch views. Click **Beats** or **Onsets** to visualize and sonify rhythm markers directly over the audio playback.
- `stimulus.plot()` — Spectrogram window (`scale='mel'` by default, or `'linear'` / `'log'`).
- `session.boxplot()` — Boxplots of BPM, LUFS, and syncopation across the session.

### Getting Metrics
Access properties on-the-fly. If a metric hasn't been computed yet, `mireasy` computes it on first access (model-based metrics take a few seconds).
```python
>>> stimulus.bpm
120.5
>>> stimulus.key
'C#'
>>> stimulus.scale
'minor'
>>> stimulus.syncopation_score()   # 0–100; separates the drums first if needed
31
```

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
- `session.average_fluctuation` / `session.average_irregularity` — Mean fluctuation / spectral irregularity across the session's songs.
- `participant.average_fluctuation` / `participant.average_irregularity` — Same, across every song in every session.

---

## 🛠 Advanced Features

### Separation & Syncopation
Syncopation requires isolating the drums with Demucs. The first time you ask for a syncopation score, `mireasy` asks for confirmation (`Proceed? [Y/n]`) — on a CPU, separation takes roughly as long as the song itself.
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
# Fast suite — synthetic audio only (~15 s with classifier models installed)
python run_tests.py

# Also run the slow model tests (BEAT THIS! beat detection, Demucs separation
# if the htdemucs checkpoint is already cached)
MIREASY_RUN_SLOW=1 python run_tests.py
```

Tests that need the Essentia classifier models (`mireasy/models/*.pb`)
skip automatically while those files are absent — run `python download_models.py`
to activate them.

---

## 🆘 Getting help

Stuck, found a bug, or unsure what a measure means? **Open an issue** at
<https://github.com/Atilik/mireasy/issues> — it's a public message to us, no
programming involved, and **[CONTRIBUTING.md](CONTRIBUTING.md) walks you
through it click by click**.
Feature requests and pull requests are covered there too.

---

## 📚 References

mireasy stands on established open-source MIR software. If you use mireasy in your
research, please also cite the tools that computed your measures:

**Beat & downbeat tracking — [Beat This!](https://github.com/CPJKU/beat_this)**
- Foscarin, F., Schlüter, J., & Widmer, G. (2024). Beat This! Accurate beat tracking without DBN postprocessing. *Proceedings of the 25th International Society for Music Information Retrieval Conference (ISMIR)*.

**Drum separation — [Demucs](https://github.com/adefossez/demucs)**
- Rouard, S., Massa, F., & Défossez, A. (2023). Hybrid Transformers for music source separation. *Proceedings of ICASSP 2023*.
- Défossez, A. (2021). Hybrid spectrogram and waveform source separation. *Proceedings of the ISMIR 2021 Workshop on Music Source Separation (MDX)*.

**Key detection & audio analysis framework — [Essentia](https://essentia.upf.edu)**
- Bogdanov, D., Wack, N., Gómez, E., Gulati, S., Herrera, P., Mayor, O., Roma, G., Salamon, J., Zapata, J. R., & Serra, X. (2013). Essentia: An audio analysis library for music information retrieval. *Proceedings of the 14th International Society for Music Information Retrieval Conference (ISMIR)*, 493–498.

**Pre-trained genre / mood / voice models — [Essentia models](https://essentia.upf.edu/models.html)**
- Alonso-Jiménez, P., Bogdanov, D., Pons, J., & Serra, X. (2020). TensorFlow audio models in Essentia. *Proceedings of ICASSP 2020*.
- Alonso-Jiménez, P., Serra, X., & Bogdanov, D. (2022). Music representation learning based on editorial metadata from Discogs. *Proceedings of the 23rd International Society for Music Information Retrieval Conference (ISMIR)*.

**Pitch tracking — CREPE (via Essentia)**
- Kim, J. W., Salamon, J., Li, P., & Bello, J. P. (2018). CREPE: A convolutional representation for pitch estimation. *Proceedings of ICASSP 2018*.

**Loudness (LUFS) — [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm)**
- Steinmetz, C. J., & Reiss, J. D. (2021). pyloudnorm: A simple yet flexible loudness meter in Python. *150th Convention of the Audio Engineering Society*.
- ITU-R BS.1770-4 (2015). Algorithms to measure audio programme loudness and true-peak audio level.

**Audio loading & spectral features — [librosa](https://librosa.org)**
- McFee, B., Raffel, C., Liang, D., Ellis, D. P. W., McVicar, M., Battenberg, E., & Nieto, O. (2015). librosa: Audio and music signal analysis in Python. *Proceedings of the 14th Python in Science Conference (SciPy)*, 18–25.

**Rhythm evaluation utilities — [mir_eval](https://github.com/craffel/mir_eval)**
- Raffel, C., McFee, B., Humphrey, E. J., Salamon, J., Nieto, O., Liang, D., & Ellis, D. P. W. (2014). mir_eval: A transparent implementation of common MIR metrics. *Proceedings of the 15th International Society for Music Information Retrieval Conference (ISMIR)*.

**Syncopation measure**
- Toussaint, G. T. (2013). *The Geometry of Musical Rhythm: What Makes a "Good" Rhythm Good?* CRC Press.

**Timbre measures (spectral irregularity, fluctuation strength)**
- Jensen, K. (1999). *Timbre Models of Musical Sounds* (Rapport 99/7). University of Copenhagen.
- Pampalk, E., Rauber, A., & Merkl, D. (2002). Content-based organization and visualization of music archives. *Proceedings of ACM Multimedia 2002*, 570–579.

**Feature organization (CSV grouping)**
- Salakka, I., Pitkäniemi, A., Pentikäinen, E., Mikkonen, K., Saari, P., Toiviainen, P., & Särkämö, T. (2021). What makes music memorable? Relationships between acoustic musical features and music-evoked emotions and memories in older adults. *PLoS ONE, 16*(5), e0251692.

**Scientific Python stack:** [NumPy](https://numpy.org) (Harris et al., 2020, *Nature*),
[SciPy](https://scipy.org) (Virtanen et al., 2020, *Nature Methods*),
[PyTorch](https://pytorch.org) (Paszke et al., 2019, *NeurIPS*),
[Matplotlib](https://matplotlib.org) (Hunter, 2007),
[python-sounddevice](https://python-sounddevice.readthedocs.io).
