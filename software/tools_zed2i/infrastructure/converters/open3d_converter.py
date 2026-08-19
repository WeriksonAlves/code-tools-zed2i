from __future__ import annotations

from typing import Any

import numpy as np

from tools_zed2i.infrastructure.converters.pointcloud_converter import (
    RosPointCloudConverter,
)


class Open3DConversionError(RuntimeError):
    """Raised when a point cloud cannot be converted to Open3D."""


class Open3DConverter:
    """Utility class for optional Open3D point cloud conversion."""

    def __init__(
        self,
        pointcloud_converter: RosPointCloudConverter | None = None,
    ) -> None:
        self._pointcloud_converter = pointcloud_converter or RosPointCloudConverter()

    def xyz_array_to_open3d(self, xyz_points: np.ndarray) -> Any:
        """Convert an Nx3 XYZ NumPy array to an Open3D PointCloud."""
        open3d = self._import_open3d()
        normalized_points = self._validate_xyz_array(xyz_points)

        point_cloud = open3d.geometry.PointCloud()
        point_cloud.points = open3d.utility.Vector3dVector(normalized_points)

        return point_cloud

    def pointcloud_message_to_open3d(self, pointcloud_message: Any) -> Any:
        """Convert a ROS PointCloud2 message to an Open3D PointCloud."""
        xyz_points = self._pointcloud_converter.pointcloud_to_xyz(
            pointcloud_message=pointcloud_message,
        )
        return self.xyz_array_to_open3d(xyz_points)

    @staticmethod
    def _import_open3d() -> Any:
        try:
            import open3d

            return open3d
        except ImportError as exception:
            raise Open3DConversionError(
                "Open3D is not installed. Install it with: "
                "python3 -m pip install -r software/requirements-open3d.txt"
            ) from exception

    @staticmethod
    def _validate_xyz_array(xyz_points: np.ndarray) -> np.ndarray:
        points = np.asarray(xyz_points, dtype=np.float64)

        if points.ndim != 2:
            raise Open3DConversionError(
                "XYZ point cloud array must be a 2D array."
            )

        if points.shape[1] != 3:
            raise Open3DConversionError(
                "XYZ point cloud array must have shape Nx3."
            )

        return points
