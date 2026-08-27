"""Dataset application layer for ZED2i recording, inspection, and export.

This package contains dataset-related models, ports, reports, and services used
to record, inspect, describe, and export ZED2i datasets.

The application layer coordinates use cases and depends on abstractions.
Concrete file-system operations should be implemented by infrastructure
adapters.
"""

from tools_zed2i.application.dataset.models.dataset_config import (
    DatasetRecordingConfig,
)
from tools_zed2i.application.dataset.models.dataset_layout import DatasetLayout
from tools_zed2i.application.dataset.models.dataset_manifest import (
    DatasetManifest,
)
from tools_zed2i.application.dataset.models.inspection_result import (
    DatasetInspectionSummary,
    DatasetSampleInspection,
)
from tools_zed2i.application.dataset.models.saved_snapshot_paths import (
    SavedSnapshotPaths,
)
from tools_zed2i.application.dataset.ports import (
    DatasetManifestRepository,
    DatasetSampleWriter,
)
from tools_zed2i.application.dataset.reports.inspection_report import (
    DatasetInspectionReportWriter,
)
from tools_zed2i.application.dataset.services.dataset_exporter import (
    DatasetExporter,
    DatasetExportError,
)
from tools_zed2i.application.dataset.services.dataset_inspector import (
    DatasetInspectionError,
    DatasetInspector,
)
from tools_zed2i.application.dataset.services.snapshot_recorder import (
    SnapshotDatasetRecorder,
    SnapshotRecorderError,
)

__all__ = [
    "DatasetExportError",
    "DatasetExporter",
    "DatasetInspectionError",
    "DatasetInspectionReportWriter",
    "DatasetInspectionSummary",
    "DatasetInspector",
    "DatasetLayout",
    "DatasetManifest",
    "DatasetManifestRepository",
    "DatasetRecordingConfig",
    "DatasetSampleInspection",
    "DatasetSampleWriter",
    "SavedSnapshotPaths",
    "SnapshotDatasetRecorder",
    "SnapshotRecorderError",
]
