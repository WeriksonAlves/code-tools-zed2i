"""Application layer for the tools_zed2i package.

This package contains use-case services, conversion orchestration, dataset
operations, point cloud processing utilities, and mapping preprocessing
pipelines.

The application layer should coordinate workflows and depend on abstractions
whenever possible. Concrete adapters for ROS 2, OpenCV, Open3D, file-system I/O,
and other external technologies should live in the infrastructure layer.
"""

from tools_zed2i.application.mapping_pipeline import (
    MappingPipelineError,
    MappingPreprocessingConfig,
    MappingPreprocessingPipeline,
    MappingPreprocessingResult,
)
from tools_zed2i.application.pointcloud_processor import (
    Open3DPointCloudProcessor,
    PlaneSegmentationResult,
    PointCloudProcessingError,
)
from tools_zed2i.application.snapshot_converter import (
    ConvertedSensorSnapshot,
    SnapshotConverter,
)
from tools_zed2i.application.zed2i_service import Zed2iService

__all__ = [
    "ConvertedSensorSnapshot",
    "MappingPipelineError",
    "MappingPreprocessingConfig",
    "MappingPreprocessingPipeline",
    "MappingPreprocessingResult",
    "Open3DPointCloudProcessor",
    "PlaneSegmentationResult",
    "PointCloudProcessingError",
    "SnapshotConverter",
    "Zed2iService",
]
