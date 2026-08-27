"""Dataset directory layout models.

This module defines the directory structure expected for recorded ZED2i dataset
sequences. The layout object centralizes path construction and avoids spreading
hard-coded directory names across the application layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools_zed2i.application.dataset.models.dataset_config import (
    DatasetRecordingConfig,
)


@dataclass(frozen=True)
class DatasetLayout:
    """Directory layout for a recorded ZED2i dataset sequence.

    Attributes:
        sequence_path: Root path of the dataset sequence.
        left_images_path: Directory containing saved left images.
        right_images_path: Directory containing saved right images.
        disparity_path: Directory containing saved disparity arrays.
        pointclouds_path: Directory containing saved point cloud arrays.
        metadata_path: Directory containing saved metadata files.
    """

    sequence_path: Path
    left_images_path: Path
    right_images_path: Path
    disparity_path: Path
    pointclouds_path: Path
    metadata_path: Path

    @classmethod
    def from_config(cls, config: DatasetRecordingConfig) -> DatasetLayout:
        """Create a dataset layout from a recording configuration.

        Args:
            config: Dataset recording configuration.

        Returns:
            Dataset layout derived from the configured sequence path.
        """
        sequence_path = config.sequence_path

        return cls(
            sequence_path=sequence_path,
            left_images_path=sequence_path / "images" / "left",
            right_images_path=sequence_path / "images" / "right",
            disparity_path=sequence_path / "disparity",
            pointclouds_path=sequence_path / "pointclouds",
            metadata_path=sequence_path / "metadata",
        )

    def directories(self) -> list[Path]:
        """Return all directories required by the dataset layout."""
        return [
            self.left_images_path,
            self.right_images_path,
            self.disparity_path,
            self.pointclouds_path,
            self.metadata_path,
        ]

    def create_directories(self) -> None:
        """Create all directories required by the dataset layout.

        This method is kept for backward compatibility with the current dataset
        recorder. In a stricter hexagonal design, directory creation should be
        moved to an infrastructure adapter.
        """
        for directory in self.directories():
            directory.mkdir(parents=True, exist_ok=True)
