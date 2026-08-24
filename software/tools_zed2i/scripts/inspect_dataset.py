from __future__ import annotations

import argparse
from pathlib import Path

from tools_zed2i.application.dataset.inspection.dataset_inspector import (
    DatasetInspector,
)
from tools_zed2i.application.dataset.inspection.inspection_report import (
    DatasetInspectionReportWriter,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
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
    output_dir = arguments.output_dir or dataset_path / "inspection"

    inspector = DatasetInspector()
    report_writer = DatasetInspectionReportWriter()

    summary = inspector.inspect(dataset_path=dataset_path)

    json_report_path = output_dir / "inspection_summary.json"
    markdown_report_path = output_dir / "inspection_report.md"

    report_writer.save_json(summary=summary, output_path=json_report_path)
    report_writer.save_markdown(summary=summary, output_path=markdown_report_path)

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