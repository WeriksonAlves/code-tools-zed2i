from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools_zed2i.application.dataset.dataset_config import DatasetRecordingConfig


class DatasetManifestError(RuntimeError):
    """Raised when a dataset manifest cannot be handled."""


@dataclass(frozen=True)
class DatasetManifest:
    """Manifest describing a recorded ZED2i dataset sequence."""

    manifest_version: str
    sequence_name: str
    created_at: str
    dataset_path: Path
    recording_config: dict[str, Any]
    expected_layout: dict[str, str]
    enabled_streams: list[str]
    inspection_summary: dict[str, Any] | None = None
    notes: dict[str, Any] = field(default_factory=dict)


class DatasetManifestWriter:
    """Writer and updater for dataset manifest files."""

    MANIFEST_FILENAME = "manifest.json"
    MANIFEST_VERSION = "1.0"

    def create_from_recording_config(
        self,
        config: DatasetRecordingConfig,
        notes: dict[str, Any] | None = None,
    ) -> DatasetManifest:
        """Create a dataset manifest from a recording configuration."""
        dataset_path = config.sequence_path

        return DatasetManifest(
            manifest_version=self.MANIFEST_VERSION,
            sequence_name=config.sequence_name,
            created_at=datetime.now(timezone.utc).isoformat(),
            dataset_path=dataset_path,
            recording_config=self._recording_config_to_dict(config),
            expected_layout=self._make_expected_layout(dataset_path),
            enabled_streams=self._get_enabled_streams(config),
            notes=notes or {},
        )

    def save(self, manifest: DatasetManifest, output_path: Path | None = None) -> Path:
        """Save a dataset manifest to disk."""
        resolved_output_path = output_path or (
            manifest.dataset_path / self.MANIFEST_FILENAME
        )

        try:
            resolved_output_path.parent.mkdir(parents=True, exist_ok=True)

            with resolved_output_path.open("w", encoding="utf-8") as file:
                json.dump(
                    self._manifest_to_serializable_dict(manifest),
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            return resolved_output_path
        except OSError as exception:
            raise DatasetManifestError(
                f"Failed to save dataset manifest to {resolved_output_path}: "
                f"{exception}"
            ) from exception

    def load(self, manifest_path: Path) -> DatasetManifest:
        """Load a dataset manifest from disk."""
        try:
            with manifest_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            return DatasetManifest(
                manifest_version=str(data["manifest_version"]),
                sequence_name=str(data["sequence_name"]),
                created_at=str(data["created_at"]),
                dataset_path=Path(data["dataset_path"]),
                recording_config=dict(data["recording_config"]),
                expected_layout=dict(data["expected_layout"]),
                enabled_streams=list(data["enabled_streams"]),
                inspection_summary=data.get("inspection_summary"),
                notes=dict(data.get("notes", {})),
            )
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exception:
            raise DatasetManifestError(
                f"Failed to load dataset manifest from {manifest_path}: {exception}"
            ) from exception

    def attach_inspection_summary(
        self,
        manifest: DatasetManifest,
        inspection_summary: dict[str, Any],
    ) -> DatasetManifest:
        """Return a new manifest with an attached inspection summary."""
        return DatasetManifest(
            manifest_version=manifest.manifest_version,
            sequence_name=manifest.sequence_name,
            created_at=manifest.created_at,
            dataset_path=manifest.dataset_path,
            recording_config=manifest.recording_config,
            expected_layout=manifest.expected_layout,
            enabled_streams=manifest.enabled_streams,
            inspection_summary=inspection_summary,
            notes=manifest.notes,
        )

    def _recording_config_to_dict(
        self,
        config: DatasetRecordingConfig,
    ) -> dict[str, Any]:
        config_dict = asdict(config)
        config_dict["dataset_root"] = str(config.dataset_root)
        config_dict["sequence_path"] = str(config.sequence_path)
        return config_dict

    @staticmethod
    def _make_expected_layout(dataset_path: Path) -> dict[str, str]:
        return {
            "manifest": str(dataset_path / "manifest.json"),
            "left_images": str(dataset_path / "images" / "left"),
            "right_images": str(dataset_path / "images" / "right"),
            "disparity": str(dataset_path / "disparity"),
            "pointclouds": str(dataset_path / "pointclouds"),
            "metadata": str(dataset_path / "metadata"),
            "inspection": str(dataset_path / "inspection"),
        }

    @staticmethod
    def _get_enabled_streams(config: DatasetRecordingConfig) -> list[str]:
        enabled_streams = []

        if config.save_left_image:
            enabled_streams.append("left_image")
        if config.save_right_image:
            enabled_streams.append("right_image")
        if config.save_disparity:
            enabled_streams.append("disparity")
        if config.save_point_cloud:
            enabled_streams.append("point_cloud")
        if config.save_metadata:
            enabled_streams.append("metadata")

        return enabled_streams

    @staticmethod
    def _manifest_to_serializable_dict(
        manifest: DatasetManifest,
    ) -> dict[str, Any]:
        manifest_dict = asdict(manifest)
        manifest_dict["dataset_path"] = str(manifest.dataset_path)
        return manifest_dict