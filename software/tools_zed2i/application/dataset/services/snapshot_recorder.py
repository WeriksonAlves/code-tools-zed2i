"""Dataset recording service for converted ZED2i sensor snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from tools_zed2i.application.dataset.models import (
    DatasetLayout,
    SavedSnapshotPaths,
)
from tools_zed2i.application.dataset.models.dataset_config import (
    DatasetRecordingConfig,
)
from tools_zed2i.application.dataset.ports import (
    DatasetManifestRepository,
    DatasetSampleWriter,
)
from tools_zed2i.application.snapshot_converter import (
    ConvertedSensorSnapshot,
    SnapshotConverter,
)
from tools_zed2i.domain.snapshot import SensorSnapshot
from tools_zed2i.infrastructure.dataset import (
    DatasetFileWriter,
    DatasetManifestWriter,
)


class SnapshotRecorderError(RuntimeError):
    """Raised when a sensor snapshot cannot be recorded."""


class SnapshotDatasetRecorder:
    """Application service for recording ZED2i snapshots as dataset samples.

    The recorder orchestrates snapshot conversion, sample file writing,
    metadata generation, and manifest creation. Concrete file-system
    operations are delegated to infrastructure adapters through application
    ports.
    """

    def __init__(
        self,
        config: DatasetRecordingConfig,
        snapshot_converter: SnapshotConverter | None = None,
        file_writer: DatasetSampleWriter | None = None,
        manifest_writer: DatasetManifestRepository | None = None,
    ) -> None:
        """Initialize the dataset recorder.

        Args:
            config: Dataset recording configuration.
            snapshot_converter: Converter used to transform raw snapshot
                payloads into NumPy/OpenCV-compatible structures.
            file_writer: Dataset sample writer adapter.
            manifest_writer: Dataset manifest repository adapter.
        """
        self._config = config
        self._layout = DatasetLayout.from_config(config)
        self._snapshot_converter = snapshot_converter or SnapshotConverter()
        self._file_writer = file_writer or DatasetFileWriter()
        self._manifest_writer = manifest_writer or DatasetManifestWriter()
        self._sample_index = 0

        self._layout.create_directories()
        self._create_manifest()

    @property
    def layout(self) -> DatasetLayout:
        """Return the dataset layout used by this recorder."""
        return self._layout

    def record_snapshot(
        self,
        snapshot: SensorSnapshot,
        sample_id: str | None = None,
    ) -> SavedSnapshotPaths:
        """Record one sensor snapshot to disk.

        Args:
            snapshot: Sensor snapshot to be recorded.
            sample_id: Optional sample identifier. When omitted, a sequential
                six-digit identifier is generated.

        Returns:
            Paths generated for the recorded sample.

        Raises:
            SnapshotRecorderError: If conversion or writing fails.
        """
        resolved_sample_id = sample_id or self._make_sample_id()

        try:
            converted_snapshot = (
                self._snapshot_converter.convert_all_available(
                    snapshot=snapshot,
                )
            )
            saved_paths = self._save_converted_snapshot(
                converted_snapshot=converted_snapshot,
                sample_id=resolved_sample_id,
            )

            if not self._config.save_metadata:
                return saved_paths

            metadata_path = self._save_metadata(
                snapshot=snapshot,
                saved_paths=saved_paths,
                sample_id=resolved_sample_id,
            )

            return SavedSnapshotPaths(
                left_image_path=saved_paths.left_image_path,
                right_image_path=saved_paths.right_image_path,
                disparity_path=saved_paths.disparity_path,
                point_cloud_path=saved_paths.point_cloud_path,
                metadata_path=metadata_path,
            )
        except (RuntimeError, TypeError, ValueError, OSError) as exception:
            raise SnapshotRecorderError(
                f"Failed to record sensor snapshot: {exception}"
            ) from exception

    def _create_manifest(self) -> None:
        """Create and save the dataset manifest."""
        manifest = self._manifest_writer.create_from_recording_config(
            self._config)
        self._manifest_writer.save(manifest)

    def _save_converted_snapshot(
        self,
        converted_snapshot: ConvertedSensorSnapshot,
        sample_id: str,
    ) -> SavedSnapshotPaths:
        """Save converted stream payloads for one sample."""
        left_image_path = self._save_left_image_if_available(
            converted_snapshot=converted_snapshot,
            sample_id=sample_id,
        )
        right_image_path = self._save_right_image_if_available(
            converted_snapshot=converted_snapshot,
            sample_id=sample_id,
        )
        disparity_path = self._save_disparity_if_available(
            converted_snapshot=converted_snapshot,
            sample_id=sample_id,
        )
        point_cloud_path = self._save_point_cloud_if_available(
            converted_snapshot=converted_snapshot,
            sample_id=sample_id,
        )

        return SavedSnapshotPaths(
            left_image_path=left_image_path,
            right_image_path=right_image_path,
            disparity_path=disparity_path,
            point_cloud_path=point_cloud_path,
        )

    def _save_left_image_if_available(
        self,
        converted_snapshot: ConvertedSensorSnapshot,
        sample_id: str,
    ) -> Path | None:
        """Save the left image if enabled and available."""
        if not self._config.save_left_image:
            return None

        if converted_snapshot.left_image is None:
            return None

        output_path = self._layout.left_images_path / f"{sample_id}.png"
        self._file_writer.save_image(
            image=converted_snapshot.left_image,
            path=output_path,
        )

        return output_path

    def _save_right_image_if_available(
        self,
        converted_snapshot: ConvertedSensorSnapshot,
        sample_id: str,
    ) -> Path | None:
        """Save the right image if enabled and available."""
        if not self._config.save_right_image:
            return None

        if converted_snapshot.right_image is None:
            return None

        output_path = self._layout.right_images_path / f"{sample_id}.png"
        self._file_writer.save_image(
            image=converted_snapshot.right_image,
            path=output_path,
        )

        return output_path

    def _save_disparity_if_available(
        self,
        converted_snapshot: ConvertedSensorSnapshot,
        sample_id: str,
    ) -> Path | None:
        """Save the disparity array if enabled and available."""
        if not self._config.save_disparity:
            return None

        if converted_snapshot.disparity is None:
            return None

        output_path = self._layout.disparity_path / f"{sample_id}.npy"
        self._file_writer.save_array(
            array=converted_snapshot.disparity,
            path=output_path,
        )

        return output_path

    def _save_point_cloud_if_available(
        self,
        converted_snapshot: ConvertedSensorSnapshot,
        sample_id: str,
    ) -> Path | None:
        """Save the XYZ point cloud if enabled and available."""
        if not self._config.save_point_cloud:
            return None

        if converted_snapshot.point_cloud_xyz is None:
            return None

        output_path = self._layout.pointclouds_path / f"{sample_id}.npy"
        self._file_writer.save_point_cloud_xyz(
            point_cloud_xyz=converted_snapshot.point_cloud_xyz,
            path=output_path,
        )

        return output_path

    def _save_metadata(
        self,
        snapshot: SensorSnapshot,
        saved_paths: SavedSnapshotPaths,
        sample_id: str,
    ) -> Path:
        """Save metadata for one recorded sample."""
        metadata_path = self._layout.metadata_path / f"{sample_id}.json"

        metadata = {
            "sample_id": sample_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "available_streams": snapshot.available_streams(),
            "saved_files": {
                "left_image": self._path_to_string(
                    saved_paths.left_image_path),
                "right_image": self._path_to_string(
                    saved_paths.right_image_path),
                "disparity": self._path_to_string(saved_paths.disparity_path),
                "point_cloud": self._path_to_string(
                    saved_paths.point_cloud_path),
            },
        }

        self._file_writer.save_metadata(metadata=metadata, path=metadata_path)

        return metadata_path

    def _make_sample_id(self) -> str:
        """Create a sequential six-digit sample identifier."""
        sample_id = f"{self._sample_index:06d}"
        self._sample_index += 1

        return sample_id

    @staticmethod
    def _path_to_string(path: Path | None) -> str | None:
        """Convert an optional path to a string."""
        if path is None:
            return None

        return str(path)
