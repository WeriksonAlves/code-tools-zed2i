from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools_zed2i.application.dataset.dataset_config import DatasetRecordingConfig
from tools_zed2i.application.dataset.dataset_layout import DatasetLayout
from tools_zed2i.application.dataset.dataset_manifest import DatasetManifestWriter
from tools_zed2i.application.dataset.dataset_writer import (
    DatasetFileWriter,
    SavedSnapshotPaths,
)
from tools_zed2i.application.snapshot_converter import SnapshotConverter
from tools_zed2i.domain.snapshot import SensorSnapshot


class SnapshotRecorderError(RuntimeError):
    """Raised when a sensor snapshot cannot be recorded."""


class SnapshotDatasetRecorder:
    """Recorder for saving ZED2i sensor snapshots as dataset samples."""

    def __init__(
        self,
        config: DatasetRecordingConfig,
        snapshot_converter: SnapshotConverter | None = None,
        file_writer: DatasetFileWriter | None = None,
        manifest_writer: DatasetManifestWriter | None = None,
    ) -> None:
        self._config = config
        self._layout = DatasetLayout.from_config(config)
        self._snapshot_converter = snapshot_converter or SnapshotConverter()
        self._file_writer = file_writer or DatasetFileWriter()
        self._manifest_writer = manifest_writer or DatasetManifestWriter()
        self._sample_index = 0

        self._layout.create_directories()
        self._create_manifest()

    def _create_manifest(self) -> None:
        manifest = self._manifest_writer.create_from_recording_config(self._config)
        self._manifest_writer.save(manifest)

    @property
    def layout(self) -> DatasetLayout:
        return self._layout

    def record_snapshot(
        self,
        snapshot: SensorSnapshot,
        sample_id: str | None = None,
    ) -> SavedSnapshotPaths:
        """Record one sensor snapshot to disk."""
        resolved_sample_id = sample_id or self._make_sample_id()

        try:
            converted_snapshot = self._snapshot_converter.convert_all_available(
                snapshot=snapshot,
            )

            saved_paths = self._save_converted_snapshot(
                converted_snapshot=converted_snapshot,
                sample_id=resolved_sample_id,
            )

            if self._config.save_metadata:
                metadata_path = self._save_metadata(
                    snapshot=snapshot,
                    saved_paths=saved_paths,
                    sample_id=resolved_sample_id,
                )
                saved_paths = SavedSnapshotPaths(
                    left_image_path=saved_paths.left_image_path,
                    right_image_path=saved_paths.right_image_path,
                    disparity_path=saved_paths.disparity_path,
                    point_cloud_path=saved_paths.point_cloud_path,
                    metadata_path=metadata_path,
                )

            return saved_paths
        except Exception as exception:
            raise SnapshotRecorderError(
                f"Failed to record sensor snapshot: {exception}"
            ) from exception

    def _save_converted_snapshot(
        self,
        converted_snapshot: Any,
        sample_id: str,
    ) -> SavedSnapshotPaths:
        left_image_path = None
        right_image_path = None
        disparity_path = None
        point_cloud_path = None

        if self._config.save_left_image and converted_snapshot.left_image is not None:
            left_image_path = self._layout.left_images_path / f"{sample_id}.png"
            self._file_writer.save_image(
                image=converted_snapshot.left_image,
                path=left_image_path,
            )

        if self._config.save_right_image and converted_snapshot.right_image is not None:
            right_image_path = self._layout.right_images_path / f"{sample_id}.png"
            self._file_writer.save_image(
                image=converted_snapshot.right_image,
                path=right_image_path,
            )

        if self._config.save_disparity and converted_snapshot.disparity is not None:
            disparity_path = self._layout.disparity_path / f"{sample_id}.npy"
            self._file_writer.save_array(
                array=converted_snapshot.disparity,
                path=disparity_path,
            )

        if (
            self._config.save_point_cloud
            and converted_snapshot.point_cloud_xyz is not None
        ):
            point_cloud_path = self._layout.pointclouds_path / f"{sample_id}.npy"
            self._file_writer.save_point_cloud_xyz(
                point_cloud_xyz=converted_snapshot.point_cloud_xyz,
                path=point_cloud_path,
            )

        return SavedSnapshotPaths(
            left_image_path=left_image_path,
            right_image_path=right_image_path,
            disparity_path=disparity_path,
            point_cloud_path=point_cloud_path,
        )

    def _save_metadata(
        self,
        snapshot: SensorSnapshot,
        saved_paths: SavedSnapshotPaths,
        sample_id: str,
    ) -> Path:
        metadata_path = self._layout.metadata_path / f"{sample_id}.json"

        metadata = {
            "sample_id": sample_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "available_streams": snapshot.available_streams(),
            "saved_files": {
                "left_image": self._path_to_string(saved_paths.left_image_path),
                "right_image": self._path_to_string(saved_paths.right_image_path),
                "disparity": self._path_to_string(saved_paths.disparity_path),
                "point_cloud": self._path_to_string(saved_paths.point_cloud_path),
            },
        }

        self._file_writer.save_metadata(metadata=metadata, path=metadata_path)

        return metadata_path

    def _make_sample_id(self) -> str:
        sample_id = f"{self._sample_index:06d}"
        self._sample_index += 1
        return sample_id

    @staticmethod
    def _path_to_string(path: Path | None) -> str | None:
        if path is None:
            return None

        return str(path)
