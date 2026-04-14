"""CLI script for document ingestion."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ingestion.pipeline import IngestionPipeline


def main():
    parser = argparse.ArgumentParser(description="Ingest SAP documents into the vector store")
    parser.add_argument("--path", help="Path to file or directory to ingest")
    parser.add_argument("--url", help="Single public URL to ingest")
    parser.add_argument("--urls-file", help="Text file with one URL per line")
    parser.add_argument("--module", default="", help="SAP module tag (e.g., S4HANA, SF, OnBase)")
    parser.add_argument("--recursive", action="store_true", help="Recursively process directories")
    args = parser.parse_args()

    if not args.path and not args.url and not args.urls_file:
        parser.error("Provide --path, --url, or --urls-file")

    pipeline = IngestionPipeline()
    total = 0

    if args.url:
        print(f"Ingesting URL: {args.url}")
        total += pipeline.ingest_url(args.url, module=args.module)

    if args.urls_file:
        urls_path = Path(args.urls_file)
        if not urls_path.exists():
            print(f"Error: URLs file not found: {urls_path}")
            sys.exit(1)
        urls = [line.strip() for line in urls_path.read_text().splitlines() if line.strip() and not line.startswith("#")]
        print(f"Ingesting {len(urls)} URLs from {urls_path}")
        total += pipeline.ingest_urls(urls, module=args.module)

    if args.path:
        path = Path(args.path)
        if path.is_file():
            print(f"Ingesting file: {path}")
            total += pipeline.ingest_file(path, module=args.module)
        elif path.is_dir():
            print(f"Ingesting directory: {path} (recursive={args.recursive})")
            total += pipeline.ingest_directory(path, recursive=args.recursive, module=args.module)
        else:
            print(f"Error: Path not found: {path}")
            sys.exit(1)

    print(f"Done! {total} chunks ingested into vector store.")


if __name__ == "__main__":
    main()
