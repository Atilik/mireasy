# Dependency licenses

An audit of every runtime dependency of mireasy, compiled so the project's own
license can be chosen with full information. Versions are the ones pinned by
`environment.yml` (audited 2026-10-13 from an installed environment; license
fields read from package metadata and verified against each project's
repository or website).

## Summary — the three things that matter

1. **mireasy's own code** contains no copied third-party code and can carry its
   own license (e.g. BSD-3-Clause). The questions below are about what we
   *depend on* and *redistribute*.
2. **Essentia's code is AGPL-3.0** — the strongest copyleft license. mireasy
   imports Essentia for key detection, pitch (CREPE), and the genre/mood
   classifiers. Depending on interpretation, distributing a program built on an
   AGPL library can carry AGPL obligations for the combined work. MTG offers
   the same software "under proprietary license upon request." **Decision
   needed:** accept this, negotiate with MTG, or make Essentia-dependent
   features an optional extra.
3. **All pretrained model weights from MTG (Essentia models, incl. the ported
   CREPE) are CC BY-NC-SA 4.0** — attribution, **non-commercial use only**,
   share-alike. In practice the package *as used for research* is fine, but
   the overall offering cannot be presented as unrestricted BSD-3. (madmom,
   whose bundled models carried the same license and were redistributed in
   this repository, was removed on 2026-10-25; BEAT THIS! — MIT, weights
   included — covers beat, downbeat and meter detection alone.)

## Direct dependencies

| Package | Version | License | Used for |
|---|---|---|---|
| [beat_this](https://github.com/CPJKU/beat_this) | 1.1.0 | **MIT** (explicitly covers code *and* published model weights) | Beat, downbeat and meter detection |
| [demucs](https://github.com/adefossez/demucs) | 4.0.1 | **MIT** (code; README does not state a license for the htdemucs weights — see open questions) | Drum separation for syncopation |
| [essentia-tensorflow](https://essentia.upf.edu) | 2.1b6.dev1389 | **AGPL-3.0** (code; wheel bundles TensorFlow, Apache-2.0) | Key detection, CREPE pitch, genre/mood classifiers |
| Essentia pretrained models | per `download_models.py` | **CC BY-NC-SA 4.0** ("All the models created by the MTG are licensed under CC BY-NC-SA 4.0"; proprietary license available on request) | Genre, mood, danceability, voice/instrumental, CREPE pitch |
| [librosa](https://librosa.org) | 0.11.0 | ISC | Audio loading, spectral features |
| [mir_eval](https://github.com/craffel/mir_eval) | 0.8.2 | MIT | Rhythm metric utilities |
| [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm) | 0.2.0 | MIT | LUFS loudness |
| [numpy](https://numpy.org) | 2.4.6 | BSD-3-Clause | Numerical core |
| [scipy](https://scipy.org) | 1.17.1 | BSD-3-Clause | Filters, signal processing |
| [torch](https://pytorch.org) | 2.8.0 | BSD-3-Clause | Neural network runtime (beat_this, demucs) |
| torchaudio | 2.8.0 | BSD-2-Clause | Audio I/O for torch models |
| [matplotlib](https://matplotlib.org) | 3.11.2 | Matplotlib license (PSF-based, BSD-compatible) | Plots, interactive player |
| [sounddevice](https://python-sounddevice.readthedocs.io) | 0.5.5 | MIT | Audio playback |
| [IPython](https://ipython.org) | 9.17.1 | BSD-3-Clause | Interactive shell |

## Notable transitive / runtime pieces

| Component | License | Note |
|---|---|---|
| soundfile 0.14.0 | BSD-3-Clause | via librosa |
| audioread 3.1.0 | MIT | via librosa |
| TensorFlow (bundled inside essentia-tensorflow) | Apache-2.0 | runs the classifier models |
| Python 3.11 | PSF-2.0 | via conda-forge |
| FFmpeg (conda-forge build) | **GPL build** | installed by `environment.yml`; invoked as a separate program for decoding (e.g. .m4a) — process-level use, not linked into mireasy |
| Tcl/Tk (tkinter) | BSD-style | GUI windows for `play()`/`plot()` |

## Open questions for the maintainers

1. Is AGPL-3.0 Essentia acceptable as a hard dependency, or should we contact
   MTG / make those features optional? (See summary point 2.)
2. Can the package's own code be published as BSD-3-Clause while documenting
   that the model weights are CC BY-NC-SA 4.0 (non-commercial)? Suggested
   wording would live in README + LICENSE.
3. Demucs htdemucs weights: the repo's MIT statement names the code; the
   weights are hosted on Hugging Face without an explicit statement on the
   README. Needs one check of the Hugging Face model card.
4. The conda-forge FFmpeg is its GPL build. Process-level invocation is
   generally considered fine, but if we ever want to be strict we can depend on
   the LGPL build instead.
