from atlas_events.event_bus import AtlasEvent, EventBus


def test_publish_delivers_event_and_wildcard() -> None:
    bus = EventBus()
    received: list[tuple[str, str]] = []

    bus.subscribe("SOURCE_IMPORTED", lambda event: received.append(("specific", event.event_id)))
    bus.subscribe("*", lambda event: received.append(("wildcard", event.event_id)))

    event = AtlasEvent("SOURCE_IMPORTED", {"source_id": "SRC-1"}, source="learning")
    failures = bus.publish(event)

    assert failures == []
    assert received == [("specific", event.event_id), ("wildcard", event.event_id)]


def test_failing_handler_does_not_block_others() -> None:
    bus = EventBus()
    received: list[str] = []

    def fail(_: AtlasEvent) -> None:
        raise RuntimeError("subscriber broke")

    bus.subscribe("GRAPH_UPDATED", fail)
    bus.subscribe("GRAPH_UPDATED", lambda event: received.append(event.event_type))

    failures = bus.publish(AtlasEvent("GRAPH_UPDATED"))

    assert received == ["GRAPH_UPDATED"]
    assert len(failures) == 1
    assert isinstance(failures[0], RuntimeError)


def test_unsubscribe_removes_handler() -> None:
    bus = EventBus()
    received: list[str] = []
    unsubscribe = bus.subscribe("TEST", lambda event: received.append(event.event_type))

    unsubscribe()
    bus.publish(AtlasEvent("TEST"))

    assert received == []
    assert bus.subscriber_count("TEST") == 0
