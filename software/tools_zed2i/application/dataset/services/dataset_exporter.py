from __future__ import annotations

import csv
import json
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Any

from tools_zed2i.application.dataset.dataset_manifest import DatasetManifestWriter
from tools_zed2i.application.dataset.inspection.dataset_inspector import (
    DatasetInspector,
)
from tools_zed2i.application.dataset.inspection.inspection_report import (
    DatasetInspectionReportWriter,
)
from tools_zed2i.application.dataset.inspection.inspection_result import (
    DatasetInspectionSummary,
    DatasetSampleInspection,
)


class DatasetExportError(RuntimeError):
    """Raised when a dataset export operation fails."""


class DatasetExporter:
    """Exporter for consolidated ZED2i dataset metadata and reports."""

    def __init__(
        self,
        inspector: DatasetInspector | None = None,
        report_writer: DatasetInspectionReportWriter | None = None,
        manifest_writer: DatasetManifestWriter | None = None,
    ) -> None:
        self._inspector = inspector or DatasetInspector()
        self._report_writer = report_writer or DatasetInspectionReportWriter()
        self._manifest_writer = manifest_writer or DatasetManifestWriter()

    def export(
        self,
        dataset_path: Path,
        output_dir: Path | None = None,
    ) -> Path:
        """Export consolidated dataset information to a directory."""
        if not dataset_path.exists():
            raise DatasetExportError(f"Dataset path does not exist: {dataset_path}")

        if not dataset_path.is_dir():
            raise DatasetExportError(f"Dataset path is not a directory: {dataset_path}")

        resolved_output_dir = output_dir or dataset_path / "exports"
        resolved_output_dir.mkdir(parents=True, exist_ok=True)

        summary = self._inspector.inspect(dataset_path=dataset_path)

        self._save_samples_csv(
            summary=summary,
            output_path=resolved_output_dir / "samples.csv",
        )
        self._save_summary_json(
            summary=summary,
            output_path=resolved_output_dir / "summary.json",
        )
        self._report_writer.save_markdown(
            summary=summary,
            output_path=resolved_output_dir / "summary.md",
        )
        self._copy_manifest_if_available(
            dataset_path=dataset_path,
            output_path=resolved_output_dir / "manifest_snapshot.json",
        )

        return resolved_output_dir

    def _save_samples_csv(
        self,
        summary: DatasetInspectionSummary,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "sample_id",
                    "is_complete",
                    "left_image_shape",
                    "right_image_shape",
                    "disparity_shape",
                    "point_cloud_shape",
                    "point_count",
                    "missing_files",
                    "errors",
                ],
            )
            writer.writeheader()

            for sample in summary.samples:
                writer.writerow(self._sample_to_csv_row(sample))

    def _save_summary_json(
        self,
        summary: DatasetInspectionSummary,
        output_path: Path,
    ) -> None:
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
        manifest_path = dataset_path / self._manifest_writer.MANIFEST_FILENAME

        if not manifest_path.exists():
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(manifest_path, output_path)

    @staticmethod
    def _sample_to_csv_row(sample: DatasetSampleInspection) -> dict[str, Any]:
        return {
            "sample_id": sample.sample_id,
            "is_complete": sample.is_complete(),
            "left_image_shape": DatasetExporter._format_shape(
                sample.left_image_shape
            ),
            "right_image_shape": DatasetExporter._format_shape(
                sample.right_image_shape
            ),
            "disparity_shape": DatasetExporter._format_shape(sample.disparity_shape),
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
        summary_dict = asdict(summary)
        summary_dict["dataset_path"] = str(summary.dataset_path)

        for sample in summary_dict["samples"]:
            for key, value in list(sample.items()):
                if isinstance(value, Path):
                    sample[key] = str(value)

        return summary_dict

    @staticmethod
    def _format_shape(shape: tuple[int, ...] | None) -> str:
        if shape is None:
            return ""

        return "x".join(str(value) for value in shape)