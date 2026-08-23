from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


class DatasetWriterError(RuntimeError):
    """Raised when a dataset file cannot be written."""


@dataclass(frozen=True)
class SavedSnapshotPaths:
    """Paths generated for one recorded sensor snapshot."""

    left_image_path: Path | None = None
    right_image_path: Path | None = None
    disparity_path: Path | None = None
    point_cloud_path: Path | None = None
    metadata_path: Path | None = None


class DatasetFileWriter:
    """Low-level writer for dataset files."""

    def save_image(self, image: np.ndarray, path: Path) -> None:
        """Save an image array to disk."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            success = cv2.imwrite(str(path), image)

            if not success:
                raise DatasetWriterError(f"cv2.imwrite returned False for {path}")
        except Exception as exception:
            raise DatasetWriterError(
                f"Failed to save image to {path}: {exception}"
            ) from exception

    def save_array(self, array: np.ndarray, path: Path) -> None:
        """Save a NumPy array to disk."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            np.save(path, array)
        except Exception as exception:
            raise DatasetWriterError(
                f"Failed to save array to {path}: {exception}"
            ) from exception

    def save_point_cloud_xyz(self, point_cloud_xyz: np.ndarray, path: Path) -> None:
        """Save an XYZ point cloud as a NumPy array."""
        self.save_array(point_cloud_xyz, path)

    def save_metadata(self, metadata: dict[str, Any], path: Path) -> None:
        """Save metadata as a JSON file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as file:
                json.dump(
                    metadata,
                    file,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )
        except Exception as exception:
            raise DatasetWriterError(
                f"Failed to save metadata to {path}: {exception}"
            ) from exception

