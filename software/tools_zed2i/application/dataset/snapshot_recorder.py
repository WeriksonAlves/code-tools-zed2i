"""Backward-compatible import path for the snapshot dataset recorder."""

from tools_zed2i.application.dataset.services.snapshot_recorder import (
    SnapshotDatasetRecorder,
    SnapshotRecorderError,
)

__all__ = [
    "SnapshotDatasetRecorder",
    "SnapshotRecorderError",
]
