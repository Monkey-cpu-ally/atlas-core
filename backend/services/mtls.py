"""
mTLS device certificate issuance — Phase 8f.

v1 contract:
  * On `POST /api/robot/devices`, after persisting the device, mint a
    fresh ECDSA P-256 key + a per-device certificate signed by a local
    self-signed CA. Return the (cert PEM, key PEM, ca PEM) in the
    response ONCE — never stored on the server.
  * The CA's private key IS stored on disk under
    /app/backend/_data/mtls/  (or MTLS_CA_DIR if set) so subsequent
    registrations are signed by the same authority.
  * Enforcement: dormant by default. Set MTLS_ENFORCE=true to make
    /telemetry and /commands/inbox endpoints reject requests that don't
    present a client cert with a CN matching the device-id. (v1 ships
    the enforcement decorator but it's GATED on the env var so existing
    HTTP-poll tests keep passing.)

Why ECDSA P-256?
  - Tiny keys (256 bits) fit in ESP32 flash / NVS comfortably.
  - mbedtls (ESP-IDF default) supports it out of the box.

CA persistence:
  /<MTLS_CA_DIR>/ca.key.pem   (mode 0600)
  /<MTLS_CA_DIR>/ca.cert.pem

Public API:
  ensure_ca()          — idempotent first-run CA mint
  issue_device_cert(device_id, name) → {cert, key, ca, fingerprint}
  get_ca_pem()         — for the device-side trust store
"""
from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import Dict

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID


_DEFAULT_DIR = Path(os.environ.get("MTLS_CA_DIR", "/app/backend/_data/mtls"))
_CA_CERT_PATH = _DEFAULT_DIR / "ca.cert.pem"
_CA_KEY_PATH  = _DEFAULT_DIR / "ca.key.pem"

_CA_VALIDITY_YEARS    = 10
_DEVICE_VALIDITY_YEARS = 2


def is_enforced() -> bool:
    """When True, the /telemetry and /commands/inbox endpoints will reject
    requests that don't present a verified client cert. v1 default = OFF."""
    return os.environ.get("MTLS_ENFORCE", "").lower() in ("1", "true", "yes")


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def ensure_ca() -> tuple[x509.Certificate, ec.EllipticCurvePrivateKey]:
    """First-run: mint a long-lived self-signed CA. Subsequent calls load
    it from disk. CA private key is mode 0600 — never returned over the
    wire."""
    _DEFAULT_DIR.mkdir(parents=True, exist_ok=True)
    if _CA_CERT_PATH.exists() and _CA_KEY_PATH.exists():
        ca_cert = x509.load_pem_x509_certificate(_CA_CERT_PATH.read_bytes())
        ca_key = serialization.load_pem_private_key(_CA_KEY_PATH.read_bytes(), password=None)
        return ca_cert, ca_key  # type: ignore[return-value]

    # Mint fresh CA
    ca_key = ec.generate_private_key(ec.SECP256R1())
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "ATLAS Root CA"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ATLAS"),
    ])
    now = _now()
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=365 * _CA_VALIDITY_YEARS))
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, content_commitment=False, key_encipherment=False,
                data_encipherment=False, key_agreement=False, key_cert_sign=True,
                crl_sign=True, encipher_only=False, decipher_only=False,
            ),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    _CA_CERT_PATH.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    _CA_KEY_PATH.write_bytes(ca_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    os.chmod(_CA_KEY_PATH, 0o600)
    return ca_cert, ca_key


def get_ca_pem() -> str:
    ca_cert, _ = ensure_ca()
    return ca_cert.public_bytes(serialization.Encoding.PEM).decode("ascii")


def issue_device_cert(device_id: str, device_name: str) -> Dict[str, str]:
    """Mint a fresh keypair + cert for one device. Returns PEM strings
    PLUS the SHA-256 fingerprint of the cert (so the registry can store
    just the fingerprint while the device keeps the key)."""
    ca_cert, ca_key = ensure_ca()
    dev_key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, device_id),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ATLAS Device"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, device_name[:64]),
    ])
    now = _now()
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(dev_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=365 * _DEVICE_VALIDITY_YEARS))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, content_commitment=False, key_encipherment=True,
                data_encipherment=False, key_agreement=False, key_cert_sign=False,
                crl_sign=False, encipher_only=False, decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False,
        )
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(device_id)]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return {
        "device_id": device_id,
        "cert_pem": cert.public_bytes(serialization.Encoding.PEM).decode("ascii"),
        "key_pem": dev_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("ascii"),
        "ca_pem": get_ca_pem(),
        "fingerprint_sha256": cert.fingerprint(hashes.SHA256()).hex().upper(),
        "not_after": cert.not_valid_after_utc.isoformat() if hasattr(cert, "not_valid_after_utc")
                      else cert.not_valid_after.isoformat(),  # py<3.13 compat
        "serial_number": format(cert.serial_number, "x").upper(),
    }
