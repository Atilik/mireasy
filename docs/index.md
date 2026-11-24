# MIReasy: Music Analysis Toolbox

**Easy to use, accessible, and reproducible Music Information Retrieval (MIR) for researchers outside of MIR.**

MIReasy is built for researchers outside of MIR who need established audio measures for their stimuli.
MIReasy gives you tempo, loudness, syncopation, key, pitch, genre, mood, and more without 
writing any code. Drag and drop an audio folder or file of an experiment and it extracts the information 
using established MIR tools and produces a CSV with one row per stimulus through one interface. 
Please see the [References](references.md) page for more information on the incorporated methodologies. 

**All analysis runs locally on your computer.** The internet is needed only to install the
software and download the analysis models once. Your audio files and your results never
leave your machine.

You can work in two ways: an interactive shell to load, analyze, and visualize audio
individually, by session (folder of songs), or by participant (folder of sessions); or from
your own Python scripts and notebooks ([Measures](measures.md)).

---

## 🏁 Quick example: what do I actually get?

> *"I have 40 music stimuli for an experiment. I want the tempo, loudness, and
> spectral brightness of each one. What do I do?"*

**From the terminal** (after [installation](installation.md)):

```bash
python -c 'from mireasy import mireasy; mireasy("/path/to/my_stimuli").process_and_save(".")'
```

You get a CSV with one row per stimulus and 45 columns of measures. `bpm` is your
tempo, `loudness_lufs` your loudness, and `spectral_centroid_mean` your spectral
brightness.

**Try it right now:** MIReasy ships [`mireasy/sample_stimuli/`](https://github.com/Atilik/mireasy/tree/main/mireasy/sample_stimuli),
five fully synthetic test "songs" (no copyrighted audio; tempo and key are in
the filenames so you can check the tool). `mireasy --demo` opens them, and
analyzing that folder gives:

| filename | bpm | syncopation_score | key | scale | loudness_lufs | spectral_centroid_mean | … |
|---|---|---|---|---|---|---|---|
| 01_steady_drums_120bpm.mp3 | 120.0 | 52 | F# | minor | −20.2 | 5248 | … |
| 02_syncopated_drums_95bpm.mp3 | 187.5 † | 57 | F# | major | −17.3 | 5464 | … |
| 03_melody_a_minor_140bpm.mp3 | 142.9 | 44 | A | minor | −17.3 | 997 | … |
| 04_chords_c_major_80bpm.mp3 | 81.1 | 31 | C | major | −16.7 | 861 | … |
| 05_quiet_ambient_no_drums.mp3 | 81.1 ‡ | 0 | A | major | −31.2 | 251 | … |

(…plus genre, mood, pitch, and more, 45 columns in total, grouped by topic;
see [Measures](measures.md) for every column's meaning.)

The sample set is deliberately imperfect, because real results are too:
**†** file 02 shows a *double-time octave error* (187.5 ≈ 2 × 95): a known
behavior of beat trackers on off-beat-heavy material; **‡** beat-based measures
are not meaningful for non-rhythmic audio like file 05, and the key of
drums-only files (01, 02) is likewise noise. Knowing which measures apply to
which stimuli is part of using MIR responsibly.

---

## Features

- **Rhythm & Syncopation**: Beat and downbeat tracking using BEAT THIS!, tempo estimation (BPM), and a syncopation score inspired by Toussaint.
- **Stem Separation**: Drum separation using Demucs.
- **Timbre & Dynamics**: LUFS loudness, RMS energy, spectral irregularity, and fluctuation strength.
- **Harmony & Pitch**: Key and scale extraction (Essentia), and frame-level pitch tracking (CREPE).
- **Genre & Mood**: Pre-trained deep learning classifiers for genre, mood, and voice/instrumental detection (Essentia).
- **Interactive Player**: A built-in GUI player (`play()`) to view waveforms, spectrograms (linear/log/mel), and pitch contours, while sonifying detected beats and onsets over the audio.
- **Batch Processing**: Automatic process and save everything as CSV (`process_and_save()`).

```{toctree}
:hidden:
:maxdepth: 2

Installation <installation>
Using MIReasy <guide>
Measures <measures>
API reference <api/index>
References <references>
Contributing <CONTRIBUTING>
Dependency licenses <DEPENDENCY_LICENSES>
```
