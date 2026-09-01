"""Application layer for the tools_zed2i package.

This package contains use-case services, conversion orchestration, dataset
operations, point cloud processing utilities, and mapping preprocessing
pipelines.

Import concrete services from their submodules to avoid eager imports and
circular dependencies.

Examples:
    from tools_zed2i.application.dataset.services import DatasetExporter
    from tools_zed2i.application.mapping import MappingPreprocessingPipeline
    from tools_zed2i.application.pointcloud import Open3DPointCloudProcessor
"""

__all__: list[str] = []
