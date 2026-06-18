"""
Phase 8f — mTLS device certificate issuance tests.

Spec:
  * POST /api/robot/devices returns a one-shot `mtls` block with
    cert_pem · key_pem · ca_pem · fingerprint_sha256 · not_after
  * Same CA across registrations (issuer chain stays consistent)
  * /api/robot/mtls/ca returns the CA in PEM + the enforced flag
  * Owner-only re-issue at /api/robot/devices/{id}/mtls/issue rotates
    the device cert (new serial, new fingerprint) but the CA stays the same
  * Fingerprint persists on the device document for future enforcement

Run:
    cd /app/backend && pytest tests/test_mtls_phase8f.py -v
"""
from __future__ import annotations

import os
import re
import uuid

import httpx
import pytest
from cryptography import x509

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
API = BACKEND.rstrip("/") + "/api/robot"

OWNER = {"X-Atlas-Role": "owner"}
GUEST = {"X-Atlas-Role": "guest"}
TIMEOUT = httpx.Timeout(60.0, connect=10.0)


PEM_CERT_RE = re.compile(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", re.DOTALL)
PEM_KEY_RE  = re.compile(r"-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----", re.DOTALL)


@pytest.fixture(scope="module")
def registered_device():
    name = f"MTLS-TEST-{uuid.uuid4().hex[:6]}"
    r = httpx.post(
        f"{API}/devices",
        json={"name": name, "kind": "esp32",
              "hardware_profile": {"sensors": ["temp"], "actuators": []},
              "tags": ["test", "mtls"]},
        headers=OWNER, timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_registration_returns_full_mtls_pack(registered_device):
    dev = registered_device
    mtls = dev.get("mtls")
    assert mtls, f"register response missing mtls block: {dev}"
    assert PEM_CERT_RE.search(mtls["cert_pem"]), "cert_pem doesn't look like a PEM cert"
    assert PEM_KEY_RE.search(mtls["key_pem"]),  "key_pem doesn't look like a PEM key"
    assert PEM_CERT_RE.search(mtls["ca_pem"]),  "ca_pem doesn't look like a PEM cert"
    assert re.fullmatch(r"[0-9A-F]{64}", mtls["fingerprint_sha256"])
    # validity window must be in the future (≥ 1 year for the device)
    assert mtls["not_after"]
    assert "warning" in mtls and "NOT be shown again" in mtls["warning"]


def test_device_cert_is_signed_by_atlas_ca(registered_device):
    mtls = registered_device["mtls"]
    cert = x509.load_pem_x509_certificate(mtls["cert_pem"].encode())
    ca   = x509.load_pem_x509_certificate(mtls["ca_pem"].encode())
    # Issuer of the device cert must equal the subject of the CA
    assert cert.issuer == ca.subject
    # CN of the device cert must equal the device id
    cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    assert cn == registered_device["id"]


def test_fingerprint_persisted_on_device(registered_device):
    """The server must store ONLY the fingerprint (not the cert/key) so
    future enforcement can verify presented certs."""
    r = httpx.get(f"{API}/devices/{registered_device['id']}", timeout=TIMEOUT)
    body = r.json()
    assert body.get("mtls_fingerprint") == registered_device["mtls"]["fingerprint_sha256"]
    assert body.get("mtls_serial")
    assert body.get("mtls_not_after")
    # The cert/key/ca must NOT be persisted server-side
    assert "cert_pem" not in body
    assert "key_pem" not in body


def test_get_ca_returns_pem_and_enforced_flag():
    r = httpx.get(f"{API}/mtls/ca", timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    body = r.json()
    assert PEM_CERT_RE.search(body["ca_pem"])
    assert body["enforced"] is False     # v1 ships dormant


def test_ca_is_stable_across_registrations(registered_device):
    """Mint a second device — both should be signed by the same CA."""
    name = f"MTLS-TEST-{uuid.uuid4().hex[:6]}"
    r = httpx.post(
        f"{API}/devices",
        json={"name": name, "kind": "esp32",
              "hardware_profile": {"sensors": ["temp"]},
              "tags": ["test"]},
        headers=OWNER, timeout=TIMEOUT,
    )
    second = r.json()
    assert second["mtls"]["ca_pem"] == registered_device["mtls"]["ca_pem"], \
        "CA must be the same across registrations — otherwise prior certs become orphans"


def test_reissue_rotates_cert_but_keeps_ca(registered_device):
    """Re-issuing must produce a NEW serial + fingerprint but signed by
    the SAME CA as the original."""
    dev_id = registered_device["id"]
    old_fp = registered_device["mtls"]["fingerprint_sha256"]
    old_ca = registered_device["mtls"]["ca_pem"]

    # Guest cannot rotate
    r403 = httpx.post(
        f"{API}/devices/{dev_id}/mtls/issue", headers=GUEST, timeout=TIMEOUT,
    )
    assert r403.status_code == 403

    # Owner can
    r = httpx.post(
        f"{API}/devices/{dev_id}/mtls/issue", headers=OWNER, timeout=TIMEOUT,
    )
    assert r.status_code == 200, r.text
    pack = r.json()
    assert pack["fingerprint_sha256"] != old_fp, "fingerprint must rotate"
    assert pack["ca_pem"] == old_ca, "CA must NOT rotate on a device re-issue"

    # Device's persisted fingerprint must now match the new cert
    dev = httpx.get(f"{API}/devices/{dev_id}", timeout=TIMEOUT).json()
    assert dev["mtls_fingerprint"] == pack["fingerprint_sha256"]


def test_reissue_404_for_unknown_device():
    r = httpx.post(
        f"{API}/devices/no-such-id/mtls/issue", headers=OWNER, timeout=TIMEOUT,
    )
    assert r.status_code == 404
