from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetSampleInspection:
    """Inspection result for a single dataset sample."""

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
        """Return True when the sample has no missing files or inspection errors."""
        return not self.missing_files and not self.errors


@dataclass(frozen=True)
class DatasetInspectionSummary:
    """Inspection summary for a complete dataset sequence."""

    dataset_path: Path
    total_samples: int
    complete_samples: int
    incomplete_samples: int
    total_point_count: int
    average_point_count: float | None
    samples: list[DatasetSampleInspection]

    def has_errors(self) -> bool:
        """Return True when at least one sample has missing files or errors."""
        return self.incomplete_samples > 0
