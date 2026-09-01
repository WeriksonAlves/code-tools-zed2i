"""Dataset manifest models.

This module defines immutable models used to describe dataset provenance,
recording configuration, expected layout, enabled streams, and inspection
summary information.

The models in this module do not perform file-system I/O. Concrete persistence
of manifest files should be implemented by infrastructure adapters.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools_zed2i.application.dataset.models.dataset_config import (
    DatasetRecordingConfig,
)

MANIFEST_FILENAME = "manifest.json"
MANIFEST_VERSION = "1.0"


@dataclass(frozen=True)
class DatasetManifest:
    """Manifest describing a recorded ZED2i dataset sequence.

    Attributes:
        manifest_version: Version of the manifest schema.
        sequence_name: Dataset sequence name.
        created_at: UTC timestamp indicating when the manifest was created.
        dataset_path: Path to the dataset sequence.
        recording_config: Serialized recording configuration.
        expected_layout: Expected dataset directory layout.
        enabled_streams: Streams enabled during recording.
        inspection_summary: Optional compact inspection summary.
        notes: Optional user-defined notes.
    """

    manifest_version: str
    sequence_name: str
    created_at: str
    dataset_path: Path
    recording_config: dict[str, Any]
    expected_layout: dict[str, str]
    enabled_streams: list[str]
    inspection_summary: dict[str, Any] | None = None
    notes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_recording_config(
        cls,
        config: DatasetRecordingConfig,
        notes: dict[str, Any] | None = None,
    ) -> DatasetManifest:
        """Create a dataset manifest from a recording configuration.

        Args:
            config: Dataset recording configuration.
            notes: Optional user-defined metadata.

        Returns:
            Manifest initialized from the recording configuration.
        """
        dataset_path = config.sequence_path

        return cls(
            manifest_version=MANIFEST_VERSION,
            sequence_name=config.sequence_name,
            created_at=datetime.now(timezone.utc).isoformat(),
            dataset_path=dataset_path,
            recording_config=recording_config_to_dict(config),
            expected_layout=make_expected_layout(dataset_path),
            enabled_streams=config.enabled_streams(),
            notes=notes or {},
        )

    def with_inspection_summary(
        self,
        inspection_summary: dict[str, Any],
    ) -> DatasetManifest:
        """Return a copy of this manifest with an inspection summary attached.

        Args:
            inspection_summary: Compact inspection summary to attach.

        Returns:
            New manifest instance containing the supplied inspection summary.
        """
        return DatasetManifest(
            manifest_version=self.manifest_version,
            sequence_name=self.sequence_name,
            created_at=self.created_at,
            dataset_path=self.dataset_path,
            recording_config=self.recording_config,
            expected_layout=self.expected_layout,
            enabled_streams=self.enabled_streams,
            inspection_summary=inspection_summary,
            notes=self.notes,
        )

    def to_serializable_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the manifest."""
        manifest_dict = asdict(self)
        manifest_dict["dataset_path"] = str(self.dataset_path)
        return manifest_dict

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> DatasetManifest:
        """Create a manifest from a raw mapping.

        Args:
            data: Raw manifest dictionary.

        Returns:
            Parsed dataset manifest.

        Raises:
            KeyError: If a required field is missing.
            TypeError: If a field has an invalid type.
            ValueError: If a field cannot be converted.
        """
        return cls(
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


def recording_config_to_dict(config: DatasetRecordingConfig) -> dict[str, Any]:
    """Return a JSON-serializable dictionary from a recording configuration."""
    config_dict = asdict(config)
    config_dict["dataset_root"] = str(config.dataset_root)
    config_dict["sequence_path"] = str(config.sequence_path)
    return config_dict


def make_expected_layout(dataset_path: Path) -> dict[str, str]:
    """Return the expected directory layout for a dataset path."""
    return {
        "manifest": str(dataset_path / MANIFEST_FILENAME),
        "left_images": str(dataset_path / "images" / "left"),
        "right_images": str(dataset_path / "images" / "right"),
        "disparity": str(dataset_path / "disparity"),
        "pointclouds": str(dataset_path / "pointclouds"),
        "metadata": str(dataset_path / "metadata"),
        "inspection": str(dataset_path / "inspection"),
        "exports": str(dataset_path / "exports"),
    }
