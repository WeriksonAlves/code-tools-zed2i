"""Dataset application ports.

This module defines application-level contracts used by dataset recording,
inspection, and export services.

Ports represent abstractions required by the application layer. Concrete
implementations must live in infrastructure adapters, such as file-system
writers, manifest repositories, or future cloud/database backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from tools_zed2i.application.dataset.models.dataset_config import (
    DatasetRecordingConfig,
)
from tools_zed2i.application.dataset.models.dataset_manifest import (
    DatasetManifest,
    MANIFEST_FILENAME,
)


class DatasetSampleWriter(ABC):
    """Port for writing dataset sample artifacts.

    Implementations of this port are responsible for persisting converted
    sample artifacts such as images, disparity arrays, point cloud arrays,
    and metadata.

    The payload parameters intentionally use ``Any`` to avoid forcing the
    application layer to depend directly on NumPy or OpenCV types.
    """

    @abstractmethod
    def save_image(self, image: Any, path: Path) -> None:
        """Save an image payload.

        Args:
            image: Image payload to be saved.
            path: Destination path.
        """
        raise NotImplementedError

    @abstractmethod
    def save_array(self, array: Any, path: Path) -> None:
        """Save an array payload.

        Args:
            array: Array payload to be saved.
            path: Destination path.
        """
        raise NotImplementedError

    @abstractmethod
    def save_point_cloud_xyz(self, point_cloud_xyz: Any, path: Path) -> None:
        """Save an XYZ point cloud payload.

        Args:
            point_cloud_xyz: XYZ point cloud payload.
            path: Destination path.
        """
        raise NotImplementedError

    @abstractmethod
    def save_metadata(self, metadata: dict[str, Any], path: Path) -> None:
        """Save sample metadata.

        Args:
            metadata: Metadata dictionary.
            path: Destination path.
        """
        raise NotImplementedError


class DatasetManifestRepository(ABC):
    """Port for dataset manifest persistence.

    Implementations of this port are responsible for creating, saving, loading,
    and updating dataset manifests.
    """

    MANIFEST_FILENAME = MANIFEST_FILENAME

    @abstractmethod
    def create_from_recording_config(
        self,
        config: DatasetRecordingConfig,
        notes: dict[str, Any] | None = None,
    ) -> DatasetManifest:
        """Create a manifest from a dataset recording configuration.

        Args:
            config: Dataset recording configuration.
            notes: Optional user-defined manifest notes.

        Returns:
            Dataset manifest initialized from the recording configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        manifest: DatasetManifest,
        output_path: Path | None = None,
    ) -> Path:
        """Save a dataset manifest.

        Args:
            manifest: Dataset manifest to persist.
            output_path: Optional destination path. When omitted, the
                implementation should save the manifest to the dataset sequence
                root.

        Returns:
            Path to the saved manifest.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self, manifest_path: Path) -> DatasetManifest:
        """Load a dataset manifest.

        Args:
            manifest_path: Path to the manifest file.

        Returns:
            Loaded dataset manifest.
        """
        raise NotImplementedError

    @abstractmethod
    def attach_inspection_summary(
        self,
        manifest: DatasetManifest,
        inspection_summary: dict[str, Any],
    ) -> DatasetManifest:
        """Attach an inspection summary to a manifest.

        Args:
            manifest: Original dataset manifest.
            inspection_summary: Compact inspection summary dictionary.

        Returns:
            Updated dataset manifest.
        """
        raise NotImplementedError
