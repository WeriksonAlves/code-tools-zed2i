"""Dataset inspection service for recorded ZED2i sequences."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from tools_zed2i.application.dataset.models.inspection_result import (
    DatasetInspectionSummary,
    DatasetSampleInspection,
)

LEFT_IMAGE_RELATIVE_PATH = Path("images") / "left"
RIGHT_IMAGE_RELATIVE_PATH = Path("images") / "right"
DISPARITY_RELATIVE_PATH = Path("disparity")
POINT_CLOUD_RELATIVE_PATH = Path("pointclouds")
METADATA_RELATIVE_PATH = Path("metadata")


class DatasetInspectionError(RuntimeError):
    """Raised when a dataset cannot be inspected."""


class DatasetInspector:
    """Application service for inspecting recorded ZED2i datasets.

    The inspector validates sample completeness and extracts lightweight
    statistics such as image shapes, disparity shapes, point cloud shapes, and
    point counts.

    Note:
        This service still performs concrete file reads using OpenCV, NumPy,
        and JSON. In a stricter hexagonal design, those operations should be
        moved to an infrastructure-level dataset reader adapter.
    """

    def inspect(self, dataset_path: Path) -> DatasetInspectionSummary:
        """Inspect a complete dataset sequence.

        Args:
            dataset_path: Path to the dataset sequence directory.

        Returns:
            Inspection summary for the dataset.

        Raises:
            DatasetInspectionError: If the dataset path is invalid.
        """
        self._validate_dataset_path(dataset_path)

        sample_ids = self._collect_sample_ids(dataset_path)
        samples = [
            self._inspect_sample(
                dataset_path=dataset_path, sample_id=sample_id)
            for sample_id in sample_ids
        ]

        return self._make_summary(dataset_path=dataset_path, samples=samples)

    def _validate_dataset_path(self, dataset_path: Path) -> None:
        """Validate the dataset path before inspection."""
        if not dataset_path.exists():
            raise DatasetInspectionError(
                f"Dataset path does not exist: {dataset_path}")

        if not dataset_path.is_dir():
            raise DatasetInspectionError(
                f"Dataset path is not a directory: {dataset_path}")

    def _collect_sample_ids(self, dataset_path: Path) -> list[str]:
        """Collect sample identifiers from metadata or data folders."""
        metadata_path = dataset_path / METADATA_RELATIVE_PATH

        if metadata_path.exists():
            metadata_ids = sorted(path.stem for path in metadata_path.glob(
                "*.json"))
            if metadata_ids:
                return metadata_ids

        candidate_ids: set[str] = set()

        for relative_folder, pattern in self._sample_id_sources():
            folder = dataset_path / relative_folder
            if folder.exists():
                candidate_ids.update(
                    path.stem for path in folder.glob(pattern))

        return sorted(candidate_ids)

    def _inspect_sample(
        self,
        dataset_path: Path,
        sample_id: str,
    ) -> DatasetSampleInspection:
        """Inspect one dataset sample."""
        missing_files: list[str] = []
        errors: list[str] = []

        left_image_path = self._make_sample_path(
            dataset_path=dataset_path,
            relative_folder=LEFT_IMAGE_RELATIVE_PATH,
            sample_id=sample_id,
            suffix=".png",
        )
        right_image_path = self._make_sample_path(
            dataset_path=dataset_path,
            relative_folder=RIGHT_IMAGE_RELATIVE_PATH,
            sample_id=sample_id,
            suffix=".png",
        )
        disparity_path = self._make_sample_path(
            dataset_path=dataset_path,
            relative_folder=DISPARITY_RELATIVE_PATH,
            sample_id=sample_id,
            suffix=".npy",
        )
        point_cloud_path = self._make_sample_path(
            dataset_path=dataset_path,
            relative_folder=POINT_CLOUD_RELATIVE_PATH,
            sample_id=sample_id,
            suffix=".npy",
        )
        metadata_path = self._make_sample_path(
            dataset_path=dataset_path,
            relative_folder=METADATA_RELATIVE_PATH,
            sample_id=sample_id,
            suffix=".json",
        )

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

        return DatasetSampleInspection(
            sample_id=sample_id,
            left_image_path=self._existing_path_or_none(left_image_path),
            right_image_path=self._existing_path_or_none(right_image_path),
            disparity_path=self._existing_path_or_none(disparity_path),
            point_cloud_path=self._existing_path_or_none(point_cloud_path),
            metadata_path=self._existing_path_or_none(metadata_path),
            left_image_shape=left_image_shape,
            right_image_shape=right_image_shape,
            disparity_shape=disparity_shape,
            point_cloud_shape=point_cloud_shape,
            point_count=self._point_count_from_shape(point_cloud_shape),
            metadata=metadata,
            missing_files=missing_files,
            errors=errors,
        )

    def _make_summary(
        self,
        dataset_path: Path,
        samples: list[DatasetSampleInspection],
    ) -> DatasetInspectionSummary:
        """Create an inspection summary from sample-level results."""
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

    @staticmethod
    def _sample_id_sources() -> list[tuple[Path, str]]:
        """Return data folders used to infer sample identifiers."""
        return [
            (LEFT_IMAGE_RELATIVE_PATH, "*.png"),
            (RIGHT_IMAGE_RELATIVE_PATH, "*.png"),
            (DISPARITY_RELATIVE_PATH, "*.npy"),
            (POINT_CLOUD_RELATIVE_PATH, "*.npy"),
        ]

    @staticmethod
    def _make_sample_path(
        dataset_path: Path,
        relative_folder: Path,
        sample_id: str,
        suffix: str,
    ) -> Path:
        """Return the expected file path for one sample artifact."""
        return dataset_path / relative_folder / f"{sample_id}{suffix}"

    @staticmethod
    def _existing_path_or_none(path: Path) -> Path | None:
        """Return the path only if it exists."""
        if path.exists():
            return path

        return None

    @staticmethod
    def _point_count_from_shape(shape: tuple[int, ...] | None) -> int | None:
        """Infer point count from a point cloud array shape."""
        if shape is None:
            return None

        if not shape:
            return None

        return shape[0]

    @staticmethod
    def _read_image_shape(
        path: Path,
        label: str,
        missing_files: list[str],
        errors: list[str],
    ) -> tuple[int, ...] | None:
        """Read image shape without exposing the loaded image."""
        if not path.exists():
            missing_files.append(label)
            return None

        try:
            image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        except cv2.error as exception:
            errors.append(f"Failed to read {label}: {path}: {exception}")
            return None

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
        """Read a NumPy array shape.

        The array is opened with memory mapping to avoid loading full point
        clouds into memory during inspection.
        """
        if not path.exists():
            missing_files.append(label)
            return None

        try:
            array = np.load(path, mmap_mode="r")
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
        """Read sample metadata from JSON."""
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
