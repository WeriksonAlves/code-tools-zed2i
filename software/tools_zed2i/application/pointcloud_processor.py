from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class PointCloudProcessingError(RuntimeError):
    """Raised when an Open3D point cloud processing operation fails."""


@dataclass(frozen=True)
class PlaneSegmentationResult:
    """Result of a plane segmentation operation."""

    plane_model: tuple[float, float, float, float]
    inlier_indices: list[int]
    inlier_cloud: Any
    outlier_cloud: Any


class Open3DPointCloudProcessor:
    """Application-level utilities for processing Open3D point clouds."""

    def voxel_downsample(
        self,
        point_cloud: Any,
        voxel_size: float,
    ) -> Any:
        """Downsample a point cloud using a voxel grid."""
        self._validate_positive_value(voxel_size, "voxel_size")

        try:
            return point_cloud.voxel_down_sample(voxel_size=voxel_size)
        except Exception as exception:
            raise PointCloudProcessingError(
                f"Failed to downsample point cloud: {exception}"
            ) from exception

    def remove_statistical_outliers(
        self,
        point_cloud: Any,
        nb_neighbors: int = 30,
        std_ratio: float = 2.0,
    ) -> Any:
        """Remove statistical outliers from a point cloud."""
        self._validate_positive_integer(nb_neighbors, "nb_neighbors")
        self._validate_positive_value(std_ratio, "std_ratio")

        try:
            filtered_cloud, _ = point_cloud.remove_statistical_outlier(
                nb_neighbors=nb_neighbors,
                std_ratio=std_ratio,
            )
            return filtered_cloud
        except Exception as exception:
            raise PointCloudProcessingError(
                f"Failed to remove statistical outliers: {exception}"
            ) from exception

    def remove_radius_outliers(
        self,
        point_cloud: Any,
        nb_points: int = 16,
        radius: float = 0.05,
    ) -> Any:
        """Remove radius-based outliers from a point cloud."""
        self._validate_positive_integer(nb_points, "nb_points")
        self._validate_positive_value(radius, "radius")

        try:
            filtered_cloud, _ = point_cloud.remove_radius_outlier(
                nb_points=nb_points,
                radius=radius,
            )
            return filtered_cloud
        except Exception as exception:
            raise PointCloudProcessingError(
                f"Failed to remove radius outliers: {exception}"
            ) from exception

    def segment_plane(
        self,
        point_cloud: Any,
        distance_threshold: float = 0.05,
        ransac_n: int = 3,
        num_iterations: int = 1000,
    ) -> PlaneSegmentationResult:
        """Segment the dominant plane using RANSAC."""
        self._validate_positive_value(distance_threshold, "distance_threshold")
        self._validate_positive_integer(ransac_n, "ransac_n")
        self._validate_positive_integer(num_iterations, "num_iterations")

        try:
            plane_model, inlier_indices = point_cloud.segment_plane(
                distance_threshold=distance_threshold,
                ransac_n=ransac_n,
                num_iterations=num_iterations,
            )

            inlier_cloud = point_cloud.select_by_index(inlier_indices)
            outlier_cloud = point_cloud.select_by_index(
                inlier_indices,
                invert=True,
            )

            return PlaneSegmentationResult(
                plane_model=tuple(float(value) for value in plane_model),
                inlier_indices=list(inlier_indices),
                inlier_cloud=inlier_cloud,
                outlier_cloud=outlier_cloud,
            )
        except Exception as exception:
            raise PointCloudProcessingError(
                f"Failed to segment plane: {exception}"
            ) from exception

    def preprocess_for_mapping(
        self,
        point_cloud: Any,
        voxel_size: float = 0.05,
        nb_neighbors: int = 30,
        std_ratio: float = 2.0,
    ) -> Any:
        """Apply a basic preprocessing pipeline for 3D mapping experiments."""
        downsampled_cloud = self.voxel_downsample(
            point_cloud=point_cloud,
            voxel_size=voxel_size,
        )

        return self.remove_statistical_outliers(
            point_cloud=downsampled_cloud,
            nb_neighbors=nb_neighbors,
            std_ratio=std_ratio,
        )

    @staticmethod
    def _validate_positive_value(value: float, name: str) -> None:
        if value <= 0.0:
            raise PointCloudProcessingError(f"{name} must be greater than zero.")

    @staticmethod
    def _validate_positive_integer(value: int, name: str) -> None:
        if value <= 0:
            raise PointCloudProcessingError(f"{name} must be greater than zero.")
