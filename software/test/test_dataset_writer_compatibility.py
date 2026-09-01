from tools_zed2i.application.dataset.models import SavedSnapshotPaths
from tools_zed2i.infrastructure.dataset.file_dataset_writer import (
    DatasetFileWriter,
    DatasetWriterError,
)


def test_dataset_writer_compatibility_imports() -> None:
    assert DatasetFileWriter is not None
    assert DatasetWriterError is not None
    assert SavedSnapshotPaths is not None
