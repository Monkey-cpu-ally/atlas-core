"""ATLAS Digital Campus registry and read-only domain service.

This module turns the approved Digital Campus blueprint into executable data.
It intentionally starts as a deterministic registry so the frontend and tests
have a stable contract before MongoDB persistence and immersive rendering are
added.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class CampusRoom:
    id: str
    building_id: str
    name: str
    room_type: str
    purpose: str
    access_level: str = "standard"
    linked_services: tuple[str, ...] = ()


@dataclass(frozen=True)
class CampusBuilding:
    id: str
    name: str
    institute: str
    primary_ai: str
    color_standard: str
    purpose: str
    rooms: tuple[CampusRoom, ...] = field(default_factory=tuple)


AI_STANDARDS = {
    "hermes": {"display_name": "Hermes", "color": "off-white"},
    "minerva": {"display_name": "Minerva", "color": "nature-green"},
    "ajani": {"display_name": "Ajani", "color": "crimson-red"},
    "council": {"display_name": "Council", "color": "royal-purple"},
}


def _room(
    room_id: str,
    building_id: str,
    name: str,
    room_type: str,
    purpose: str,
    *linked_services: str,
    access_level: str = "standard",
) -> CampusRoom:
    return CampusRoom(
        id=room_id,
        building_id=building_id,
        name=name,
        room_type=room_type,
        purpose=purpose,
        access_level=access_level,
        linked_services=tuple(linked_services),
    )


BUILDINGS: tuple[CampusBuilding, ...] = (
    CampusBuilding(
        id="executive-headquarters",
        name="Executive Headquarters",
        institute="Executive Command Center",
        primary_ai="council",
        color_standard=AI_STANDARDS["council"]["color"],
        purpose="Coordinate ATLAS missions, projects, system health, and Founder reviews.",
        rooms=(
            _room("executive-dashboard", "executive-headquarters", "Executive Dashboard", "command", "Display organization health, alerts, projects, and milestones.", "project-service", "audit-service", "notification-service"),
            _room("founder-office", "executive-headquarters", "Founder Office", "founder-workspace", "Provide protected access to the roadmap, journals, legacy archive, and approvals.", "project-service", "knowledge-service", access_level="founder"),
            _room("central-plaza", "executive-headquarters", "Central Plaza and ATLAS Core", "navigation", "Serve as the central campus navigation and system-status surface.", "campus-service", "ai-orchestrator"),
        ),
    ),
    CampusBuilding(
        id="hermes-engineering-complex",
        name="Hermes Engineering Complex",
        institute="Engineering Institute",
        primary_ai="hermes",
        color_standard=AI_STANDARDS["hermes"]["color"],
        purpose="Design, simulate, manufacture, test, and maintain ATLAS technology.",
        rooms=(
            _room("robotics-institute", "hermes-engineering-complex", "Robotics Institute", "engineering-laboratory", "Coordinate robotics architecture and subsystem work.", "engineering-service", "digital-twin-service"),
            _room("weaver-laboratory", "hermes-engineering-complex", "Weaver Laboratory", "engineering-laboratory", "Develop and validate the Weaver robotic platform.", "engineering-service", "simulation-service", "digital-twin-service"),
            _room("electronics-pcb-lab", "hermes-engineering-complex", "Electronics and PCB Laboratory", "engineering-laboratory", "Develop embedded electronics, power systems, and PCB designs.", "engineering-service", "knowledge-service"),
            _room("manufacturing-center", "hermes-engineering-complex", "Manufacturing Center", "manufacturing-cell", "Plan workcells, tooling, quality, and production systems.", "manufacturing-service", "digital-twin-service"),
            _room("simulation-center", "hermes-engineering-complex", "Simulation Center", "simulation-chamber", "Run approved engineering and robotics simulations.", "simulation-service", "digital-twin-service"),
        ),
    ),
    CampusBuilding(
        id="minerva-scientific-complex",
        name="Minerva Scientific Research Complex",
        institute="Research Institute",
        primary_ai="minerva",
        color_standard=AI_STANDARDS["minerva"]["color"],
        purpose="Discover, test, and preserve scientific knowledge for ATLAS projects.",
        rooms=(
            _room("biology-institute", "minerva-scientific-complex", "Biology Institute", "research-laboratory", "Study biological systems, ecology, genetics, and regenerative science.", "research-service", "knowledge-service"),
            _room("chemistry-institute", "minerva-scientific-complex", "Chemistry Institute", "research-laboratory", "Study chemistry, electrochemistry, polymers, and industrial processes.", "research-service", "knowledge-service"),
            _room("materials-discovery-center", "minerva-scientific-complex", "Materials Discovery Center", "research-laboratory", "Evaluate metals, ceramics, composites, biomaterials, coatings, and smart materials.", "research-service", "engineering-service"),
            _room("environmental-research-center", "minerva-scientific-complex", "Environmental Research Center", "research-laboratory", "Study restoration, water, air, soil, ecosystems, and sustainable engineering.", "research-service", "simulation-service"),
            _room("discovery-garden", "minerva-scientific-complex", "Discovery Garden", "living-library", "Model plant libraries, ecosystems, agriculture, and Green Robot restoration research.", "research-service", "digital-twin-service"),
        ),
    ),
    CampusBuilding(
        id="ajani-strategic-command",
        name="Ajani Strategic Command Complex",
        institute="Operations Institute",
        primary_ai="ajani",
        color_standard=AI_STANDARDS["ajani"]["color"],
        purpose="Plan missions, architecture, logistics, resources, risks, and contingencies.",
        rooms=(
            _room("architecture-studio", "ajani-strategic-command", "Architecture Studio", "design-studio", "Develop campus, factory, city, infrastructure, and facility plans.", "strategy-service", "engineering-service"),
            _room("mission-command", "ajani-strategic-command", "Mission Command Center", "command", "Track priorities, schedules, dependencies, resources, and risks.", "strategy-service", "project-service"),
            _room("strategic-war-room", "ajani-strategic-command", "Strategic War Room", "review-chamber", "Run scenario, logistics, recovery, budget, and supply-chain analysis.", "strategy-service", "simulation-service"),
            _room("battlefield-simulation", "ajani-strategic-command", "Battlefield Simulation Grounds", "simulation-chamber", "Train disaster response, rescue, terrain navigation, and multi-robot coordination in a controlled virtual environment.", "simulation-service", "robotics-fleet-service"),
            _room("hunters-preserve", "ajani-strategic-command", "Hunter's Preserve", "simulation-chamber", "Develop observation, tracking, route planning, hazard avoidance, and energy management without harming wildlife.", "simulation-service"),
            _room("logistics-center", "ajani-strategic-command", "Logistics Center", "operations", "Track materials, fleets, suppliers, inventories, energy, schedules, and maintenance resources.", "strategy-service", "manufacturing-service"),
        ),
    ),
    CampusBuilding(
        id="council-chamber",
        name="Council Chamber",
        institute="ATLAS Council",
        primary_ai="council",
        color_standard=AI_STANDARDS["council"]["color"],
        purpose="Conduct cross-disciplinary review, ethics review, conflict resolution, and advancement approval.",
        rooms=(
            _room("council-review-board", "council-chamber", "Council Review Board", "review-chamber", "Review evidence, disagreements, risks, and major decisions.", "ai-orchestrator", "audit-service"),
            _room("major-decision-archive", "council-chamber", "Major Decision Archive", "archive", "Preserve approved decisions, dissents, evidence, and revision history.", "knowledge-service", "audit-service"),
        ),
    ),
    CampusBuilding(
        id="hall-of-knowledge",
        name="Engineering Library and Hall of Knowledge",
        institute="Knowledge Bank",
        primary_ai="council",
        color_standard=AI_STANDARDS["council"]["color"],
        purpose="Provide governed access to Bibles, standards, records, tests, and lessons learned.",
        rooms=(
            _room("world-tree", "hall-of-knowledge", "World Tree", "knowledge-navigation", "Visualize disciplines, institutes, projects, and validated knowledge relationships.", "knowledge-service", "knowledge-graph-service"),
            _room("knowledge-vault", "hall-of-knowledge", "Knowledge Vault", "archive", "Preserve versioned documents, code, designs, experiments, and decisions.", "knowledge-service", "audit-service", access_level="restricted"),
        ),
    ),
)


def list_buildings() -> list[dict]:
    return [asdict(building) for building in BUILDINGS]


def get_building(building_id: str) -> dict | None:
    return next((asdict(item) for item in BUILDINGS if item.id == building_id), None)


def iter_rooms() -> Iterable[CampusRoom]:
    for building in BUILDINGS:
        yield from building.rooms


def get_room(room_id: str) -> dict | None:
    return next((asdict(item) for item in iter_rooms() if item.id == room_id), None)


def search_campus(query: str) -> list[dict]:
    normalized = query.strip().casefold()
    if not normalized:
        return []

    results: list[dict] = []
    for building in BUILDINGS:
        building_text = " ".join((building.name, building.institute, building.purpose, building.primary_ai)).casefold()
        if normalized in building_text:
            results.append({"kind": "building", **asdict(building)})

        for room in building.rooms:
            room_text = " ".join((room.name, room.room_type, room.purpose, " ".join(room.linked_services))).casefold()
            if normalized in room_text:
                results.append({"kind": "room", **asdict(room)})
    return results


def campus_health() -> dict:
    rooms = list(iter_rooms())
    integrity_errors: list[str] = []

    building_ids = {item.id for item in BUILDINGS}
    for room in rooms:
        if room.building_id not in building_ids:
            integrity_errors.append(f"Room {room.id} references missing building {room.building_id}")

    for building in BUILDINGS:
        expected_color = AI_STANDARDS[building.primary_ai]["color"]
        if building.color_standard != expected_color:
            integrity_errors.append(
                f"Building {building.id} violates {building.primary_ai} color standard"
            )

    return {
        "status": "healthy" if not integrity_errors else "degraded",
        "version": "0.1.0",
        "buildings": len(BUILDINGS),
        "rooms": len(rooms),
        "ai_standards": AI_STANDARDS,
        "integrity_errors": integrity_errors,
    }
