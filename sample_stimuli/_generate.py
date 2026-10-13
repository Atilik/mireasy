"""Regenerates the synthetic sample stimuli in this folder.

All audio is fully synthetic (no copyrighted material): drum hits are shaped
noise/sine sweeps, tonal parts are additive synthesis. Filenames carry the
ground truth (tempo, key) so users can check mireasy's output against it.

Run:  python sample_stimuli/_generate.py
"""
import numpy as np
import soundfile as sf
import os

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261013)


def _env(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))


def kick(dur=0.30):
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 120 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * _env(n, 0.10)


def snare(dur=0.20):
    n = int(dur * SR)
    noise = np.diff(rng.standard_normal(n + 1))          # high-pass-ish noise
    tone = np.sin(2 * np.pi * 185 * np.arange(n) / SR)
    return (0.7 * noise / np.abs(noise).max() + 0.4 * tone) * _env(n, 0.05)


def hat(dur=0.06):
    n = int(dur * SR)
    noise = np.diff(np.diff(rng.standard_normal(n + 2)))
    return noise / np.abs(noise).max() * _env(n, 0.015)


def tone(freq, dur, bright=8):
    """Additive quasi-saw note with a soft attack and exponential decay."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, bright + 1))
    attack = np.minimum(t / 0.02, 1.0)
    return y * attack * _env(n, dur * 0.8)


def place(canvas, snippet, t0):
    i = int(t0 * SR)
    j = min(i + len(snippet), len(canvas))
    canvas[i:j] += snippet[: j - i]


def normalize(y, peak=0.9):
    return y / np.abs(y).max() * peak


def drum_track(bpm, length_s, pattern):
    """pattern: list of (instrument, beat_offset) repeated every bar (4 beats)."""
    y = np.zeros(int(length_s * SR))
    spb = 60.0 / bpm
    bar = 0.0
    while bar * spb < length_s - 1:
        for inst, off in pattern:
            place(y, inst(), (bar + off) * spb)
        bar += 4
    return y


def main():
    songs = {}

    # 1. Steady four-on-the-floor at 120 BPM — low syncopation.
    songs["01_steady_drums_120bpm.wav"] = normalize(drum_track(
        120, 8.0,
        [(kick, 0), (kick, 1), (kick, 2), (kick, 3),
         (snare, 1), (snare, 3),
         (hat, 0.5), (hat, 1.5), (hat, 2.5), (hat, 3.5)]))

    # 2. Offbeat-heavy pattern at 95 BPM — high syncopation.
    songs["02_syncopated_drums_95bpm.wav"] = normalize(drum_track(
        95, 8.0,
        [(kick, 0), (kick, 1.75), (kick, 2.5), (snare, 1.25), (snare, 3.5),
         (hat, 0.75), (hat, 1.5), (hat, 2.25), (hat, 3.25)]))

    # 3. A-minor melody at 140 BPM over an A-minor drone, light percussion.
    y = drum_track(140, 8.0, [(kick, 0), (kick, 2), (hat, 1), (hat, 3)]) * 0.5
    A, C, E = 220.0, 261.63, 329.63
    for f in (A / 2, C / 2, E / 2):
        place(y, tone(f, 7.5, bright=4) * 0.25, 0.0)
    melody = [A, C, E, 440.0, E, C, A, E, A, C, E, C, A, C, A, A / 2]
    spb = 60.0 / 140
    for i, f in enumerate(melody):
        place(y, tone(f, spb * 0.9) * 0.6, i * spb * 2 % 7.5)
    songs["03_melody_a_minor_140bpm.wav"] = normalize(y)

    # 4. C-major chords (C-F-G-C) at 80 BPM with a soft kick on each beat.
    y = drum_track(80, 9.0, [(kick, 0), (kick, 1), (kick, 2), (kick, 3)]) * 0.35
    chords = [(261.63, 329.63, 392.00), (349.23, 440.00, 523.25),
              (392.00, 493.88, 587.33), (261.63, 329.63, 392.00)]
    spb = 60.0 / 80
    for i, chord in enumerate(chords):
        for f in chord:
            place(y, tone(f, spb * 3.8, bright=6) * 0.4, i * 4 * spb / 2)
    songs["04_chords_c_major_80bpm.wav"] = normalize(y)

    # 5. Quiet ambient pad, no drums — low loudness, non-rhythmic material.
    n = int(10.0 * SR)
    t = np.arange(n) / SR
    pad = sum(np.sin(2 * np.pi * f * t + p) for f, p in
              [(110, 0.0), (165, 1.1), (220, 2.3), (277, 0.7)])
    slow_noise = np.convolve(rng.standard_normal(n), np.ones(2000) / 2000, "same")
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
    songs["05_quiet_ambient_no_drums.wav"] = normalize(
        (pad + 3 * slow_noise) * swell, peak=0.12)

    for name, y in songs.items():
        sf.write(os.path.join(HERE, name), y.astype(np.float32), SR,
                 subtype="PCM_16")
        print(f"wrote {name}  ({len(y)/SR:.1f} s)")


if __name__ == "__main__":
    main()
