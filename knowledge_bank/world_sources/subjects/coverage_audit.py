from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TAXONOMY = ROOT / "learning_subjects.json"
TAXONOMY_EXTENSION = ROOT / "learning_subjects_extension_v1.json"
RESOURCES = ROOT / "resources"
OUTPUT = ROOT / "coverage_matrix_v2.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_taxonomy() -> dict:
    taxonomy = load_json(TAXONOMY)
    subjects = dict(taxonomy.get("subjects", {}))

    if TAXONOMY_EXTENSION.is_file():
        extension = load_json(TAXONOMY_EXTENSION)
        ext_levels = extension.get("levels", taxonomy.get("levels", []))
        if ext_levels != taxonomy.get("levels", []):
            raise ValueError("Taxonomy extension levels must match canonical taxonomy levels")

        overlap = sorted(set(subjects) & set(extension.get("subjects", {})))
        if overlap:
            raise ValueError(f"Taxonomy extension duplicates canonical subjects: {overlap}")
        subjects.update(extension.get("subjects", {}))

    taxonomy["subjects"] = subjects
    return taxonomy


def iter_subject_manifests(subject: str):
    """Yield every resource manifest for a subject, including nested depth folders."""
    for path in sorted(RESOURCES.rglob(f"{subject}*.json")):
        if path.name == OUTPUT.name:
            continue
        yield path, load_json(path)


def build_coverage() -> dict:
    taxonomy = load_taxonomy()
    levels = taxonomy["levels"]
    subjects = taxonomy["subjects"]

    report = {
        "schema_version": "2.1",
        "levels": levels,
        "subjects": {},
        "summary": {},
    }
    total_cells = 0
    covered_cells = 0

    for subject, subject_meta in subjects.items():
        subsubjects = subject_meta["subsubjects"]
        cell_resources = defaultdict(list)

        for path, manifest in iter_subject_manifests(subject):
            for resource in manifest.get("resources", []):
                resource_levels = resource.get("levels", [])
                resource_subsubjects = resource.get("subsubjects", [])
                resource_ref = {
                    "title": resource.get("title"),
                    "provider": resource.get("provider"),
                    "resource_type": resource.get("resource_type"),
                    "manifest": str(path.relative_to(RESOURCES)),
                    "url": resource.get("url"),
                }
                for subsubject in resource_subsubjects:
                    if subsubject not in subsubjects:
                        continue
                    for level in resource_levels:
                        if level in levels:
                            cell_resources[(subsubject, level)].append(resource_ref)

        matrix = {}
        subject_total = len(subsubjects) * len(levels)
        subject_covered = 0
        gaps = []

        for subsubject in subsubjects:
            matrix[subsubject] = {}
            for level in levels:
                resources = cell_resources[(subsubject, level)]
                is_covered = bool(resources)
                if is_covered:
                    subject_covered += 1
                else:
                    gaps.append({"subsubject": subsubject, "level": level})
                matrix[subsubject][level] = {
                    "covered": is_covered,
                    "resource_count": len(resources),
                    "resources": resources,
                }

        total_cells += subject_total
        covered_cells += subject_covered
        report["subjects"][subject] = {
            "subsubject_count": len(subsubjects),
            "total_cells": subject_total,
            "covered_cells": subject_covered,
            "coverage_percent": round(subject_covered / subject_total * 100, 2) if subject_total else 0.0,
            "gap_count": len(gaps),
            "gaps": gaps,
            "matrix": matrix,
        }

    report["summary"] = {
        "subject_count": len(subjects),
        "level_count": len(levels),
        "total_cells": total_cells,
        "covered_cells": covered_cells,
        "gap_cells": total_cells - covered_cells,
        "coverage_percent": round(covered_cells / total_cells * 100, 2) if total_cells else 0.0,
        "definition": "A cell is covered when at least one manifest resource explicitly maps to that exact subsubject and level.",
    }
    return report


def main() -> None:
    report = build_coverage()
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
