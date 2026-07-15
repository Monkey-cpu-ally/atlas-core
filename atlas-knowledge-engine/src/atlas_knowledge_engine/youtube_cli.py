"""Command-line entry point for live ATLAS YouTube ingestion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .youtube_ingestion import IngestionError, YouTubeIngestionService
from .youtube_live import YouTubeOEmbedMetadataProvider, YouTubeTranscriptProvider


def save_record(record: dict[str, object], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_id = str(record["source_id"])
    transcript_hash = str(record["transcript_hash"])
    output_path = output_dir / f"{source_id}.json"

    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        if existing.get("transcript_hash") == transcript_hash:
            raise IngestionError("This exact transcript is already stored in ATLAS.")

    output_path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retrieve an authorized YouTube transcript and prepare an ATLAS record."
    )
    parser.add_argument("url", help="YouTube video, Short, live, or youtu.be URL")
    parser.add_argument("--subject", action="append", default=[], help="ATLAS subject tag")
    parser.add_argument("--agent", action="append", default=[], help="Assigned ATLAS AI")
    parser.add_argument(
        "--output-dir",
        default="knowledge/ingested/youtube",
        help="Directory used for JSON knowledge records",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    service = YouTubeIngestionService(
        YouTubeTranscriptProvider(),
        YouTubeOEmbedMetadataProvider(),
    )

    try:
        record = service.ingest(
            args.url,
            subjects=args.subject,
            assigned_agents=args.agent,
        )
        output_path = save_record(record.to_dict(), Path(args.output_dir))
    except IngestionError as exc:
        print(f"ATLAS ingestion failed: {exc}")
        return 1

    print(f"Saved pending-review knowledge record: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
