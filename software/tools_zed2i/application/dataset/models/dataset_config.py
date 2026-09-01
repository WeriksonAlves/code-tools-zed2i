"""Dataset recording configuration models.

This module defines immutable configuration objects used to describe how ZED2i
sensor snapshots should be recorded into dataset sequences.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetRecordingConfig:
    """Configuration for recording ZED2i sensor snapshots.

    Attributes:
        dataset_root: Root directory where dataset sequences are stored.
        sequence_name: Name of the dataset sequence.
        save_left_image: Whether left images should be saved.
        save_right_image: Whether right images should be saved.
        save_disparity: Whether disparity arrays should be saved.
        save_point_cloud: Whether point cloud arrays should be saved.
        save_metadata: Whether metadata files should be saved.
    """

    dataset_root: Path
    sequence_name: str
    save_left_image: bool = True
    save_right_image: bool = True
    save_disparity: bool = True
    save_point_cloud: bool = True
    save_metadata: bool = True

    def __post_init__(self) -> None:
        """Validate dataset recording configuration values."""
        if not self.sequence_name.strip():
            raise ValueError("Dataset sequence name cannot be empty.")

    @property
    def sequence_path(self) -> Path:
        """Return the full path of the dataset sequence."""
        return self.dataset_root / self.sequence_name

    def enabled_streams(self) -> list[str]:
        """Return the list of streams enabled for recording."""
        enabled_streams = []

        if self.save_left_image:
            enabled_streams.append("left_image")
        if self.save_right_image:
            enabled_streams.append("right_image")
        if self.save_disparity:
            enabled_streams.append("disparity")
        if self.save_point_cloud:
            enabled_streams.append("point_cloud")
        if self.save_metadata:
            enabled_streams.append("metadata")

        return enabled_streams
