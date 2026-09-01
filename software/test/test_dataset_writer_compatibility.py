from tools_zed2i.application.dataset.dataset_writer import (
    DatasetFileWriter as CompatibilityDatasetFileWriter,
)
from tools_zed2i.application.dataset.dataset_writer import (
    DatasetWriterError as CompatibilityDatasetWriterError,
)
from tools_zed2i.application.dataset.dataset_writer import (
    SavedSnapshotPaths as CompatibilitySavedSnapshotPaths,
)
from tools_zed2i.infrastructure.dataset.file_dataset_writer import (
    DatasetFileWriter,
    DatasetWriterError,
    SavedSnapshotPaths,
)


def test_dataset_writer_compatibility_imports() -> None:
    assert CompatibilityDatasetFileWriter is DatasetFileWriter
    assert CompatibilityDatasetWriterError is DatasetWriterError
    assert CompatibilitySavedSnapshotPaths is SavedSnapshotPaths
