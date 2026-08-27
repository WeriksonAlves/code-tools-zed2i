"""Dataset inspection result models.

This module defines immutable result objects produced by dataset inspection
services. The models summarize file availability, detected shapes, point cloud
sizes, metadata content, and sample-level errors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetSampleInspection:
    """Inspection result for a single dataset sample.

    Attributes:
        sample_id: Dataset sample identifier.
        left_image_path: Path to the left image file, when available.
        right_image_path: Path to the right image file, when available.
        disparity_path: Path to the disparity array file, when available.
        point_cloud_path: Path to the point cloud array file, when available.
        metadata_path: Path to the metadata file, when available.
        left_image_shape: Shape of the left image array.
        right_image_shape: Shape of the right image array.
        disparity_shape: Shape of the disparity array.
        point_cloud_shape: Shape of the point cloud array.
        point_count: Number of points in the point cloud.
        metadata: Loaded metadata dictionary, when available.
        missing_files: List of missing expected file categories.
        errors: List of inspection errors.
    """

    sample_id: str
    left_image_path: Path | None = None
    right_image_path: Path | None = None
    disparity_path: Path | None = None
    point_cloud_path: Path | None = None
    metadata_path: Path | None = None
    left_image_shape: tuple[int, ...] | None = None
    right_image_shape: tuple[int, ...] | None = None
    disparity_shape: tuple[int, ...] | None = None
    point_cloud_shape: tuple[int, ...] | None = None
    point_count: int | None = None
    metadata: dict[str, Any] | None = None
    missing_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def is_complete(self) -> bool:
        """Return whether the sample has no missing files or errors."""
        return not self.missing_files and not self.errors

    def has_point_cloud(self) -> bool:
        """Return whether the sample contains a valid point cloud reference."""
        return self.point_cloud_path is not None and self.point_count is not None


@dataclass(frozen=True)
class DatasetInspectionSummary:
    """Inspection summary for a complete dataset sequence.

    Attributes:
        dataset_path: Path to the inspected dataset sequence.
        total_samples: Number of inspected samples.
        complete_samples: Number of complete samples.
        incomplete_samples: Number of incomplete samples.
        total_point_count: Total number of points across inspected samples.
        average_point_count: Average point count per sample, when available.
        samples: Sample-level inspection results.
    """

    dataset_path: Path
    total_samples: int
    complete_samples: int
    incomplete_samples: int
    total_point_count: int
    average_point_count: float | None
    samples: list[DatasetSampleInspection]

    def has_errors(self) -> bool:
        """Return whether at least one sample has missing files or errors."""
        return self.incomplete_samples > 0

    def is_empty(self) -> bool:
        """Return whether the summary has no inspected samples."""
        return self.total_samples == 0

    def completion_ratio(self) -> float | None:
        """Return the ratio of complete samples.

        Returns:
            Ratio in the range [0.0, 1.0], or ``None`` when there are no
            inspected samples.
        """
        if self.total_samples == 0:
            return None

        return self.complete_samples / self.total_samples
