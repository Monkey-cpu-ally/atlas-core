import pytest

from services import service_health_registry as registry


@pytest.fixture(autouse=True)
def clear_test_probes():
    original = dict(registry._PROBES)
    registry._PROBES.clear()
    yield
    registry._PROBES.clear()
    registry._PROBES.update(original)


@pytest.mark.asyncio
async def test_registry_reports_unknown_without_probe():
    result = await registry.service_health("campus-service")
    assert result is not None
    assert result["state"] == "unknown"


@pytest.mark.asyncio
async def test_registered_healthy_probe():
    registry.register_probe("campus-service", lambda: {"status": "healthy", "summary": "Campus ready"})
    result = await registry.service_health("campus-service")
    assert result["state"] == "healthy"
    assert result["summary"] == "Campus ready"


@pytest.mark.asyncio
async def test_failing_probe_is_offline_not_exception():
    def broken():
        raise RuntimeError("boom")

    registry.register_probe("campus-service", broken)
    result = await registry.service_health("campus-service")
    assert result["state"] == "offline"
    assert result["details"]["error"] == "RuntimeError"


@pytest.mark.asyncio
async def test_executive_summary_never_claims_healthy_for_unknown_required_services():
    registry.register_probe("campus-service", lambda: {"status": "healthy"})
    summary = await registry.executive_summary()
    assert summary["status"] == "degraded"
    assert "knowledge-service" in summary["v1_uncertain"]


def test_unknown_service_rejected_on_probe_registration():
    with pytest.raises(KeyError):
        registry.register_probe("imaginary-service", lambda: {"status": "healthy"})
