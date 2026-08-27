"""Dataset export service for consolidated ZED2i metadata reports."""

from __future__ import annotations

import csv
import json
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Any

from tools_zed2i.application.dataset.models.inspection_result import (
    DatasetInspectionSummary,
    DatasetSampleInspection,
)
from tools_zed2i.application.dataset.ports import DatasetManifestRepository
from tools_zed2i.application.dataset.reports.inspection_report import (
    DatasetInspectionReportWriter,
)
from tools_zed2i.application.dataset.services.dataset_inspector import DatasetInspector
from tools_zed2i.infrastructure.dataset.file_manifest_repository import (
    DatasetManifestWriter,
)

SAMPLES_CSV_FILENAME = "samples.csv"
SUMMARY_JSON_FILENAME = "summary.json"
SUMMARY_MARKDOWN_FILENAME = "summary.md"
MANIFEST_SNAPSHOT_FILENAME = "manifest_snapshot.json"


class DatasetExportError(RuntimeError):
    """Raised when a dataset export operation fails."""


class DatasetExporter:
    """Application service for exporting consolidated dataset information.

    The exporter generates lightweight artifacts derived from a recorded ZED2i
    dataset, including per-sample CSV data, summary JSON, Markdown reports, and
    a manifest snapshot when available.
    """

    def __init__(
        self,
        inspector: DatasetInspector | None = None,
        report_writer: DatasetInspectionReportWriter | None = None,
        manifest_writer: DatasetManifestRepository | None = None,
    ) -> None:
        """Initialize the dataset exporter.

        Args:
            inspector: Dataset inspection service.
            report_writer: Report writer used to generate Markdown output.
            manifest_writer: Manifest repository used to locate manifest files.
        """
        self._inspector = inspector or DatasetInspector()
        self._report_writer = report_writer or DatasetInspectionReportWriter()
        self._manifest_writer = manifest_writer or DatasetManifestWriter()

    def export(
        self,
        dataset_path: Path,
        output_dir: Path | None = None,
    ) -> Path:
        """Export consolidated dataset information to a directory.

        Args:
            dataset_path: Path to the dataset sequence directory.
            output_dir: Optional export directory. When omitted, exports are
                saved under ``dataset_path / "exports"``.

        Returns:
            Path to the generated export directory.

        Raises:
            DatasetExportError: If the dataset path is invalid or export fails.
        """
        self._validate_dataset_path(dataset_path)

        resolved_output_dir = output_dir or dataset_path / "exports"
        resolved_output_dir.mkdir(parents=True, exist_ok=True)

        try:
            summary = self._inspector.inspect(dataset_path=dataset_path)

            self._save_samples_csv(
                summary=summary,
                output_path=resolved_output_dir / SAMPLES_CSV_FILENAME,
            )
            self._save_summary_json(
                summary=summary,
                output_path=resolved_output_dir / SUMMARY_JSON_FILENAME,
            )
            self._report_writer.save_markdown(
                summary=summary,
                output_path=resolved_output_dir / SUMMARY_MARKDOWN_FILENAME,
            )
            self._copy_manifest_if_available(
                dataset_path=dataset_path,
                output_path=resolved_output_dir / MANIFEST_SNAPSHOT_FILENAME,
            )

            return resolved_output_dir
        except (OSError, RuntimeError, TypeError, ValueError) as exception:
            raise DatasetExportError(
                f"Failed to export dataset {dataset_path}: {exception}"
            ) from exception

    def _validate_dataset_path(self, dataset_path: Path) -> None:
        """Validate the dataset path before export."""
        if not dataset_path.exists():
            raise DatasetExportError(
                f"Dataset path does not exist: {dataset_path}")

        if not dataset_path.is_dir():
            raise DatasetExportError(
                f"Dataset path is not a directory: {dataset_path}")

    def _save_samples_csv(
        self,
        summary: DatasetInspectionSummary,
        output_path: Path,
    ) -> None:
        """Save per-sample inspection data as CSV."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self._csv_fieldnames(),
            )
            writer.writeheader()

            for sample in summary.samples:
                writer.writerow(self._sample_to_csv_row(sample))

    def _save_summary_json(
        self,
        summary: DatasetInspectionSummary,
        output_path: Path,
    ) -> None:
        """Save dataset inspection summary as JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                self._summary_to_serializable_dict(summary),
                file,
                indent=2,
                ensure_ascii=False,
            )

    def _copy_manifest_if_available(
        self,
        dataset_path: Path,
        output_path: Path,
    ) -> None:
        """Copy the dataset manifest to the export directory if it exists."""
        manifest_path = dataset_path / self._manifest_writer.MANIFEST_FILENAME

        if not manifest_path.exists():
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(manifest_path, output_path)

    @staticmethod
    def _csv_fieldnames() -> list[str]:
        """Return CSV field names for sample-level export."""
        return [
            "sample_id",
            "is_complete",
            "left_image_shape",
            "right_image_shape",
            "disparity_shape",
            "point_cloud_shape",
            "point_count",
            "missing_files",
            "errors",
        ]

    @staticmethod
    def _sample_to_csv_row(sample: DatasetSampleInspection) -> dict[str, Any]:
        """Convert a sample inspection result to a CSV row."""
        return {
            "sample_id": sample.sample_id,
            "is_complete": sample.is_complete(),
            "left_image_shape": DatasetExporter._format_shape(
                sample.left_image_shape
            ),
            "right_image_shape": DatasetExporter._format_shape(
                sample.right_image_shape
            ),
            "disparity_shape": DatasetExporter._format_shape(
                sample.disparity_shape),
            "point_cloud_shape": DatasetExporter._format_shape(
                sample.point_cloud_shape
            ),
            "point_count": sample.point_count,
            "missing_files": ",".join(sample.missing_files),
            "errors": ";".join(sample.errors),
        }

    @staticmethod
    def _summary_to_serializable_dict(
        summary: DatasetInspectionSummary,
    ) -> dict[str, Any]:
        """Return a JSON-serializable representation of a summary."""
        summary_dict = asdict(summary)
        summary_dict["dataset_path"] = str(summary.dataset_path)

        for sample in summary_dict["samples"]:
            for key, value in list(sample.items()):
                if isinstance(value, Path):
                    sample[key] = str(value)

        return summary_dict

    @staticmethod
    def _format_shape(shape: tuple[int, ...] | None) -> str:
        """Format an array shape for CSV export."""
        if shape is None:
            return ""

        return "x".join(str(value) for value in shape)
