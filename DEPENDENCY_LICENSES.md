# Dependency licenses

What MIReasy is built on, and under which license. Checked on 2026-11-24
against the package metadata of a new installation (87 packages) and the
publishers' own pages.

## Summary

1. **MIReasy's own code is BSD 3-Clause.** It contains no copied third-party
   code.
2. **Essentia is AGPL-3.0.** MIReasy uses it for key detection, pitch (CREPE)
   and the genre, mood and voice classifiers. If you pass MIReasy on together
   with Essentia, the AGPL conditions can apply to the whole. MTG also offers
   Essentia under a commercial license on request.
3. **The Essentia models are CC BY-NC-SA 4.0: non-commercial use only.** This
   covers the genre, mood, voice and CREPE pitch models that
   `mireasy-download-models` fetches from MTG.
4. **The Demucs model weights have no clear license.** The Demucs author
   writes: "The license of the weights is not clear: MusDB contains some data
   that were only usable for research purpose." Drum separation, and so the
   syncopation score, should be treated as research use only.

In short: MIReasy is free to use for research. It is not cleared for
commercial use.

## Direct dependencies

Versions are those of a new installation on that day, with Python 3.11. The
conda recipe in `environment.yml` pins some older versions.

| Package | Version | License | Used for |
|---|---|---|---|
| [beat-this](https://github.com/CPJKU/beat_this) | 1.1.0 | **MIT**, code and published model weights. The authors note that some of the training data is copyrighted or under limited Creative Commons licenses. | Beat, downbeat and meter detection |
| [demucs](https://github.com/adefossez/demucs) | 4.1.0 | **MIT** for the code. Model weights: not clear (see summary). | Drum separation for syncopation |
| [essentia-tensorflow](https://essentia.upf.edu) | 2.1b6.dev1389 | **AGPL-3.0** (the wheel bundles TensorFlow, Apache-2.0) | Key detection, CREPE pitch, genre/mood classifiers |
| Essentia models | fetched by `mireasy-download-models`, not shipped in the package | **CC BY-NC-SA 4.0**. The CREPE model is derived from MIT licensed work. | Genre, mood, voice/instrumental, CREPE pitch |
| [librosa](https://librosa.org) | 0.11.0 | ISC | Audio loading, spectral features |
| [mir_eval](https://github.com/craffel/mir_eval) | 0.8.2 | MIT | Rhythm metric utilities |
| [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm) | 0.2.0 | MIT | LUFS loudness |
| [numpy](https://numpy.org) | 2.4.6 | BSD-3-Clause | Numerical core |
| [scipy](https://scipy.org) | 1.17.1 | BSD-3-Clause | Filters, signal processing |
| [torch](https://pytorch.org) | 2.15.0 | BSD-3-Clause | Neural network runtime (beat-this, demucs) |
| torchaudio | 2.11.1 | BSD-2-Clause | Audio I/O for torch models |
| [matplotlib](https://matplotlib.org) | 3.11.2 | Matplotlib license (PSF-based, BSD-compatible) | Plots, interactive player |
| [soundfile](https://python-soundfile.readthedocs.io) | 0.14.0 | BSD-3-Clause | Audio file reading and writing |
| [sounddevice](https://python-sounddevice.readthedocs.io) | 0.5.6 | MIT | Audio playback |
| [IPython](https://ipython.org) | 9.19.1 | BSD-3-Clause | Interactive shell |
| [certifi](https://github.com/certifi/python-certifi) | 2026.11.20 | MPL-2.0 | Root certificates for the model downloads |

## Other pieces worth knowing

| Component | License | Note |
|---|---|---|
| soxr, lameenc, libsndfile (inside soundfile) | LGPL | Installed through librosa, beat-this and demucs |
| tqdm | MPL-2.0 | Installed through other packages |
| NVIDIA CUDA libraries | NVIDIA proprietary license | Linux only: about 15 packages that PyTorch pulls in from PyPI |
| TensorFlow (inside essentia-tensorflow) | Apache-2.0 | Runs the classifier models |
| FFmpeg | GPL or LGPL, depending on the build | Optional, a separate program used to read formats such as .m4a |
| Python | PSF-2.0 | |
| Tcl/Tk (tkinter) | BSD-style | GUI windows for `play()` and `plot()` |

All other packages in the dependency tree (about 65) carry permissive
licenses: MIT, BSD, Apache-2.0, ISC or PSF.
