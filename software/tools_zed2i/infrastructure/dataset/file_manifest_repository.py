"""File-system repository for ZED2i dataset manifests.

This module contains the infrastructure adapter responsible for saving and
loading ``manifest.json`` files. The manifest model itself belongs to the
application model layer; this repository only handles persistence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools_zed2i.application.dataset.models.dataset_config import (
    DatasetRecordingConfig,
)
from tools_zed2i.application.dataset.models.dataset_manifest import (
    MANIFEST_FILENAME,
    DatasetManifest,
)


class DatasetManifestError(RuntimeError):
    """Raised when a dataset manifest cannot be saved or loaded."""


class DatasetManifestWriter:
    """File-system repository for dataset manifest persistence.

    The class name is kept as ``DatasetManifestWriter`` for backward
    compatibility with previous versions of the package, although its role is
    closer to a repository.
    """

    MANIFEST_FILENAME = MANIFEST_FILENAME

    def create_from_recording_config(
        self,
        config: DatasetRecordingConfig,
        notes: dict[str, Any] | None = None,
    ) -> DatasetManifest:
        """Create a manifest from a dataset recording configuration.

        Args:
            config: Dataset recording configuration.
            notes: Optional user-defined metadata.

        Returns:
            Dataset manifest initialized from the recording configuration.
        """
        return DatasetManifest.from_recording_config(
            config=config,
            notes=notes,
        )

    def save(
        self,
        manifest: DatasetManifest,
        output_path: Path | None = None,
    ) -> Path:
        """Save a dataset manifest to disk.

        Args:
            manifest: Dataset manifest to be saved.
            output_path: Optional output path. When omitted, the manifest is
                saved to ``manifest.dataset_path / "manifest.json"``.

        Returns:
            Path to the saved manifest file.

        Raises:
            DatasetManifestError: If the manifest cannot be saved.
        """
        resolved_output_path = output_path or (
            manifest.dataset_path / self.MANIFEST_FILENAME
        )

        try:
            resolved_output_path.parent.mkdir(parents=True, exist_ok=True)

            with resolved_output_path.open("w", encoding="utf-8") as file:
                json.dump(
                    manifest.to_serializable_dict(),
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            return resolved_output_path
        except (OSError, TypeError, ValueError) as exception:
            raise DatasetManifestError(
                f"Failed to save dataset manifest to {resolved_output_path}: "
                f"{exception}"
            ) from exception

    def load(self, manifest_path: Path) -> DatasetManifest:
        """Load a dataset manifest from disk.

        Args:
            manifest_path: Path to the manifest JSON file.

        Returns:
            Loaded dataset manifest.

        Raises:
            DatasetManifestError: If the manifest cannot be loaded or parsed.
        """
        try:
            with manifest_path.open("r", encoding="utf-8") as file:
                raw_manifest = json.load(file)

            if not isinstance(raw_manifest, dict):
                raise TypeError(
                    f"Manifest content must be a JSON object: {manifest_path}"
                )

            return DatasetManifest.from_mapping(raw_manifest)
        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as exception:
            raise DatasetManifestError(
                f"Failed to load dataset manifest from "
                f"{manifest_path}: {exception}"
            ) from exception

    def attach_inspection_summary(
        self,
        manifest: DatasetManifest,
        inspection_summary: dict[str, Any],
    ) -> DatasetManifest:
        """Return a manifest with an attached inspection summary.

        Args:
            manifest: Original dataset manifest.
            inspection_summary: Compact inspection summary dictionary.

        Returns:
            New manifest instance with inspection summary attached.
        """
        return manifest.with_inspection_summary(
            inspection_summary=inspection_summary,
        )
