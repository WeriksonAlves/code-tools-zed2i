from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


class PointCloudConversionError(RuntimeError):
    """Raised when a ROS PointCloud2 message cannot be converted."""


class RosPointCloudConverter:
    """
    Utility class for converting ROS PointCloud2 messages to NumPy arrays.
    """

    def pointcloud_to_array(
        self,
        pointcloud_message: PointCloud2,
        field_names: Iterable[str] | None = None,
        skip_nans: bool = True,
    ) -> np.ndarray:
        """Convert a PointCloud2 message to a structured NumPy array."""
        selected_fields = tuple(field_names) if field_names is not None else None

        try:
            points = point_cloud2.read_points_numpy(
                pointcloud_message,
                field_names=selected_fields,
                skip_nans=skip_nans,
            )
            return np.asarray(points)
        except Exception as exception:
            raise PointCloudConversionError(
                f"Failed to convert ROS PointCloud2 message: {exception}"
            ) from exception

    def pointcloud_to_xyz(
        self,
        pointcloud_message: PointCloud2,
        skip_nans: bool = True,
    ) -> np.ndarray:
        """Convert a PointCloud2 message to an Nx3 XYZ NumPy array."""
        return self.pointcloud_to_array(
            pointcloud_message=pointcloud_message,
            field_names=("x", "y", "z"),
            skip_nans=skip_nans,
        )

    def pointcloud_to_xyzi(
        self,
        pointcloud_message: PointCloud2,
        skip_nans: bool = True,
    ) -> np.ndarray:
        """Convert a PointCloud2 message to an Nx4 XYZI NumPy array."""
        return self.pointcloud_to_array(
            pointcloud_message=pointcloud_message,
            field_names=("x", "y", "z", "intensity"),
            skip_nans=skip_nans,
        )

    def pointcloud_to_xyzrgb(
        self,
        pointcloud_message: PointCloud2,
        skip_nans: bool = True,
    ) -> np.ndarray:
        """Convert a PointCloud2 message to an Nx4 XYZRGB NumPy array."""
        return self.pointcloud_to_array(
            pointcloud_message=pointcloud_message,
            field_names=("x", "y", "z", "rgb"),
            skip_nans=skip_nans,
        )
