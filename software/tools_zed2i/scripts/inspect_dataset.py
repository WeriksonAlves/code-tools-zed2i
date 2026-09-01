"""Command-line interface for inspecting ZED2i datasets.

This module provides the ``inspect_zed2i_dataset`` console script. It parses
command-line arguments, runs the dataset inspection service, writes inspection
reports, updates the dataset manifest when available, and prints a compact
summary to stdout.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tools_zed2i.application.dataset.models.inspection_result import (
    DatasetInspectionSummary,
)
from tools_zed2i.application.dataset.reports.inspection_report import (
    DatasetInspectionReportWriter,
)
from tools_zed2i.application.dataset.services.dataset_inspector import (
    DatasetInspector,
)
from tools_zed2i.infrastructure.dataset.file_manifest_repository import (
    DatasetManifestWriter,
)

DEFAULT_INSPECTION_DIRNAME = "inspection"
INSPECTION_JSON_FILENAME = "inspection_summary.json"
INSPECTION_MARKDOWN_FILENAME = "inspection_report.md"


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for dataset inspection.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Inspect a dataset recorded with tools_zed2i.",
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
        help="Directory where inspection reports will be saved.",
    )

    return parser.parse_args()


def main() -> None:
    """Run dataset inspection from the command line."""
    arguments = parse_arguments()

    dataset_path = arguments.dataset_path
    output_dir = (
        arguments.output_dir or dataset_path / DEFAULT_INSPECTION_DIRNAME
    )

    inspector = DatasetInspector()
    report_writer = DatasetInspectionReportWriter()

    summary = inspector.inspect(dataset_path=dataset_path)

    json_report_path = output_dir / INSPECTION_JSON_FILENAME
    markdown_report_path = output_dir / INSPECTION_MARKDOWN_FILENAME

    report_writer.save_json(summary=summary, output_path=json_report_path)
    report_writer.save_markdown(
        summary=summary, output_path=markdown_report_path)

    _update_manifest_if_available(dataset_path=dataset_path, summary=summary)

    _print_inspection_summary(
        summary=summary,
        json_report_path=json_report_path,
        markdown_report_path=markdown_report_path,
    )


def _update_manifest_if_available(
    dataset_path: Path,
    summary: DatasetInspectionSummary,
) -> None:
    """Update the dataset manifest with inspection results when available.

    Args:
        dataset_path: Dataset sequence path.
        summary: Dataset inspection summary.
    """
    manifest_writer = DatasetManifestWriter()
    manifest_path = dataset_path / manifest_writer.MANIFEST_FILENAME

    if not manifest_path.exists():
        return

    manifest = manifest_writer.load(manifest_path)
    updated_manifest = manifest_writer.attach_inspection_summary(
        manifest=manifest,
        inspection_summary=_make_manifest_inspection_summary(summary),
    )

    manifest_writer.save(updated_manifest, manifest_path)


def _make_manifest_inspection_summary(
    summary: DatasetInspectionSummary,
) -> dict[str, int | float | None]:
    """Create a compact inspection summary for the dataset manifest.

    Args:
        summary: Full dataset inspection summary.

    Returns:
        Compact dictionary suitable for manifest storage.
    """
    return {
        "total_samples": summary.total_samples,
        "complete_samples": summary.complete_samples,
        "incomplete_samples": summary.incomplete_samples,
        "total_point_count": summary.total_point_count,
        "average_point_count": summary.average_point_count,
    }


def _print_inspection_summary(
    summary: DatasetInspectionSummary,
    json_report_path: Path,
    markdown_report_path: Path,
) -> None:
    """Print a compact inspection summary to stdout.

    Args:
        summary: Dataset inspection summary.
        json_report_path: Path to the generated JSON report.
        markdown_report_path: Path to the generated Markdown report.
    """
    print(f"Dataset path: {summary.dataset_path}")
    print(f"Total samples: {summary.total_samples}")
    print(f"Complete samples: {summary.complete_samples}")
    print(f"Incomplete samples: {summary.incomplete_samples}")
    print(f"Total point count: {summary.total_point_count}")
    print(f"Average point count: {summary.average_point_count}")
    print(f"JSON report: {json_report_path}")
    print(f"Markdown report: {markdown_report_path}")


if __name__ == "__main__":
    main()
