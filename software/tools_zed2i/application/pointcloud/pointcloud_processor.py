"""Open3D point cloud processing utilities for mapping applications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class PointCloudProcessingError(RuntimeError):
    """Raised when an Open3D point cloud processing operation fails."""


@dataclass(frozen=True)
class PlaneSegmentationResult:
    """Result of a plane segmentation operation.

    Attributes:
        plane_model: Plane coefficients ``(a, b, c, d)`` from the equation
            ``ax + by + cz + d = 0``.
        inlier_indices: Indices of points classified as plane inliers.
        inlier_cloud: Point cloud containing the plane inliers.
        outlier_cloud: Point cloud containing the remaining points.
    """

    plane_model: tuple[float, float, float, float]
    inlier_indices: list[int]
    inlier_cloud: Any
    outlier_cloud: Any

    def inlier_count(self) -> int:
        """Return the number of plane inliers."""
        return len(self.inlier_indices)

    def has_inliers(self) -> bool:
        """Return whether the segmented plane has at least one inlier."""
        return bool(self.inlier_indices)


class Open3DPointCloudProcessor:
    """Application-level utilities for processing Open3D point clouds.

    The processor assumes that point clouds are Open3D-compatible objects. The
    concrete Open3D dependency is intentionally kept implicit through duck
    typing to make tests and adapters easier to isolate.
    """

    def voxel_downsample(
        self,
        point_cloud: Any,
        voxel_size: float,
    ) -> Any:
        """Downsample a point cloud using a voxel grid.

        Args:
            point_cloud: Open3D-compatible point cloud.
            voxel_size: Voxel size used for downsampling.

        Returns:
            Downsampled point cloud.

        Raises:
            PointCloudProcessingError: If the operation fails.
        """
        self._validate_positive_value(voxel_size, "voxel_size")

        try:
            return point_cloud.voxel_down_sample(voxel_size=voxel_size)
        except (RuntimeError, TypeError, ValueError, AttributeError
                ) as exception:
            raise PointCloudProcessingError(
                f"Failed to downsample point cloud: {exception}"
            ) from exception

    def remove_statistical_outliers(
        self,
        point_cloud: Any,
        nb_neighbors: int = 30,
        std_ratio: float = 2.0,
    ) -> Any:
        """Remove statistical outliers from a point cloud.

        Args:
            point_cloud: Open3D-compatible point cloud.
            nb_neighbors: Number of neighbors used by the statistical filter.
            std_ratio: Standard deviation ratio threshold.

        Returns:
            Filtered point cloud.

        Raises:
            PointCloudProcessingError: If the operation fails.
        """
        self._validate_positive_integer(nb_neighbors, "nb_neighbors")
        self._validate_positive_value(std_ratio, "std_ratio")

        try:
            filtered_cloud, _ = point_cloud.remove_statistical_outlier(
                nb_neighbors=nb_neighbors,
                std_ratio=std_ratio,
            )
            return filtered_cloud
        except (RuntimeError, TypeError, ValueError, AttributeError
                ) as exception:
            raise PointCloudProcessingError(
                f"Failed to remove statistical outliers: {exception}"
            ) from exception

    def remove_radius_outliers(
        self,
        point_cloud: Any,
        nb_points: int = 16,
        radius: float = 0.05,
    ) -> Any:
        """Remove radius-based outliers from a point cloud.

        Args:
            point_cloud: Open3D-compatible point cloud.
            nb_points: Minimum number of neighbors within the search radius.
            radius: Search radius.

        Returns:
            Filtered point cloud.

        Raises:
            PointCloudProcessingError: If the operation fails.
        """
        self._validate_positive_integer(nb_points, "nb_points")
        self._validate_positive_value(radius, "radius")

        try:
            filtered_cloud, _ = point_cloud.remove_radius_outlier(
                nb_points=nb_points,
                radius=radius,
            )
            return filtered_cloud
        except (RuntimeError, TypeError, ValueError, AttributeError
                ) as exception:
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
        """Segment the dominant plane using RANSAC.

        Args:
            point_cloud: Open3D-compatible point cloud.
            distance_threshold: Maximum distance from a point to the plane.
            ransac_n: Number of points sampled per RANSAC iteration.
            num_iterations: Number of RANSAC iterations.

        Returns:
            Plane segmentation result.

        Raises:
            PointCloudProcessingError: If segmentation fails.
        """
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
                plane_model=self._parse_plane_model(plane_model),
                inlier_indices=list(inlier_indices),
                inlier_cloud=inlier_cloud,
                outlier_cloud=outlier_cloud,
            )
        except (RuntimeError, TypeError, ValueError, AttributeError
                ) as exception:
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
        """Apply a basic preprocessing pipeline for 3D mapping experiments.

        The current pipeline applies voxel downsampling followed by statistical
        outlier removal.

        Args:
            point_cloud: Open3D-compatible point cloud.
            voxel_size: Voxel size used for downsampling.
            nb_neighbors: Number of neighbors used by the statistical filter.
            std_ratio: Standard deviation ratio threshold.

        Returns:
            Preprocessed point cloud.
        """
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
    def _parse_plane_model(
        plane_model: Any,
    ) -> tuple[float, float, float, float]:
        """Parse an Open3D plane model into a four-value tuple."""
        parsed_model = tuple(float(value) for value in plane_model)

        if len(parsed_model) != 4:
            raise PointCloudProcessingError(
                "Plane model must contain exactly four coefficients."
            )

        return parsed_model

    @staticmethod
    def _validate_positive_value(value: float, name: str) -> None:
        """Validate that a numeric value is greater than zero."""
        if value <= 0.0:
            raise PointCloudProcessingError(
                f"{name} must be greater than zero.")

    @staticmethod
    def _validate_positive_integer(value: int, name: str) -> None:
        """Validate that an integer value is greater than zero."""
        if value <= 0:
            raise PointCloudProcessingError(
                f"{name} must be greater than zero.")
