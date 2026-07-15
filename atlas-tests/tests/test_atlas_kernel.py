from atlas_core_runtime.kernel import AtlasKernel


class ExampleService:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def health(self) -> dict[str, str]:
        return {"status": "healthy" if self.started and not self.stopped else "idle"}


def test_kernel_starts_services_and_emits_events() -> None:
    kernel = AtlasKernel()
    service = ExampleService()
    events: list[str] = []
    kernel.events.subscribe("*", lambda event: events.append(event.event_type))

    kernel.register_service("example", service)
    kernel.start()

    assert service.started is True
    assert kernel.state == "running"
    assert "SERVICE_REGISTERED" in events
    assert "KERNEL_STARTED" in events
    assert kernel.health()["status"] == "healthy"


def test_kernel_stop_is_idempotent_and_stops_services() -> None:
    kernel = AtlasKernel()
    service = ExampleService()
    kernel.register_service("example", service)
    kernel.start()

    kernel.stop()
    kernel.stop()

    assert service.stopped is True
    assert kernel.state == "stopped"
    assert kernel.status().stopped_at is not None


def test_kernel_registers_event_bus_as_protected_service() -> None:
    kernel = AtlasKernel()

    assert kernel.services.get("event_bus") is kernel.events

    try:
        kernel.register_service("event_bus", object(), replace=True)
    except PermissionError:
        pass
    else:
        raise AssertionError("event_bus must not be replaceable")
