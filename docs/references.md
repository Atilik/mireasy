# 📚 References

mireasy stands on established open-source MIR software. If you use mireasy in your
research, please also cite the tools that computed your measures:

**Beat & downbeat tracking: [Beat This!](https://github.com/CPJKU/beat_this)**
- Foscarin, F., Schlüter, J., & Widmer, G. (2024). Beat This! Accurate beat tracking without DBN postprocessing. *Proceedings of the 25th International Society for Music Information Retrieval Conference (ISMIR)*.

**Drum separation: [Demucs](https://github.com/adefossez/demucs)**
- Rouard, S., Massa, F., & Défossez, A. (2023). Hybrid Transformers for music source separation. *Proceedings of ICASSP 2023*.
- Défossez, A. (2021). Hybrid spectrogram and waveform source separation. *Proceedings of the ISMIR 2021 Workshop on Music Source Separation (MDX)*.

**Key detection & audio analysis framework: [Essentia](https://essentia.upf.edu)**
- Bogdanov, D., Wack, N., Gómez, E., Gulati, S., Herrera, P., Mayor, O., Roma, G., Salamon, J., Zapata, J. R., & Serra, X. (2013). Essentia: An audio analysis library for music information retrieval. *Proceedings of the 14th International Society for Music Information Retrieval Conference (ISMIR)*, 493–498.

**Key profiles used by Essentia's key detection**
- Faraldo, Á., Jordà, S., & Herrera, P. (2017). A multi-profile method for key estimation in EDM. *Proceedings of the 2017 AES International Conference on Semantic Audio*.

**Pre-trained genre / mood / voice models: [Essentia models](https://essentia.upf.edu/models.html)**
- Alonso-Jiménez, P., Bogdanov, D., Pons, J., & Serra, X. (2020). TensorFlow audio models in Essentia. *Proceedings of ICASSP 2020*.
- Alonso-Jiménez, P., Serra, X., & Bogdanov, D. (2022). Music representation learning based on editorial metadata from Discogs. *Proceedings of the 23rd International Society for Music Information Retrieval Conference (ISMIR)*.

**Pitch tracking: CREPE (via Essentia)**
- Kim, J. W., Salamon, J., Li, P., & Bello, J. P. (2018). CREPE: A convolutional representation for pitch estimation. *Proceedings of ICASSP 2018*.

**Loudness (LUFS): [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm)**
- Steinmetz, C. J., & Reiss, J. D. (2021). pyloudnorm: A simple yet flexible loudness meter in Python. *150th Convention of the Audio Engineering Society*.
- ITU-R BS.1770-4 (2015). Algorithms to measure audio programme loudness and true-peak audio level.

**Audio loading & spectral features: [librosa](https://librosa.org)**
- McFee, B., Raffel, C., Liang, D., Ellis, D. P. W., McVicar, M., Battenberg, E., & Nieto, O. (2015). librosa: Audio and music signal analysis in Python. *Proceedings of the 14th Python in Science Conference (SciPy)*, 18–25.

**Rhythm evaluation utilities: [mir_eval](https://github.com/craffel/mir_eval)**
- Raffel, C., McFee, B., Humphrey, E. J., Salamon, J., Nieto, O., Liang, D., & Ellis, D. P. W. (2014). mir_eval: A transparent implementation of common MIR metrics. *Proceedings of the 15th International Society for Music Information Retrieval Conference (ISMIR)*.

**Syncopation measure**
- Lerdahl, F., & Jackendoff, R. (1983). *A Generative Theory of Tonal Music*. MIT Press.
- Toussaint, G. T. (2002). A mathematical analysis of African, Brazilian, and Cuban clave rhythms. *Proceedings of BRIDGES: Mathematical Connections in Art, Music and Science*, 157–168.
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
