# MIReasy: Music Analysis Toolbox

[![tests](https://github.com/Atilik/mireasy/actions/workflows/tests.yml/badge.svg)](https://github.com/Atilik/mireasy/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/Atilik/mireasy/branch/main/graph/badge.svg)](https://codecov.io/gh/Atilik/mireasy)
[![docs](https://img.shields.io/readthedocs/mireasy?label=docs)](https://mireasy.readthedocs.io/en/latest/)
[![license](https://img.shields.io/github/license/Atilik/mireasy)](https://github.com/Atilik/mireasy/blob/main/LICENSE.md)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Atilik/mireasy/blob/main/CONTRIBUTING.md)


**Easy to use, accessible, and reproducible Music Information Retrieval (MIR) for researchers outside of MIR.**

MIReasy is built for researchers outside of MIR who need established audio measures for their stimuli.
MIReasy gives you tempo, loudness, syncopation, key, pitch, genre, mood, and more without
writing any code. Drag and drop an audio folder or file of an experiment and it extracts the information
using established MIR tools and produces a CSV with one row per stimulus through one interface.
Please see the **References** section at the end for more information on the incorporated methodologies.

**All analysis runs locally on your computer.** The internet is needed only to install the
software and download the analysis models once. Your audio files and your results never
leave your machine.

You can work in two ways: an interactive shell to load, analyze, and visualize audio
individually, by session (folder of songs), or by participant (folder of sessions); or from
your own Python scripts and notebooks.

## 📖 Documentation

Everything is on the documentation site, **<https://mireasy.readthedocs.io>**:

- [Installation](https://mireasy.readthedocs.io/en/latest/installation.html): step by step, no terminal experience needed
- [Using MIReasy](https://mireasy.readthedocs.io/en/latest/guide.html): the interactive shell, the player, exporting a CSV
- [Measures](https://mireasy.readthedocs.io/en/latest/measures.html): what every column means
- [API reference](https://mireasy.readthedocs.io/en/latest/api/index.html): for your own scripts and notebooks
- [References](https://mireasy.readthedocs.io/en/latest/references.html): the methods behind the measures

## 🛠️ Install

Needs Python 3.11 to 3.14 on an Apple Silicon Mac (macOS 15+) or Linux. Windows is not supported for now.

```bash
pip install https://github.com/Atilik/mireasy/archive/refs/heads/main.zip
```

Then download the analysis models once (about 45 MB) and try MIReasy on the five test songs that come with it:

```bash
mireasy-download-models
mireasy --demo
```

To analyze your own audio: `mireasy /path/to/your/audio/`. New to the terminal? The
[installation guide](https://mireasy.readthedocs.io/en/latest/installation.html) walks you through every step.

## 🆘 Getting help

Stuck, found a bug, or unsure what a measure means? **Open an issue** at
<https://github.com/Atilik/mireasy/issues>. It's a public message to us, no
programming involved, and **[CONTRIBUTING.md](https://github.com/Atilik/mireasy/blob/main/CONTRIBUTING.md) walks you
through it click by click**.
Feature requests and pull requests are covered there too.

## 📚 References

mireasy stands on established open-source MIR software. If you use mireasy in your
research, please also cite the tools that computed your measures: they are listed on the
[References](https://mireasy.readthedocs.io/en/latest/references.html) page.

## License

MIReasy's own code is under the BSD 3-Clause license ([LICENSE.md](https://github.com/Atilik/mireasy/blob/main/LICENSE.md)).
Some of the tools it builds on have stronger terms: Essentia is AGPL-3.0, and the model weights are for
non-commercial or research use only. So MIReasy is free to use for research, but it is not cleared for
commercial use. Details are in [DEPENDENCY_LICENSES.md](https://github.com/Atilik/mireasy/blob/main/DEPENDENCY_LICENSES.md).
