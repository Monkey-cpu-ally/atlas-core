from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TAXONOMY = ROOT / "learning_subjects.json"
RESOURCES = ROOT / "resources"
OUTPUT = ROOT / "coverage_matrix_v2.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_subject_manifests(subject: str):
    for path in sorted(RESOURCES.glob(f"{subject}*.json")):
        yield path, load_json(path)


def build_coverage() -> dict:
    taxonomy = load_json(TAXONOMY)
    levels = taxonomy["levels"]
    subjects = taxonomy["subjects"]

    report = {
        "schema_version": "2.0",
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
                    "manifest": path.name,
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
