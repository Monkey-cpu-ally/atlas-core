from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import MaterialProfile
from .service import LuxuryDesignService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlas-luxury")
    parser.add_argument("--database", default="atlas_luxury.db")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize the SQLite database")

    create_project = subparsers.add_parser("create-project")
    create_project.add_argument("design_id")
    create_project.add_argument("name")
    create_project.add_argument("product_type")
    create_project.add_argument("description")

    add_material = subparsers.add_parser("add-material")
    add_material.add_argument("name")
    add_material.add_argument("category")
    add_material.add_argument("--repairability", type=float, default=0.5)
    add_material.add_argument("--sustainability", type=float, default=0.5)
    add_material.add_argument("--aging-quality", type=float, default=0.5)
    add_material.add_argument("--notes", default="")

    update_progress = subparsers.add_parser("update-progress")
    update_progress.add_argument("module_id")
    update_progress.add_argument("completion", type=float)
    update_progress.add_argument("--evidence", default="")

    subparsers.add_parser("show-progress")
    subparsers.add_parser("list-projects")
    subparsers.add_parser("list-materials")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    service = LuxuryDesignService(Path(args.database))
    service.initialize()

    if args.command == "init":
        print(f"Initialized {args.database}")
    elif args.command == "create-project":
        record = service.create_project(
            args.design_id, args.name, args.product_type, args.description
        )
        print(json.dumps({"design_id": record.concept.design_id, "stage": record.stage.value}))
    elif args.command == "add-material":
        material = MaterialProfile(
            name=args.name,
            category=args.category,
            properties={},
            repairability=args.repairability,
            sustainability=args.sustainability,
            aging_quality=args.aging_quality,
            notes=args.notes,
        )
        service.add_material(material)
        print(json.dumps({"saved_material": material.name}))
    elif args.command == "update-progress":
        service.progress_repository.update(args.module_id, args.completion, args.evidence)
        print(json.dumps(service.progress_report(), indent=2))
    elif args.command == "show-progress":
        print(json.dumps(service.progress_report(), indent=2))
    elif args.command == "list-projects":
        print(json.dumps(service.projects.list_ids(), indent=2))
    elif args.command == "list-materials":
        print(json.dumps([item.name for item in service.materials.list_all()], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
