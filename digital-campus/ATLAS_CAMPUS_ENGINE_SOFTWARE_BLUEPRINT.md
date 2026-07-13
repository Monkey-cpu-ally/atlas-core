# ATLAS Campus Engine — Software Blueprint

## Mission

The Campus Engine turns the ATLAS Digital Engineering Campus into a navigable, data-driven AtlasOS interface. Buildings, laboratories, rooms, projects, Digital Twins, documents, simulations, and AI workspaces are represented as functional software objects rather than decorative scenes.

## 1. Product Goal

A user should be able to:

- Open the Digital Campus.
- Enter institutes and laboratories.
- View active projects and status.
- Open engineering documents.
- Inspect Digital Twins.
- Launch approved simulations.
- Talk with Hermes, Minerva, Ajani, or the Council in the correct workspace.
- Review tests, risks, decisions, and recent changes.
- Move from a visual room to the underlying engineering data without losing context.

## 2. Design Principle

The Campus is a visual navigation layer over real AtlasOS records.

A building is not merely a 3D model. It is a view of an institute.

A laboratory is not merely a room. It is a filtered workspace containing projects, assets, people or AIs, simulations, documents, alerts, and tools.

A machine is not merely an object. It links to a Digital Twin.

## 3. Core Domain Models

### Campus

- Campus ID
- Name
- Version
- Theme
- Health state
- Buildings
- Global navigation
- Active alerts

### Building

- Building ID
- Name
- Owning institute
- Primary AI
- Permanent color
- Purpose
- Departments
- Rooms
- Projects
- Health and activity summary

### Room

- Room ID
- Building ID
- Room type
- Name
- Purpose
- Access level
- Tools
- Linked projects
- Linked Digital Twins
- Linked documents
- Active sessions

### Campus Asset

- Asset ID
- Asset type
- Digital Twin ID
- Location
- Status
- Owner
- Version
- Interaction actions

### Workspace Session

- Session ID
- User
- AI participant
- Room
- Project context
- Open records
- Active tools
- Start time
- Audit events

## 4. Permanent AI Environments

### Hermes — Off-White

Default spaces:

- Robotics Institute
- Weaver Laboratory
- Manufacturing Center
- Electronics and PCB Laboratory
- Simulation Center
- Digital Twin Center

### Minerva — Nature Green

Default spaces:

- Biology Institute
- Chemistry Institute
- Biomedical Laboratory
- Environmental Research Center
- Materials Discovery Center
- Discovery Garden

### Ajani — Crimson Red

Default spaces:

- Architecture Studio
- Mission Command
- Strategic War Room
- Battlefield Simulation Grounds
- Hunter's Preserve
- Logistics Center
- World Simulator

### Council — Royal Purple

Default spaces:

- Council Chamber
- Review Board
- Ethics and Risk Review
- Major Decision Archive

## 5. Navigation Layers

The engine should support three levels:

1. **Campus Map:** Buildings, alerts, institute activity, mission state.
2. **Building View:** Departments, rooms, projects, assets, responsible AI.
3. **Workspace View:** Real documents, APIs, Digital Twins, tasks, simulations, and reports.

Users must always have a direct route back to search, projects, and the Executive Dashboard.

## 6. Functional Room Types

- AI Workspace
- Project Room
- Research Laboratory
- Engineering Laboratory
- Simulation Chamber
- Digital Twin Bay
- Manufacturing Cell
- Review Chamber
- Library
- Archive
- Mission Room
- Testing Facility
- Founder Workspace

Each room type defines available widgets, permissions, data queries, and actions.

## 7. Campus Services

Recommended services:

- Campus Registry Service
- Building and Room Service
- Navigation Service
- Workspace Context Service
- Campus Search Service
- Project Link Service
- Digital Twin Link Service
- Knowledge Bank Link Service
- AI Presence Service
- Notification and Alert Service
- Access Control Service
- Campus Audit Service

