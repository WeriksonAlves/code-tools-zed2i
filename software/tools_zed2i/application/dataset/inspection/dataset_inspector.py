"""Backward-compatible import path for dataset inspection services."""

from tools_zed2i.application.dataset.services.dataset_inspector import (
    DatasetInspectionError,
    DatasetInspector,
)

__all__ = [
    "DatasetInspectionError",
    "DatasetInspector",
]
