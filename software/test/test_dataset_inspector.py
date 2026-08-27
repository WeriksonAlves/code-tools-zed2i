from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from tools_zed2i.application.dataset import (
    DatasetInspectionError,
    DatasetInspector,
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


def test_dataset_inspector_inspects_complete_dataset(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset"
    create_sample(dataset_path)

    inspector = DatasetInspector()

    summary = inspector.inspect(dataset_path)

    assert summary.total_samples == 1
    assert summary.complete_samples == 1
    assert summary.incomplete_samples == 0
    assert summary.total_point_count == 5
    assert summary.average_point_count == 5.0

    sample = summary.samples[0]

    assert sample.sample_id == "000000"
    assert sample.left_image_shape == (2, 3, 3)
    assert sample.right_image_shape == (2, 3, 3)
    assert sample.disparity_shape == (2, 3)
    assert sample.point_cloud_shape == (5, 3)
    assert sample.point_count == 5
    assert sample.is_complete()


def test_dataset_inspector_detects_missing_files(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset"
    create_sample(dataset_path)

    (dataset_path / "images" / "right" / "000000.png").unlink()

    inspector = DatasetInspector()

    summary = inspector.inspect(dataset_path)

    assert summary.total_samples == 1
    assert summary.complete_samples == 0
    assert summary.incomplete_samples == 1

    sample = summary.samples[0]

    assert "right_image" in sample.missing_files
    assert not sample.is_complete()


def test_dataset_inspector_raises_for_missing_dataset_path(tmp_path: Path
                                                           ) -> None:
    inspector = DatasetInspector()

    with pytest.raises(DatasetInspectionError):
        inspector.inspect(tmp_path / "missing_dataset")
