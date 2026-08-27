from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetRecordingConfig:
    """Configuration for recording ZED2i sensor snapshots."""

    dataset_root: Path
    sequence_name: str
    save_left_image: bool = True
    save_right_image: bool = True
    save_disparity: bool = True
    save_point_cloud: bool = True
    save_metadata: bool = True

    @property
    def sequence_path(self) -> Path:
        return self.dataset_root / self.sequence_name
