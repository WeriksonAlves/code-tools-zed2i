"""ROS PointCloud2 conversion adapters for ZED2i point cloud streams."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2

XYZ_FIELDS = ("x", "y", "z")
XYZI_FIELDS = ("x", "y", "z", "intensity")
XYZRGB_FIELDS = ("x", "y", "z", "rgb")


class PointCloudConversionError(RuntimeError):
    """Raised when a ROS PointCloud2 message cannot be converted."""


class RosPointCloudConverter:
    """Converter for ROS ``PointCloud2`` messages.

    This adapter uses ``sensor_msgs_py.point_cloud2`` to extract point fields
    into NumPy arrays. It is infrastructure code because it depends directly on
    ROS message types.
    """

    def pointcloud_to_array(
        self,
        pointcloud_message: PointCloud2,
        field_names: Iterable[str] | None = None,
        skip_nans: bool = True,
    ) -> np.ndarray:
        """Convert a PointCloud2 message to a NumPy array.

        Args:
            pointcloud_message: ROS ``PointCloud2`` message.
            field_names: Optional list of fields to extract.
            skip_nans: Whether points containing NaN values should be skipped.

        Returns:
            NumPy array containing the selected point fields.

        Raises:
            PointCloudConversionError: If the message cannot be converted.
        """
        selected_fields = self._normalize_field_names(field_names)

        try:
            points = point_cloud2.read_points_numpy(
                pointcloud_message,
                field_names=selected_fields,
                skip_nans=skip_nans,
            )
            return np.asarray(points)
        except (
            RuntimeError,
            TypeError,
            ValueError,
            AssertionError
        ) as exception:
            raise PointCloudConversionError(
                f"Failed to convert ROS PointCloud2 message: {exception}"
            ) from exception

    def pointcloud_to_xyz(
        self,
        pointcloud_message: PointCloud2,
        skip_nans: bool = True,
    ) -> np.ndarray:
        """Convert a PointCloud2 message to an ``N x 3`` XYZ array."""
        return self.pointcloud_to_array(
            pointcloud_message=pointcloud_message,
            field_names=XYZ_FIELDS,
            skip_nans=skip_nans,
        )

    def pointcloud_to_xyzi(
        self,
        pointcloud_message: PointCloud2,
        skip_nans: bool = True,
    ) -> np.ndarray:
        """Convert a PointCloud2 message to an ``N x 4`` XYZI array."""
        return self.pointcloud_to_array(
            pointcloud_message=pointcloud_message,
            field_names=XYZI_FIELDS,
            skip_nans=skip_nans,
        )

    def pointcloud_to_xyzrgb(
        self,
        pointcloud_message: PointCloud2,
        skip_nans: bool = True,
    ) -> np.ndarray:
        """Convert a PointCloud2 message to an ``N x 4`` XYZRGB array."""
        return self.pointcloud_to_array(
            pointcloud_message=pointcloud_message,
            field_names=XYZRGB_FIELDS,
            skip_nans=skip_nans,
        )

    @staticmethod
    def _normalize_field_names(
        field_names: Iterable[str] | None,
    ) -> tuple[str, ...] | None:
        """Normalize field names to the format expected by ROS utilities."""
        if field_names is None:
            return None

        return tuple(field_names)
