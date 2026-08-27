"""Backward-compatible import path for dataset file writing components."""

from tools_zed2i.application.dataset.models.saved_snapshot_paths import (
    DatasetFileWriter,
    DatasetWriterError,
    SavedSnapshotPaths,
)

# from tools_zed2i.infrastructure.dataset.file_dataset_writer import (
#     DatasetFileWriter,
#     DatasetWriterError,
# )

__all__ = [
    "DatasetFileWriter",
    "DatasetWriterError",
    "SavedSnapshotPaths",
]
