from __future__ import annotations

import json
from pathlib import Path

from tools_zed2i.application.dataset.inspection.inspection_report import (
    DatasetInspectionReportWriter,
)
from tools_zed2i.application.dataset.inspection.inspection_result import (
    DatasetInspectionSummary,
    DatasetSampleInspection,
)


def test_dataset_inspection_report_writer_saves_json(tmp_path: Path) -> None:
    summary = DatasetInspectionSummary(
        dataset_path=tmp_path / "dataset",
        total_samples=1,
        complete_samples=1,
        incomplete_samples=0,
        total_point_count=10,
        average_point_count=10.0,
        samples=[
            DatasetSampleInspection(
                sample_id="000000",
                point_count=10,
                point_cloud_shape=(10, 3),
            )
        ],
    )

    output_path = tmp_path / "report" / "inspection_summary.json"

    writer = DatasetInspectionReportWriter()
    writer.save_json(summary=summary, output_path=output_path)

    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        loaded_report = json.load(file)

    assert loaded_report["total_samples"] == 1
    assert loaded_report["samples"][0]["sample_id"] == "000000"


def test_dataset_inspection_report_writer_saves_markdown(tmp_path: Path) -> None:
    summary = DatasetInspectionSummary(
        dataset_path=tmp_path / "dataset",
        total_samples=1,
        complete_samples=1,
        incomplete_samples=0,
        total_point_count=10,
        average_point_count=10.0,
        samples=[
            DatasetSampleInspection(
                sample_id="000000",
                point_count=10,
                point_cloud_shape=(10, 3),
            )
        ],
    )

    output_path = tmp_path / "report" / "inspection_report.md"

    writer = DatasetInspectionReportWriter()
    writer.save_markdown(summary=summary, output_path=output_path)

    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    assert "# Dataset Inspection Report" in content
    assert "Total samples: 1" in content
    assert "000000" in content