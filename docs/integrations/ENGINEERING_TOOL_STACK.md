# ATLAS Engineering Tool Stack

This branch adds local adapters for OpenCV, CadQuery, and KiCad.

## OpenCV

Capability: `inspect_image`

Purpose: safely decode an image and return width, height, channel count, and data type without changing the source file.

Dependency: `opencv-python-headless`

## CadQuery

Capability: `generate_box`

Purpose: generate a basic parametric solid and export both STEP and STL files. This is the first working CAD primitive for Hermes and is intentionally narrow.

Dependency: `cadquery`

Default output: `artifacts/cad/`

## KiCad

Capabilities:

- `version`
- `validate_schematic`
- `validate_pcb`

Purpose: detect a locally installed `kicad-cli`, run schematic ERC, run PCB DRC, and save JSON reports.

KiCad itself is not installed by pip. Install KiCad on the host operating system and ensure `kicad-cli` is available on `PATH`.

Default report output: `artifacts/kicad/`

## Safety

All adapters are disabled by default at the Tool Bus policy layer. OpenCV and KiCad validation are read-only. CadQuery writes generated artifacts locally and therefore requires local-write approval.

## Development stack

The repository root also contains a Dockerfile and `docker-compose.yml` for ATLAS, MongoDB, and Qdrant. Ollama remains a host service by default and is reached at `host.docker.internal:11434`.

## Validation

Run:

```bash
cd backend
pytest tests/test_engineering_tool_adapters.py -v
```

Passing contract tests prove registration and safe availability checks. Full functional tests require the corresponding local runtime to be installed.
