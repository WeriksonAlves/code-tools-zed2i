from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools_zed2i.application.pointcloud_processor import (
    Open3DPointCloudProcessor,
    PlaneSegmentationResult,
)
from tools_zed2i.domain.snapshot import SensorSnapshot
from tools_zed2i.infrastructure.converters.open3d_converter import Open3DConverter


class MappingPipelineError(RuntimeError):
    """Raised when the mapping preprocessing pipeline fails."""


@dataclass(frozen=True)
class MappingPreprocessingConfig:
    """Configuration for point cloud preprocessing in mapping experiments."""

    voxel_size: float = 0.05
    nb_neighbors: int = 30
    std_ratio: float = 2.0
    enable_plane_segmentation: bool = False
    plane_distance_threshold: float = 0.05
    plane_ransac_n: int = 3
    plane_num_iterations: int = 1000


@dataclass(frozen=True)
class MappingPreprocessingResult:
    """Result produced by the mapping preprocessing pipeline."""

    raw_cloud: Any
    preprocessed_cloud: Any
    plane_segmentation: PlaneSegmentationResult | None = None

    def has_plane_segmentation(self) -> bool:
        return self.plane_segmentation is not None


class MappingPreprocessingPipeline:
    """Pipeline for converting and preprocessing ZED2i point clouds."""

    def __init__(
        self,
        open3d_converter: Any | None = None,
        pointcloud_processor: Open3DPointCloudProcessor | None = None,
    ) -> None:
        self._open3d_converter = open3d_converter or Open3DConverter()
        self._pointcloud_processor = (
            pointcloud_processor or Open3DPointCloudProcessor()
        )

    def run_from_snapshot(
        self,
        snapshot: SensorSnapshot,
        config: MappingPreprocessingConfig | None = None,
    ) -> MappingPreprocessingResult:
        """Run the preprocessing pipeline from a sensor snapshot."""
        if snapshot.point_cloud is None:
            raise MappingPipelineError(
                "Sensor snapshot does not contain a point cloud message."
            )

        return self.run_from_pointcloud_message(
            pointcloud_message=snapshot.point_cloud,
            config=config,
        )

    def run_from_pointcloud_message(
        self,
        pointcloud_message: Any,
        config: MappingPreprocessingConfig | None = None,
    ) -> MappingPreprocessingResult:
        """Run the preprocessing pipeline from a ROS PointCloud2 message."""
        pipeline_config = config or MappingPreprocessingConfig()

        try:
            raw_cloud = self._open3d_converter.pointcloud_message_to_open3d(
                pointcloud_message
            )
            return self.run_from_open3d_cloud(
                point_cloud=raw_cloud,
                config=pipeline_config,
            )
        except Exception as exception:
            raise MappingPipelineError(
                f"Failed to run mapping pipeline from PointCloud2 message: {exception}"
            ) from exception

    def run_from_open3d_cloud(
        self,
        point_cloud: Any,
        config: MappingPreprocessingConfig | None = None,
    ) -> MappingPreprocessingResult:
        """Run the preprocessing pipeline from an Open3D point cloud."""
        pipeline_config = config or MappingPreprocessingConfig()

        try:
            preprocessed_cloud = self._pointcloud_processor.preprocess_for_mapping(
                point_cloud=point_cloud,
                voxel_size=pipeline_config.voxel_size,
                nb_neighbors=pipeline_config.nb_neighbors,
                std_ratio=pipeline_config.std_ratio,
            )

            plane_segmentation = None
            if pipeline_config.enable_plane_segmentation:
                plane_segmentation = self._pointcloud_processor.segment_plane(
                    point_cloud=preprocessed_cloud,
                    distance_threshold=pipeline_config.plane_distance_threshold,
                    ransac_n=pipeline_config.plane_ransac_n,
                    num_iterations=pipeline_config.plane_num_iterations,
                )

            return MappingPreprocessingResult(
                raw_cloud=point_cloud,
                preprocessed_cloud=preprocessed_cloud,
                plane_segmentation=plane_segmentation,
            )
        except Exception as exception:
            raise MappingPipelineError(
                f"Failed to run mapping preprocessing pipeline: {exception}"
            ) from exception
