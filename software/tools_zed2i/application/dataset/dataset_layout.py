from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools_zed2i.application.dataset.dataset_config import DatasetRecordingConfig


@dataclass(frozen=True)
class DatasetLayout:
    """Directory layout for a recorded ZED2i dataset sequence."""

    sequence_path: Path
    left_images_path: Path
    right_images_path: Path
    disparity_path: Path
    pointclouds_path: Path
    metadata_path: Path

    @classmethod
    def from_config(cls, config: DatasetRecordingConfig) -> DatasetLayout:
        sequence_path = config.sequence_path

        return cls(
            sequence_path=sequence_path,
            left_images_path=sequence_path / "images" / "left",
            right_images_path=sequence_path / "images" / "right",
            disparity_path=sequence_path / "disparity",
            pointclouds_path=sequence_path / "pointclouds",
            metadata_path=sequence_path / "metadata",
        )

    def create_directories(self) -> None:
        self.left_images_path.mkdir(parents=True, exist_ok=True)
        self.right_images_path.mkdir(parents=True, exist_ok=True)
        self.disparity_path.mkdir(parents=True, exist_ok=True)
        self.pointclouds_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
