from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from tools_zed2i.application.dataset.inspection.inspection_result import (
    DatasetInspectionSummary,
    DatasetSampleInspection,
)


class DatasetInspectionReportWriter:
    """Writer for dataset inspection reports."""

    def save_json(self, summary: DatasetInspectionSummary, output_path: Path) -> None:
        """Save the inspection summary as JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                self._summary_to_serializable_dict(summary),
                file,
                indent=2,
                ensure_ascii=False,
            )

    def save_markdown(
        self,
        summary: DatasetInspectionSummary,
        output_path: Path,
    ) -> None:
        """Save the inspection summary as a Markdown report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            file.write(self.to_markdown(summary))

    def to_markdown(self, summary: DatasetInspectionSummary) -> str:
        """Convert the inspection summary to Markdown."""
        lines = [
            "# Dataset Inspection Report",
            "",
            f"Dataset path: `{summary.dataset_path}`",
            "",
            "## Summary",
            "",
            f"- Total samples: {summary.total_samples}",
            f"- Complete samples: {summary.complete_samples}",
            f"- Incomplete samples: {summary.incomplete_samples}",
            f"- Total point count: {summary.total_point_count}",
            f"- Average point count: {summary.average_point_count}",
            "",
            "## Samples",
            "",
            "| Sample | Complete | Left image | Right image | Disparity | Point cloud | Points | Missing | Errors |",
            "|---|---:|---|---|---|---|---:|---|---|",
        ]

        for sample in summary.samples:
            lines.append(self._sample_to_markdown_row(sample))

        lines.append("")

        return "\n".join(lines)

    def _sample_to_markdown_row(self, sample: DatasetSampleInspection) -> str:
        missing = ", ".join(sample.missing_files) if sample.missing_files else "-"
        errors = "; ".join(sample.errors) if sample.errors else "-"

        return (
            f"| {sample.sample_id} "
            f"| {sample.is_complete()} "
            f"| {self._format_shape(sample.left_image_shape)} "
            f"| {self._format_shape(sample.right_image_shape)} "
            f"| {self._format_shape(sample.disparity_shape)} "
            f"| {self._format_shape(sample.point_cloud_shape)} "
            f"| {sample.point_count if sample.point_count is not None else '-'} "
            f"| {missing} "
            f"| {errors} |"
        )

    def _summary_to_serializable_dict(
        self,
        summary: DatasetInspectionSummary,
    ) -> dict[str, Any]:
        serialized_summary = asdict(summary)
        serialized_summary["dataset_path"] = str(summary.dataset_path)

        for sample in serialized_summary["samples"]:
            for key, value in list(sample.items()):
                if isinstance(value, Path):
                    sample[key] = str(value)

        return serialized_summary

    @staticmethod
    def _format_shape(shape: tuple[int, ...] | None) -> str:
        if shape is None:
            return "-"

        return "x".join(str(value) for value in shape)