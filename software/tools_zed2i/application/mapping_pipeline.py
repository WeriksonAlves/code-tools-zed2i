"""Mapping preprocessing pipeline for ZED2i point clouds."""

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
    """Configuration for point cloud preprocessing in mapping experiments.

    Attributes:
        voxel_size: Voxel size used for downsampling.
        nb_neighbors: Number of neighbors used by statistical outlier removal.
        std_ratio: Standard deviation ratio threshold.
        enable_plane_segmentation: Whether to segment the dominant plane.
        plane_distance_threshold: RANSAC plane distance threshold.
        plane_ransac_n: Number of points sampled per RANSAC iteration.
        plane_num_iterations: Number of RANSAC iterations.
    """

    voxel_size: float = 0.05
    nb_neighbors: int = 30
    std_ratio: float = 2.0
    enable_plane_segmentation: bool = False
    plane_distance_threshold: float = 0.05
    plane_ransac_n: int = 3
    plane_num_iterations: int = 1000

    def __post_init__(self) -> None:
        """Validate preprocessing configuration values."""
        self._validate_positive_value(self.voxel_size, "voxel_size")
        self._validate_positive_integer(self.nb_neighbors, "nb_neighbors")
        self._validate_positive_value(self.std_ratio, "std_ratio")
        self._validate_positive_value(
            self.plane_distance_threshold,
            "plane_distance_threshold",
        )
        self._validate_positive_integer(self.plane_ransac_n, "plane_ransac_n")
        self._validate_positive_integer(
            self.plane_num_iterations,
            "plane_num_iterations",
        )

    @staticmethod
    def _validate_positive_value(value: float, name: str) -> None:
        """Validate that a numeric value is greater than zero."""
        if value <= 0.0:
            raise MappingPipelineError(f"{name} must be greater than zero.")

    @staticmethod
    def _validate_positive_integer(value: int, name: str) -> None:
        """Validate that an integer value is greater than zero."""
        if value <= 0:
            raise MappingPipelineError(f"{name} must be greater than zero.")


@dataclass(frozen=True)
class MappingPreprocessingResult:
    """Result produced by the mapping preprocessing pipeline.

    Attributes:
        raw_cloud: Open3D point cloud before preprocessing.
        preprocessed_cloud: Open3D point cloud after preprocessing.
        plane_segmentation: Optional dominant-plane segmentation result.
    """

    raw_cloud: Any
    preprocessed_cloud: Any
    plane_segmentation: PlaneSegmentationResult | None = None

    def has_plane_segmentation(self) -> bool:
        """Return whether plane segmentation was computed."""
        return self.plane_segmentation is not None


class MappingPreprocessingPipeline:
    """Pipeline for converting and preprocessing ZED2i point clouds.

    The pipeline supports three entry points:

    - from a ``SensorSnapshot``;
    - from a ROS ``PointCloud2``-like message;
    - from an Open3D-compatible point cloud.

    This class orchestrates conversion and point cloud processing. Concrete
    Open3D conversion is delegated to the converter adapter.
    """

    def __init__(
        self,
        open3d_converter: Any | None = None,
        pointcloud_processor: Open3DPointCloudProcessor | None = None,
    ) -> None:
        """Initialize the preprocessing pipeline.

        Args:
            open3d_converter: Converter from point cloud messages to Open3D.
            pointcloud_processor: Processor for Open3D point clouds.
        """
        self._open3d_converter = open3d_converter or Open3DConverter()
        self._pointcloud_processor = (
            pointcloud_processor or Open3DPointCloudProcessor()
        )

    def run_from_snapshot(
        self,
        snapshot: SensorSnapshot,
        config: MappingPreprocessingConfig | None = None,
    ) -> MappingPreprocessingResult:
        """Run preprocessing from a sensor snapshot.

        Args:
            snapshot: Sensor snapshot containing a point cloud payload.
            config: Optional preprocessing configuration.

        Returns:
            Mapping preprocessing result.

        Raises:
            MappingPipelineError: If the snapshot has no point cloud.
        """
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
        """Run preprocessing from a ROS PointCloud2-like message.

        Args:
            pointcloud_message: PointCloud2-compatible message.
            config: Optional preprocessing configuration.

        Returns:
            Mapping preprocessing result.

        Raises:
            MappingPipelineError: If conversion or preprocessing fails.
        """
        pipeline_config = config or MappingPreprocessingConfig()

        try:
            raw_cloud = self._open3d_converter.pointcloud_message_to_open3d(
                pointcloud_message,
            )
            return self.run_from_open3d_cloud(
                point_cloud=raw_cloud,
                config=pipeline_config,
            )
        except (RuntimeError, TypeError, ValueError, AttributeError
                ) as exception:
            raise MappingPipelineError(
                "Failed to run mapping pipeline from PointCloud2 message: "
                f"{exception}"
            ) from exception

    def run_from_open3d_cloud(
        self,
        point_cloud: Any,
        config: MappingPreprocessingConfig | None = None,
    ) -> MappingPreprocessingResult:
        """Run preprocessing from an Open3D-compatible point cloud.

        Args:
            point_cloud: Open3D-compatible input point cloud.
            config: Optional preprocessing configuration.

        Returns:
            Mapping preprocessing result.

        Raises:
            MappingPipelineError: If preprocessing fails.
        """
        pipeline_config = config or MappingPreprocessingConfig()

        try:
            preprocessed_cloud = ...
            self._pointcloud_processor.preprocess_for_mapping(
                point_cloud=point_cloud,
                voxel_size=pipeline_config.voxel_size,
                nb_neighbors=pipeline_config.nb_neighbors,
                std_ratio=pipeline_config.std_ratio,
            )

            plane_segmentation = self._segment_plane_if_enabled(
                point_cloud=preprocessed_cloud,
                config=pipeline_config,
            )

            return MappingPreprocessingResult(
                raw_cloud=point_cloud,
                preprocessed_cloud=preprocessed_cloud,
                plane_segmentation=plane_segmentation,
            )
        except (RuntimeError, TypeError, ValueError, AttributeError
                ) as exception:
            raise MappingPipelineError(
                f"Failed to run mapping preprocessing pipeline: {exception}"
            ) from exception

    def _segment_plane_if_enabled(
        self,
        point_cloud: Any,
        config: MappingPreprocessingConfig,
    ) -> PlaneSegmentationResult | None:
        """Segment the dominant plane when enabled by configuration."""
        if not config.enable_plane_segmentation:
            return None

        return self._pointcloud_processor.segment_plane(
            point_cloud=point_cloud,
            distance_threshold=config.plane_distance_threshold,
            ransac_n=config.plane_ransac_n,
            num_iterations=config.plane_num_iterations,
        )
