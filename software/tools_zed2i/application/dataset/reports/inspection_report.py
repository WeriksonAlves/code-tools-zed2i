"""Markdown and JSON report generation for dataset inspection results."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from tools_zed2i.application.dataset.models.inspection_result import (
    DatasetInspectionSummary,
    DatasetSampleInspection,
)


class DatasetInspectionReportWriter:
    """Writer for dataset inspection reports.

    This class converts inspection summaries into human-readable Markdown and
    JSON files. It is intentionally simple and deterministic to make generated
    reports easy to compare across experiments.
    """

    def save_json(self, summary: DatasetInspectionSummary, output_path: Path
                  ) -> None:
        """Save the inspection summary as a JSON file.

        Args:
            summary: Dataset inspection summary.
            output_path: Destination JSON path.
        """
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
        """Save the inspection summary as a Markdown report.

        Args:
            summary: Dataset inspection summary.
            output_path: Destination Markdown path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            file.write(self.to_markdown(summary))

    def to_markdown(self, summary: DatasetInspectionSummary) -> str:
        """Convert an inspection summary to Markdown text.

        Args:
            summary: Dataset inspection summary.

        Returns:
            Markdown-formatted report.
        """
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
            "| Sample | Complete | Left image | Right image | Disparity | ",
            "Point cloud | Points | Missing | Errors |",
            "|---|---:|---|---|---|---|---:|---|---|",
        ]

        lines.extend(
            self._sample_to_markdown_row(sample)
            for sample in summary.samples
        )
        lines.append("")

        return "\n".join(lines)

    def _sample_to_markdown_row(self, sample: DatasetSampleInspection) -> str:
        """Convert a sample inspection result to a Markdown table row."""
        missing = ", ".join(sample.missing_files
                            ) if sample.missing_files else "-"
        errors = "; ".join(sample.errors) if sample.errors else "-"

        return (
            f"| {sample.sample_id} "
            f"| {sample.is_complete()} "
            f"| {self._format_shape(sample.left_image_shape)} "
            f"| {self._format_shape(sample.right_image_shape)} "
            f"| {self._format_shape(sample.disparity_shape)} "
            f"| {self._format_shape(sample.point_cloud_shape)} | "
            f"{sample.point_count if sample.point_count is not None else '-'} "
            f"| {missing} "
            f"| {errors} |"
        )

    def _summary_to_serializable_dict(
        self,
        summary: DatasetInspectionSummary,
    ) -> dict[str, Any]:
        """Return a JSON-serializable dictionary from an inspection summary."""
        serialized_summary = asdict(summary)
        serialized_summary["dataset_path"] = str(summary.dataset_path)

        for sample in serialized_summary["samples"]:
            for key, value in list(sample.items()):
                if isinstance(value, Path):
                    sample[key] = str(value)

        return serialized_summary

    @staticmethod
    def _format_shape(shape: tuple[int, ...] | None) -> str:
        """Format an array shape for tabular reports."""
        if shape is None:
            return "-"

        return "x".join(str(value) for value in shape)
