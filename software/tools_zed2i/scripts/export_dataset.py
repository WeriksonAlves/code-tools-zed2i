"""Command-line interface for exporting ZED2i dataset metadata.

This module provides the ``export_zed2i_dataset`` console script. It parses
command-line arguments, calls the dataset export application service, and
prints the generated output paths.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tools_zed2i.application.dataset.services.dataset_exporter import (
    MANIFEST_SNAPSHOT_FILENAME,
    SAMPLES_CSV_FILENAME,
    SUMMARY_JSON_FILENAME,
    SUMMARY_MARKDOWN_FILENAME,
    DatasetExporter,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for dataset export.

    Returns:
        Parsed command-line arguments.
    """
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

    _print_export_summary(
        dataset_path=arguments.dataset_path,
        output_dir=output_dir,
    )


def _print_export_summary(dataset_path: Path, output_dir: Path) -> None:
    """Print generated dataset export paths.

    Args:
        dataset_path: Source dataset sequence path.
        output_dir: Directory containing exported files.
    """
    print(f"Dataset path: {dataset_path}")
    print(f"Export directory: {output_dir}")
    print(f"Samples CSV: {output_dir / SAMPLES_CSV_FILENAME}")
    print(f"Summary JSON: {output_dir / SUMMARY_JSON_FILENAME}")
    print(f"Summary Markdown: {output_dir / SUMMARY_MARKDOWN_FILENAME}")

    manifest_snapshot_path = output_dir / MANIFEST_SNAPSHOT_FILENAME
    if manifest_snapshot_path.exists():
        print(f"Manifest snapshot: {manifest_snapshot_path}")


if __name__ == "__main__":
    main()
