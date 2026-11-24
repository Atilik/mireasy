"""Root certificates for the model downloads.

Python from python.org on a Mac has no root certificates until its "Install
Certificates" command has been run. Without them these downloads fail with
``CERTIFICATE_VERIFY_FAILED``: the Essentia models, the BEAT THIS! model, and
the Demucs model with Demucs 4.0 (Demucs 4.1 takes its model from the Hugging
Face hub, which brings its own certificates).

:func:`ensure_certificates` runs when mireasy is imported. If Python has no
certificates, it sets the ``SSL_CERT_FILE`` environment variable to the
certificate bundle of the certifi package, for the current process. A Python
that has its own certificates is left alone, and so is a process where
``SSL_CERT_FILE`` or ``SSL_CERT_DIR`` is already set.
"""
import os
import ssl


def _python_has_certificates():
    paths = ssl.get_default_verify_paths()
    if paths.cafile:
        return True
    if paths.capath is None:
        return False
    try:
        return bool(os.listdir(paths.capath))
    except OSError:
        return False


def ensure_certificates():
    """Point Python at certifi's certificates if it has none of its own.

    Returns True when ``SSL_CERT_FILE`` was set, False when nothing changed.
    """
    if os.environ.get("SSL_CERT_FILE") or os.environ.get("SSL_CERT_DIR"):
        return False
    if _python_has_certificates():
        return False
    try:
        import certifi
    except ImportError:
        return False
    os.environ["SSL_CERT_FILE"] = certifi.where()
    return True
