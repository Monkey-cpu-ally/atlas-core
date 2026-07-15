import pytest

from atlas_core_runtime.service_registry import ServiceRegistry


class HealthyService:
    def health(self) -> dict[str, object]:
        return {"status": "healthy", "jobs": 2}


class BrokenHealthService:
    def health(self) -> dict[str, object]:
        raise RuntimeError("health check failed")


def test_register_and_get_service() -> None:
    registry = ServiceRegistry()
    service = object()

    registry.register("Learning", service, version="1.0.0")

    assert registry.get("learning") is service
    assert registry.entry("LEARNING").version == "1.0.0"
    assert registry.names() == ("learning",)


def test_duplicate_requires_explicit_replacement() -> None:
    registry = ServiceRegistry()
    registry.register("knowledge", object())

    with pytest.raises(KeyError, match="already registered"):
        registry.register("knowledge", object())

    replacement = object()
    registry.register("knowledge", replacement, replace=True)
    assert registry.get("knowledge") is replacement


def test_nonreplaceable_service_is_protected() -> None:
    registry = ServiceRegistry()
    registry.register("security", object(), replaceable=False)

    with pytest.raises(PermissionError, match="not replaceable"):
        registry.register("security", object(), replace=True)


def test_health_snapshot_isolates_failures() -> None:
    registry = ServiceRegistry()
    registry.register("learning", HealthyService(), version="1.2.0")
    registry.register("broken", BrokenHealthService())
    registry.register("plain", object())

    snapshot = registry.health_snapshot()

    assert snapshot["learning"] == {"status": "healthy", "jobs": 2, "version": "1.2.0"}
    assert snapshot["broken"]["status"] == "unhealthy"
    assert "health check failed" in str(snapshot["broken"]["error"])
    assert snapshot["plain"]["status"] == "unknown"
