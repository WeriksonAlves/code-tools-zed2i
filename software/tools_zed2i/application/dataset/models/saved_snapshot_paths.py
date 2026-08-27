"""Models describing files generated from recorded sensor snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SavedSnapshotPaths:
    """Paths generated for one recorded sensor snapshot.

    Attributes:
        left_image_path: Path to the saved left image, when available.
        right_image_path: Path to the saved right image, when available.
        disparity_path: Path to the saved disparity array, when available.
        point_cloud_path: Path to the saved point cloud array, when available.
        metadata_path: Path to the saved metadata file, when available.
    """

    left_image_path: Path | None = None
    right_image_path: Path | None = None
    disparity_path: Path | None = None
    point_cloud_path: Path | None = None
    metadata_path: Path | None = None

    def as_dict(self) -> dict[str, Path | None]:
        """Return saved paths indexed by logical file type."""
        return {
            "left_image_path": self.left_image_path,
            "right_image_path": self.right_image_path,
            "disparity_path": self.disparity_path,
            "point_cloud_path": self.point_cloud_path,
            "metadata_path": self.metadata_path,
        }

    def available_paths(self) -> dict[str, Path]:
        """Return only paths that were generated."""
        return {
            name: path
            for name, path in self.as_dict().items()
            if path is not None
        }

    def is_empty(self) -> bool:
        """Return whether no files were generated for the snapshot."""
        return not self.available_paths()
