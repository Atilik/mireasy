"""Tests for mireasy.certs: downloads must work on a Python without certificates.

Python from python.org on a Mac has no root certificates until its "Install
Certificates" command has been run. These tests fake that state and check that
mireasy then uses the certifi bundle, and that it changes nothing otherwise.
Offline and fast.
"""
import os
import ssl
import subprocess
import sys

import certifi
import pytest

from mireasy import certs

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_NAMES = ("SSL_CERT_FILE", "SSL_CERT_DIR")


def _paths(cafile=None, capath=None):
    return ssl.DefaultVerifyPaths(cafile, capath, "SSL_CERT_FILE", "/nowhere/cert.pem",
                                  "SSL_CERT_DIR", "/nowhere/certs")


@pytest.fixture
def no_cert_env(monkeypatch):
    # setenv first, so that monkeypatch records the real state and restores it
    # after the test even though the code under test writes to os.environ.
    for name in ENV_NAMES:
        monkeypatch.setenv(name, "")
        monkeypatch.delenv(name)


@pytest.fixture
def python_without_certificates(no_cert_env, monkeypatch):
    monkeypatch.setattr(ssl, "get_default_verify_paths", lambda: _paths())


def test_python_without_certificates_gets_the_certifi_bundle(python_without_certificates):
    assert certs.ensure_certificates() is True
    assert os.environ["SSL_CERT_FILE"] == certifi.where()
    assert os.path.isfile(os.environ["SSL_CERT_FILE"])


def test_python_then_reads_its_certificates_from_that_bundle(
        python_without_certificates, monkeypatch, tmp_path):
    # A bundle with one certificate, so the count shows where Python read from.
    end = "-----END CERTIFICATE-----"
    one = tmp_path / "one.pem"
    one.write_text(certifi.contents().split(end)[0] + end + "\n", encoding="ascii")
    monkeypatch.setattr(certifi, "where", lambda: str(one))

    assert certs.ensure_certificates() is True
    assert ssl.create_default_context().cert_store_stats()["x509"] == 1


def test_python_with_a_certificate_file_is_left_alone(no_cert_env, monkeypatch, tmp_path):
    bundle = tmp_path / "cert.pem"
    bundle.write_text("x")
    monkeypatch.setattr(ssl, "get_default_verify_paths", lambda: _paths(cafile=str(bundle)))
    assert certs.ensure_certificates() is False
    assert "SSL_CERT_FILE" not in os.environ


def test_python_with_a_certificate_folder_is_left_alone(no_cert_env, monkeypatch, tmp_path):
    (tmp_path / "ab12cd34.0").write_text("x")
    monkeypatch.setattr(ssl, "get_default_verify_paths", lambda: _paths(capath=str(tmp_path)))
    assert certs.ensure_certificates() is False
    assert "SSL_CERT_FILE" not in os.environ


def test_an_empty_certificate_folder_counts_as_no_certificates(no_cert_env, monkeypatch, tmp_path):
    monkeypatch.setattr(ssl, "get_default_verify_paths", lambda: _paths(capath=str(tmp_path)))
    assert certs.ensure_certificates() is True
    assert os.environ["SSL_CERT_FILE"] == certifi.where()


def test_a_certificate_folder_that_cannot_be_read_counts_as_no_certificates(
        no_cert_env, monkeypatch, tmp_path):
    def refuse(path):
        raise PermissionError(path)

    monkeypatch.setattr(ssl, "get_default_verify_paths", lambda: _paths(capath=str(tmp_path)))
    monkeypatch.setattr(os, "listdir", refuse)
    assert certs.ensure_certificates() is True
    assert os.environ["SSL_CERT_FILE"] == certifi.where()


@pytest.mark.parametrize("name", ENV_NAMES)
def test_a_certificate_setting_of_the_user_is_respected(python_without_certificates,
                                                        monkeypatch, name):
    monkeypatch.setenv(name, "/my/own/certificates")
    assert certs.ensure_certificates() is False
    assert os.environ[name] == "/my/own/certificates"
    assert [n for n in ENV_NAMES if n in os.environ] == [name]


def test_without_certifi_nothing_changes_and_nothing_breaks(python_without_certificates,
                                                            monkeypatch):
    monkeypatch.setitem(sys.modules, "certifi", None)      # makes `import certifi` fail
    assert certs.ensure_certificates() is False
    assert "SSL_CERT_FILE" not in os.environ


def test_importing_mireasy_applies_it():
    # Every download starts with `import mireasy`: the model downloader, and the
    # BEAT THIS! and Demucs models that are fetched at the first analysis.
    code = ("import ssl\n"
            "ssl.get_default_verify_paths = lambda: ssl.DefaultVerifyPaths(\n"
            "    None, None, 'SSL_CERT_FILE', '/nowhere/cert.pem', 'SSL_CERT_DIR', '/nowhere/certs')\n"
            "import os, mireasy\n"
            "print(os.environ.get('SSL_CERT_FILE', 'not set'))\n")
    env = {k: v for k, v in os.environ.items() if k not in ENV_NAMES}
    r = subprocess.run([sys.executable, "-c", code], cwd=REPO, env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == certifi.where()
