# Bundled wheels

Why bundle at all? BEAT THIS! is not on PyPI. Installing it from its git URL
requires `git`, which fresh Macs only get via the Xcode Command Line Tools.
Bundling the wheel keeps the install git-free — and since it is pure Python,
compiler-free on every platform.

## beat_this-1.1.0-py3-none-any.whl

- **Source:** https://github.com/CPJKU/beat_this tag `v1.1.0`
  (commit `ad79748…`); pure-Python wheel, works on any platform and any
  supported Python version.
- **Built:** 2026-09-29 (`pip wheel --no-deps`), unmodified.
- **sha256:** `8a56f9847c8e51a00a523cb12fbba8983a97599a3060d45efc22acbb71cc6dc2`
- **License:** MIT (CPJKU) — explicitly covers the code *and* the published
  model weights, which BEAT THIS! downloads on first use (~80 MB, cached).

### Rebuild it yourself

```bash
python -m pip wheel \
  "beat_this @ git+https://github.com/CPJKU/beat_this@v1.1.0" \
  --no-deps --no-cache-dir -w wheels/
```

## History

Until 2026-10-25 this folder also carried a compiled madmom wheel (macOS /
Apple Silicon / CPython 3.11 only). madmom was a legacy fallback beat tracker
that no code path used by default; it was removed so that the install has no
compiled, platform-specific dependency and can run on Linux and on several
Python versions. BEAT THIS! provides beats, downbeats and meter for everything.