## 8. API Contract

Suggested endpoints:

- `GET /api/campus/health`
- `GET /api/campus`
- `GET /api/campus/buildings`
- `GET /api/campus/buildings/{building_id}`
- `GET /api/campus/rooms/{room_id}`
- `GET /api/campus/assets/{asset_id}`
- `GET /api/campus/search`
- `POST /api/campus/sessions`
- `GET /api/campus/sessions/{session_id}`
- `POST /api/campus/sessions/{session_id}/context`
- `POST /api/campus/navigation`
- `GET /api/campus/alerts`

## 9. Data Integration

The Campus Engine reads from:

- Knowledge Bank
- Project Manager
- Digital Twin Engine
- Research Engine
- Simulation services
- Robotics and manufacturing services
- GitHub integration
- CI and test status
- AI orchestrator
- Notification system

It should not duplicate source data when a governed service already owns it.

## 10. Visual State

Visuals should communicate real state:

- Healthy and active
- Idle
- Under review
- Degraded
- Blocked
- Faulted
- Maintenance
- Restricted

Decorative animations must never hide warnings or imply false progress.

## 11. Campus Search

Search should find:

- Buildings
- Rooms
- AIs
- Projects
- Digital Twins
- Documents
- Tests
- Failures
- Tools
- Materials
- Components
- Missions

Results should show both the digital location and the authoritative underlying record.

## 12. Interaction Model

Selecting an asset may provide:

- Open Digital Twin
- View documentation
- View project
- Run approved simulation
- View test history
- View maintenance
- Ask assigned AI
- Create task
- Report issue

Available actions depend on permissions and asset state.

## 13. Security and Access

The engine must enforce:

- Authentication
- Role-based permissions
- Protected Founder and family spaces
- Restricted research and business records
- Safe handling of credentials
- Audit logging
- Read-only modes
- Approval requirements for consequential actions

Entering a virtual room does not automatically authorize every action associated with it.

## 14. Initial Release Scope

Version 0.1 should include:

- Campus registry
- Four AI headquarters
- Executive Headquarters
- Robotics Institute
- Minerva Scientific Complex
- Ajani Strategic Complex
- Council Chamber
- Knowledge Library
- Project links
- Digital Twin links
- Search
- Health and alert states
- Simple 2D or lightweight 2.5D navigation

Full 3D rendering is not required for the first functional release.

## 15. Development Phases

### Phase A — Data Foundation

Create campus, building, room, asset, and session models.

### Phase B — API

Build read-only campus navigation and search endpoints.

### Phase C — AtlasOS Interface

Create campus map, building pages, room workspaces, and AI presence panels.

### Phase D — Live Integrations

Connect projects, Knowledge Bank, Digital Twins, GitHub status, and CI.

### Phase E — Simulation and Action

Add approved simulation launch, task creation, reviews, and controlled operations.

### Phase F — Immersive Presentation

Add richer 2.5D or 3D environments after the functional system is stable.

## 16. Testing Requirements

- Every building resolves to a valid institute.
- Every room has a valid owner and purpose.
- Permanent AI colors remain correct.
- Broken document or twin links are detected.
- Unauthorized room actions are blocked.
- Search distinguishes drafts from validated records.
- Campus health reflects actual service state.
- Navigation preserves project context.
- API tests run without paid external services.

## 17. Definition of Done

The Campus Engine is not complete because the map looks impressive.

It is complete when a user can navigate from the campus to a real engineering project, inspect its authoritative knowledge and Digital Twin, work with the correct AI, review evidence, and return with context preserved.

## Campus Engine Rules

- **CE-1:** Function before spectacle.
- **CE-2:** Visual state must reflect real system state.
- **CE-3:** Do not duplicate authoritative data.
- **CE-4:** Every room exists for a real workflow.
- **CE-5:** Begin with 2D or 2.5D navigation; earn full 3D through stability.
