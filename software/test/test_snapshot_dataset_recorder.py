from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from tools_zed2i.application.dataset.models.dataset_config import DatasetRecordingConfig
from tools_zed2i.application.dataset.services.snapshot_recorder import (
    SavedSnapshotPaths,
    SnapshotDatasetRecorder,
)
from tools_zed2i.application.snapshot_converter import ConvertedSensorSnapshot
from tools_zed2i.domain.snapshot import SensorSnapshot


class FakeSnapshotConverter:
    def convert_all_available(self, snapshot: SensorSnapshot
                              ) -> ConvertedSensorSnapshot:
        return ConvertedSensorSnapshot(
            left_image=np.zeros((2, 2, 3), dtype=np.uint8)
            if snapshot.left_image is not None
            else None,
            right_image=np.ones((2, 2, 3), dtype=np.uint8)
            if snapshot.right_image is not None
            else None,
            disparity=np.ones((2, 2), dtype=np.float32)
            if snapshot.disparity is not None
            else None,
            point_cloud_xyz=np.ones((3, 3), dtype=np.float32)
            if snapshot.point_cloud is not None
            else None,
        )


class FakeDatasetFileWriter:
    def __init__(self) -> None:
        self.saved_images: list[Path] = []
        self.saved_arrays: list[Path] = []
        self.saved_point_clouds: list[Path] = []
        self.saved_metadata: list[Path] = []

    def save_image(self, image: np.ndarray, path: Path) -> None:
        self.saved_images.append(path)

    def save_array(self, array: np.ndarray, path: Path) -> None:
        self.saved_arrays.append(path)

    def save_point_cloud_xyz(self, point_cloud_xyz: np.ndarray, path: Path
                             ) -> None:
        self.saved_point_clouds.append(path)

    def save_metadata(self, metadata: dict[str, Any], path: Path) -> None:
        self.saved_metadata.append(path)


class FakeDatasetManifestWriter:
    def __init__(self) -> None:
        self.saved_manifest_count = 0

    def create_from_recording_config(self, config: object) -> object:
        return object()

    def save(self, manifest: object, output_path: object | None = None
             ) -> Path:
        del manifest
        del output_path

        self.saved_manifest_count += 1
        return Path("manifest.json")


def test_snapshot_dataset_recorder_creates_dataset_layout(tmp_path: Path
                                                          ) -> None:
    config = DatasetRecordingConfig(
        dataset_root=tmp_path,
        sequence_name="sequence_test",
    )

    recorder = SnapshotDatasetRecorder(
        config=config,
        snapshot_converter=FakeSnapshotConverter(),
        file_writer=FakeDatasetFileWriter(),
        manifest_writer=FakeDatasetManifestWriter(),
    )

    assert recorder.layout.sequence_path.exists()
    assert recorder.layout.left_images_path.exists()
    assert recorder.layout.right_images_path.exists()
    assert recorder.layout.disparity_path.exists()
    assert recorder.layout.pointclouds_path.exists()
    assert recorder.layout.metadata_path.exists()


def test_snapshot_dataset_recorder_saves_available_streams(tmp_path: Path
                                                           ) -> None:
    writer = FakeDatasetFileWriter()

    config = DatasetRecordingConfig(
        dataset_root=tmp_path,
        sequence_name="sequence_test",
    )

    recorder = SnapshotDatasetRecorder(
        config=config,
        snapshot_converter=FakeSnapshotConverter(),
        file_writer=writer,
        manifest_writer=FakeDatasetManifestWriter(),
    )

    snapshot = SensorSnapshot(
        left_image="left",
        right_image="right",
        disparity="disparity",
        point_cloud="point_cloud",
    )

    saved_paths = recorder.record_snapshot(snapshot, sample_id="sample_001")

    assert saved_paths.left_image_path is not None
    assert saved_paths.right_image_path is not None
    assert saved_paths.disparity_path is not None
    assert saved_paths.point_cloud_path is not None
    assert saved_paths.metadata_path is not None

    assert writer.saved_images == [
        tmp_path / "sequence_test" / "images" / "left" / "sample_001.png",
        tmp_path / "sequence_test" / "images" / "right" / "sample_001.png",
    ]
    assert writer.saved_arrays == [
        tmp_path / "sequence_test" / "disparity" / "sample_001.npy",
    ]
    assert writer.saved_point_clouds == [
        tmp_path / "sequence_test" / "pointclouds" / "sample_001.npy",
    ]
    assert writer.saved_metadata == [
        tmp_path / "sequence_test" / "metadata" / "sample_001.json",
    ]


def test_snapshot_dataset_recorder_respects_disabled_streams(tmp_path: Path
                                                             ) -> None:
    writer = FakeDatasetFileWriter()

    config = DatasetRecordingConfig(
        dataset_root=tmp_path,
        sequence_name="sequence_test",
        save_left_image=False,
        save_right_image=False,
        save_disparity=False,
        save_point_cloud=True,
        save_metadata=True,
    )

    recorder = SnapshotDatasetRecorder(
        config=config,
        snapshot_converter=FakeSnapshotConverter(),
        file_writer=writer,
        manifest_writer=FakeDatasetManifestWriter(),
    )

    snapshot = SensorSnapshot(
        left_image="left",
        right_image="right",
        disparity="disparity",
        point_cloud="point_cloud",
    )

    saved_paths = recorder.record_snapshot(snapshot, sample_id="sample_001")

    assert saved_paths.left_image_path is None
    assert saved_paths.right_image_path is None
    assert saved_paths.disparity_path is None
    assert saved_paths.point_cloud_path is not None
    assert saved_paths.metadata_path is not None

    assert writer.saved_images == []
    assert writer.saved_arrays == []
    assert writer.saved_point_clouds == [
        tmp_path / "sequence_test" / "pointclouds" / "sample_001.npy",
    ]
    assert writer.saved_metadata == [
        tmp_path / "sequence_test" / "metadata" / "sample_001.json",
    ]


def test_snapshot_dataset_recorder_auto_increments_sample_id(tmp_path: Path
                                                             ) -> None:
    writer = FakeDatasetFileWriter()

    config = DatasetRecordingConfig(
        dataset_root=tmp_path,
        sequence_name="sequence_test",
    )

    recorder = SnapshotDatasetRecorder(
        config=config,
        snapshot_converter=FakeSnapshotConverter(),
        file_writer=writer,
        manifest_writer=FakeDatasetManifestWriter(),
    )

    snapshot = SensorSnapshot(left_image="left")

    first_paths = recorder.record_snapshot(snapshot)
    second_paths = recorder.record_snapshot(snapshot)

    assert first_paths.left_image_path is not None
    assert second_paths.left_image_path is not None

    assert first_paths.left_image_path.name == "000000.png"
    assert second_paths.left_image_path.name == "000001.png"


def test_saved_snapshot_paths_can_be_empty() -> None:
    saved_paths = SavedSnapshotPaths()

    assert saved_paths.left_image_path is None
    assert saved_paths.right_image_path is None
    assert saved_paths.disparity_path is None
    assert saved_paths.point_cloud_path is None
    assert saved_paths.metadata_path is None


def test_snapshot_dataset_recorder_creates_manifest(tmp_path: Path) -> None:
    manifest_writer = FakeDatasetManifestWriter()

    config = DatasetRecordingConfig(
        dataset_root=tmp_path,
        sequence_name="sequence_test",
    )

    SnapshotDatasetRecorder(
        config=config,
        snapshot_converter=FakeSnapshotConverter(),
        file_writer=FakeDatasetFileWriter(),
        manifest_writer=manifest_writer,
    )

    assert manifest_writer.saved_manifest_count == 1
