from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from tools_zed2i.application.dataset.inspection.inspection_result import (
    DatasetInspectionSummary,
    DatasetSampleInspection,
)


class DatasetInspectionError(RuntimeError):
    """Raised when a dataset cannot be inspected."""


class DatasetInspector:
    """Inspector for datasets recorded with the ZED2i dataset recorder."""

    def inspect(self, dataset_path: Path) -> DatasetInspectionSummary:
        """Inspect a complete dataset sequence."""
        if not dataset_path.exists():
            raise DatasetInspectionError(f"Dataset path does not exist: {dataset_path}")

        if not dataset_path.is_dir():
            raise DatasetInspectionError(f"Dataset path is not a directory: {dataset_path}")

        sample_ids = self._collect_sample_ids(dataset_path)
        samples = [
            self._inspect_sample(dataset_path=dataset_path, sample_id=sample_id)
            for sample_id in sample_ids
        ]

        complete_samples = sum(sample.is_complete() for sample in samples)
        incomplete_samples = len(samples) - complete_samples
        point_counts = [
            sample.point_count
            for sample in samples
            if sample.point_count is not None
        ]
        total_point_count = sum(point_counts)
        average_point_count = (
            total_point_count / len(point_counts) if point_counts else None
        )

        return DatasetInspectionSummary(
            dataset_path=dataset_path,
            total_samples=len(samples),
            complete_samples=complete_samples,
            incomplete_samples=incomplete_samples,
            total_point_count=total_point_count,
            average_point_count=average_point_count,
            samples=samples,
        )

    def _collect_sample_ids(self, dataset_path: Path) -> list[str]:
        metadata_path = dataset_path / "metadata"

        if metadata_path.exists():
            metadata_ids = sorted(path.stem for path in metadata_path.glob("*.json"))
            if metadata_ids:
                return metadata_ids

        candidate_ids: set[str] = set()

        for relative_folder, pattern in [
            ("images/left", "*.png"),
            ("images/right", "*.png"),
            ("disparity", "*.npy"),
            ("pointclouds", "*.npy"),
        ]:
            folder = dataset_path / relative_folder
            if folder.exists():
                candidate_ids.update(path.stem for path in folder.glob(pattern))

        return sorted(candidate_ids)

    def _inspect_sample(
        self,
        dataset_path: Path,
        sample_id: str,
    ) -> DatasetSampleInspection:
        missing_files: list[str] = []
        errors: list[str] = []

        left_image_path = dataset_path / "images" / "left" / f"{sample_id}.png"
        right_image_path = dataset_path / "images" / "right" / f"{sample_id}.png"
        disparity_path = dataset_path / "disparity" / f"{sample_id}.npy"
        point_cloud_path = dataset_path / "pointclouds" / f"{sample_id}.npy"
        metadata_path = dataset_path / "metadata" / f"{sample_id}.json"

        left_image_shape = self._read_image_shape(
            path=left_image_path,
            label="left_image",
            missing_files=missing_files,
            errors=errors,
        )
        right_image_shape = self._read_image_shape(
            path=right_image_path,
            label="right_image",
            missing_files=missing_files,
            errors=errors,
        )
        disparity_shape = self._read_array_shape(
            path=disparity_path,
            label="disparity",
            missing_files=missing_files,
            errors=errors,
        )
        point_cloud_shape = self._read_array_shape(
            path=point_cloud_path,
            label="point_cloud",
            missing_files=missing_files,
            errors=errors,
        )
        metadata = self._read_metadata(
            path=metadata_path,
            missing_files=missing_files,
            errors=errors,
        )

        point_count = None
        if point_cloud_shape is not None and len(point_cloud_shape) >= 1:
            point_count = point_cloud_shape[0]

        return DatasetSampleInspection(
            sample_id=sample_id,
            left_image_path=left_image_path if left_image_path.exists() else None,
            right_image_path=right_image_path if right_image_path.exists() else None,
            disparity_path=disparity_path if disparity_path.exists() else None,
            point_cloud_path=point_cloud_path if point_cloud_path.exists() else None,
            metadata_path=metadata_path if metadata_path.exists() else None,
            left_image_shape=left_image_shape,
            right_image_shape=right_image_shape,
            disparity_shape=disparity_shape,
            point_cloud_shape=point_cloud_shape,
            point_count=point_count,
            metadata=metadata,
            missing_files=missing_files,
            errors=errors,
        )

    @staticmethod
    def _read_image_shape(
        path: Path,
        label: str,
        missing_files: list[str],
        errors: list[str],
    ) -> tuple[int, ...] | None:
        if not path.exists():
            missing_files.append(label)
            return None

        image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

        if image is None:
            errors.append(f"Failed to read {label}: {path}")
            return None

        return tuple(int(value) for value in image.shape)

    @staticmethod
    def _read_array_shape(
        path: Path,
        label: str,
        missing_files: list[str],
        errors: list[str],
    ) -> tuple[int, ...] | None:
        if not path.exists():
            missing_files.append(label)
            return None

        try:
            array = np.load(path)
            return tuple(int(value) for value in array.shape)
        except (OSError, ValueError) as exception:
            errors.append(f"Failed to read {label}: {path}: {exception}")
            return None

    @staticmethod
    def _read_metadata(
        path: Path,
        missing_files: list[str],
        errors: list[str],
    ) -> dict[str, Any] | None:
        if not path.exists():
            missing_files.append("metadata")
            return None

        try:
            with path.open("r", encoding="utf-8") as file:
                loaded_metadata = json.load(file)

            if not isinstance(loaded_metadata, dict):
                errors.append(f"Metadata is not a JSON object: {path}")
                return None

            return loaded_metadata
        except (OSError, JSONDecodeError) as exception:
            errors.append(f"Failed to read metadata: {path}: {exception}")
            return None