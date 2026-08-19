from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from tools_zed2i.domain.snapshot import SensorSnapshot
from tools_zed2i.infrastructure.converters.image_converter import RosImageConverter
from tools_zed2i.infrastructure.converters.pointcloud_converter import (
    RosPointCloudConverter,
)


@dataclass(frozen=True)
class ConvertedSensorSnapshot:
    """Converted sensor snapshot with NumPy/OpenCV-compatible arrays."""

    left_image: np.ndarray | None = None
    right_image: np.ndarray | None = None
    disparity: np.ndarray | None = None
    point_cloud_xyz: np.ndarray | None = None

    def is_empty(self) -> bool:
        return (
            self.left_image is None
            and self.right_image is None
            and self.disparity is None
            and self.point_cloud_xyz is None
        )


class SnapshotConverter:
    """Application-level converter for selected snapshot streams."""

    def __init__(
        self,
        image_converter: Any | None = None,
        pointcloud_converter: Any | None = None,
    ) -> None:
        self._image_converter = image_converter or RosImageConverter()
        self._pointcloud_converter = (
            pointcloud_converter or RosPointCloudConverter()
        )

    def convert_images_to_bgr(
        self,
        snapshot: SensorSnapshot,
    ) -> ConvertedSensorSnapshot:
        """
        Convert available image streams in a sensor snapshot to BGR arrays.
        """
        left_image = None
        right_image = None
        disparity = None

        if snapshot.left_image is not None:
            left_image = self._image_converter.left_image_to_bgr(
                snapshot.left_image)

        if snapshot.right_image is not None:
            right_image = self._image_converter.right_image_to_bgr(
                snapshot.right_image)

        if snapshot.disparity is not None:
            disparity = self._image_converter.disparity_to_array(
                snapshot.disparity)

        return ConvertedSensorSnapshot(
            left_image=left_image,
            right_image=right_image,
            disparity=disparity,
        )

    def convert_point_cloud_to_xyz(
        self,
        snapshot: SensorSnapshot,
    ) -> ConvertedSensorSnapshot:
        """Convert the available point cloud stream to an XYZ NumPy array."""
        point_cloud_xyz = None

        if snapshot.point_cloud is not None:
            point_cloud_xyz = self._pointcloud_converter.pointcloud_to_xyz(
                snapshot.point_cloud
            )

        return ConvertedSensorSnapshot(point_cloud_xyz=point_cloud_xyz)

    def convert_all_available(
        self,
        snapshot: SensorSnapshot,
    ) -> ConvertedSensorSnapshot:
        """Convert all currently supported streams in a sensor snapshot."""
        converted_images = self.convert_images_to_bgr(snapshot)
        converted_point_cloud = self.convert_point_cloud_to_xyz(snapshot)

        return ConvertedSensorSnapshot(
            left_image=converted_images.left_image,
            right_image=converted_images.right_image,
            disparity=converted_images.disparity,
            point_cloud_xyz=converted_point_cloud.point_cloud_xyz,
        )
