from __future__ import annotations

import argparse
from pathlib import Path

from tools_zed2i.application.dataset.export.dataset_exporter import DatasetExporter


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Export consolidated metadata from a tools_zed2i dataset.",
    )
    parser.add_argument(
        "dataset_path",
        type=Path,
        help="Path to the dataset sequence directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory where exported files will be saved.",
    )

    return parser.parse_args()


def main() -> None:
    """Run dataset export from the command line."""
    arguments = parse_arguments()

    exporter = DatasetExporter()
    output_dir = exporter.export(
        dataset_path=arguments.dataset_path,
        output_dir=arguments.output_dir,
    )

    print(f"Dataset path: {arguments.dataset_path}")
    print(f"Export directory: {output_dir}")
    print(f"Samples CSV: {output_dir / 'samples.csv'}")
    print(f"Summary JSON: {output_dir / 'summary.json'}")
    print(f"Summary Markdown: {output_dir / 'summary.md'}")

    manifest_snapshot_path = output_dir / "manifest_snapshot.json"
    if manifest_snapshot_path.exists():
        print(f"Manifest snapshot: {manifest_snapshot_path}")


if __name__ == "__main__":
    main()