"""File-system writer adapter for recorded ZED2i dataset samples.

This module contains infrastructure-level file writing operations used by the
dataset recording application service. It performs concrete disk I/O using
OpenCV, NumPy, and JSON serialization.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np


class DatasetWriterError(RuntimeError):
    """Raised when a dataset file cannot be written."""


class DatasetFileWriter:
    """Low-level file-system writer for dataset sample artifacts.

    This class is an infrastructure adapter. It contains concrete I/O details
    such as directory creation, image writing, NumPy array persistence, and
    metadata serialization.
    """

    def save_image(self, image: np.ndarray, path: Path) -> None:
        """Save an image array to disk.

        Args:
            image: Image array to be written.
            path: Destination image path.

        Raises:
            DatasetWriterError: If the image cannot be saved.
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            success = cv2.imwrite(str(path), image)

            if not success:
                raise DatasetWriterError(
                    f"cv2.imwrite returned False for {path}"
                )
        except (OSError, cv2.error) as exception:
            raise DatasetWriterError(
                f"Failed to save image to {path}: {exception}"
            ) from exception

    def save_array(self, array: np.ndarray, path: Path) -> None:
        """Save a NumPy array to disk.

        Args:
            array: Array to be saved.
            path: Destination ``.npy`` path.

        Raises:
            DatasetWriterError: If the array cannot be saved.
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            np.save(path, array)
        except (OSError, ValueError) as exception:
            raise DatasetWriterError(
                f"Failed to save array to {path}: {exception}"
            ) from exception

    def save_point_cloud_xyz(self, point_cloud_xyz: np.ndarray, path: Path
                             ) -> None:
        """Save an XYZ point cloud as a NumPy array.

        Args:
            point_cloud_xyz: Point cloud array with shape ``(N, 3)``.
            path: Destination ``.npy`` path.
        """
        self.save_array(array=point_cloud_xyz, path=path)

    def save_metadata(self, metadata: dict[str, Any], path: Path) -> None:
        """Save metadata as a JSON file.

        Args:
            metadata: Metadata dictionary.
            path: Destination JSON path.

        Raises:
            DatasetWriterError: If metadata cannot be saved.
        """
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
        except (OSError, TypeError, ValueError) as exception:
            raise DatasetWriterError(
                f"Failed to save metadata to {path}: {exception}"
            ) from exception
