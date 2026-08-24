from __future__ import annotations

import csv
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from tools_zed2i.application.dataset.dataset_config import DatasetRecordingConfig
from tools_zed2i.application.dataset.dataset_manifest import DatasetManifestWriter
from tools_zed2i.application.dataset.export.dataset_exporter import (
    DatasetExporter,
    DatasetExportError,
)


def create_sample(dataset_path: Path, sample_id: str = "000000") -> None:
    left_path = dataset_path / "images" / "left" / f"{sample_id}.png"
    right_path = dataset_path / "images" / "right" / f"{sample_id}.png"
    disparity_path = dataset_path / "disparity" / f"{sample_id}.npy"
    point_cloud_path = dataset_path / "pointclouds" / f"{sample_id}.npy"
    metadata_path = dataset_path / "metadata" / f"{sample_id}.json"

    left_path.parent.mkdir(parents=True, exist_ok=True)
    right_path.parent.mkdir(parents=True, exist_ok=True)
    disparity_path.parent.mkdir(parents=True, exist_ok=True)
    point_cloud_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    cv2.imwrite(str(left_path), np.zeros((2, 3, 3), dtype=np.uint8))
    cv2.imwrite(str(right_path), np.zeros((2, 3, 3), dtype=np.uint8))
    np.save(disparity_path, np.zeros((2, 3), dtype=np.float32))
    np.save(point_cloud_path, np.zeros((5, 3), dtype=np.float32))

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump({"sample_id": sample_id}, file)


def create_manifest(dataset_path: Path) -> None:
    writer = DatasetManifestWriter()
    config = DatasetRecordingConfig(
        dataset_root=dataset_path.parent,
        sequence_name=dataset_path.name,
    )

    manifest = writer.create_from_recording_config(config)
    writer.save(manifest)


def test_dataset_exporter_exports_dataset_reports(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset"
    create_sample(dataset_path)
    create_manifest(dataset_path)

    exporter = DatasetExporter()

    output_dir = exporter.export(dataset_path=dataset_path)

    assert output_dir.exists()
    assert (output_dir / "samples.csv").exists()
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "summary.md").exists()
    assert (output_dir / "manifest_snapshot.json").exists()


def test_dataset_exporter_writes_samples_csv(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset"
    create_sample(dataset_path)

    exporter = DatasetExporter()

    output_dir = exporter.export(dataset_path=dataset_path)

    with (output_dir / "samples.csv").open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["sample_id"] == "000000"
    assert rows[0]["is_complete"] == "True"
    assert rows[0]["left_image_shape"] == "2x3x3"
    assert rows[0]["point_cloud_shape"] == "5x3"
    assert rows[0]["point_count"] == "5"


def test_dataset_exporter_writes_summary_json(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset"
    create_sample(dataset_path)

    exporter = DatasetExporter()

    output_dir = exporter.export(dataset_path=dataset_path)

    with (output_dir / "summary.json").open("r", encoding="utf-8") as file:
        summary = json.load(file)

    assert summary["total_samples"] == 1
    assert summary["complete_samples"] == 1
    assert summary["incomplete_samples"] == 0
    assert summary["total_point_count"] == 5


def test_dataset_exporter_raises_for_missing_dataset(tmp_path: Path) -> None:
    exporter = DatasetExporter()

    with pytest.raises(DatasetExportError):
        exporter.export(dataset_path=tmp_path / "missing_dataset")