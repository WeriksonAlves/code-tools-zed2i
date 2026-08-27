from __future__ import annotations

from pathlib import Path

from tools_zed2i.application.dataset import DatasetRecordingConfig
from tools_zed2i.infrastructure.dataset import (
    DatasetManifestWriter,
)


def test_dataset_manifest_writer_creates_manifest_from_recording_config(
    tmp_path: Path,
) -> None:
    config = DatasetRecordingConfig(
        dataset_root=tmp_path,
        sequence_name="sequence_test",
        save_left_image=True,
        save_right_image=False,
        save_disparity=True,
        save_point_cloud=True,
        save_metadata=True,
    )

    writer = DatasetManifestWriter()

    manifest = writer.create_from_recording_config(config)

    assert manifest.manifest_version == "1.0"
    assert manifest.sequence_name == "sequence_test"
    assert manifest.dataset_path == tmp_path / "sequence_test"
    assert manifest.recording_config["sequence_name"] == "sequence_test"
    assert manifest.recording_config["dataset_root"] == str(tmp_path)
    assert "left_image" in manifest.enabled_streams
    assert "right_image" not in manifest.enabled_streams
    assert "disparity" in manifest.enabled_streams
    assert "point_cloud" in manifest.enabled_streams
    assert "metadata" in manifest.enabled_streams


def test_dataset_manifest_writer_saves_and_loads_manifest(tmp_path: Path
                                                          ) -> None:
    config = DatasetRecordingConfig(
        dataset_root=tmp_path,
        sequence_name="sequence_test",
    )

    writer = DatasetManifestWriter()
    manifest = writer.create_from_recording_config(config)

    manifest_path = writer.save(manifest)

    assert manifest_path.exists()

    loaded_manifest = writer.load(manifest_path)

    assert loaded_manifest.manifest_version == manifest.manifest_version
    assert loaded_manifest.sequence_name == manifest.sequence_name
    assert loaded_manifest.dataset_path == manifest.dataset_path
    assert loaded_manifest.enabled_streams == manifest.enabled_streams


def test_dataset_manifest_writer_attaches_inspection_summary(
    tmp_path: Path,
) -> None:
    config = DatasetRecordingConfig(
        dataset_root=tmp_path,
        sequence_name="sequence_test",
    )

    writer = DatasetManifestWriter()
    manifest = writer.create_from_recording_config(config)

    updated_manifest = writer.attach_inspection_summary(
        manifest=manifest,
        inspection_summary={
            "total_samples": 10,
            "complete_samples": 10,
            "incomplete_samples": 0,
        },
    )

    assert updated_manifest.inspection_summary is not None
    assert updated_manifest.inspection_summary["total_samples"] == 10
    assert updated_manifest.inspection_summary["complete_samples"] == 10
    assert updated_manifest.inspection_summary["incomplete_samples"] == 0
