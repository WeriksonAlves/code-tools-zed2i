from __future__ import annotations

"""Sensor snapshot models for ZED2i streams.

This module defines immutable containers that represent the latest available
messages from the ZED2i sensor streams. It intentionally stores stream payloads
as generic objects because the domain layer must not depend on ROS 2 message
types or other infrastructure-specific classes.
"""

from dataclasses import dataclass
from typing import Any

LEFT_IMAGE_STREAM = "left_image"
RIGHT_IMAGE_STREAM = "right_image"
DISPARITY_STREAM = "disparity"
IMU_STREAM = "imu"
POINT_CLOUD_STREAM = "point_cloud"

ALL_STREAM_NAMES = (
    LEFT_IMAGE_STREAM,
    RIGHT_IMAGE_STREAM,
    DISPARITY_STREAM,
    IMU_STREAM,
    POINT_CLOUD_STREAM,
)


@dataclass(frozen=True)
class SensorSnapshot:
    """Immutable snapshot containing the latest available ZED2i stream data.

    The snapshot stores the latest available payload for each supported stream.
    The payload type is intentionally generic to keep the domain independent
    from ROS 2, OpenCV, NumPy, and Open3D.

    Attributes:
        left_image: Latest left image payload, when available.
        right_image: Latest right image payload, when available.
        disparity: Latest disparity payload, when available.
        imu: Latest IMU payload, when available.
        point_cloud: Latest point cloud payload, when available.
    """

    left_image: Any | None = None
    right_image: Any | None = None
    disparity: Any | None = None
    imu: Any | None = None
    point_cloud: Any | None = None

    def has_left_image(self) -> bool:
        """Return whether the snapshot contains a left image payload."""
        return self.left_image is not None

    def has_right_image(self) -> bool:
        """Return whether the snapshot contains a right image payload."""
        return self.right_image is not None

    def has_disparity(self) -> bool:
        """Return whether the snapshot contains a disparity payload."""
        return self.disparity is not None

    def has_imu(self) -> bool:
        """Return whether the snapshot contains an IMU payload."""
        return self.imu is not None

    def has_point_cloud(self) -> bool:
        """Return whether the snapshot contains a point cloud payload."""
        return self.point_cloud is not None

    def is_complete(self) -> bool:
        """Return whether all supported streams are available."""
        return all(self._stream_payloads().values())

    def available_streams(self) -> list[str]:
        """Return the names of streams with available payloads."""
        return [
            stream_name
            for stream_name, has_payload in self._stream_payloads().items()
            if has_payload
        ]

    def _stream_payloads(self) -> dict[str, bool]:
        """Return stream availability indexed by stream name."""
        return {
            LEFT_IMAGE_STREAM: self.has_left_image(),
            RIGHT_IMAGE_STREAM: self.has_right_image(),
            DISPARITY_STREAM: self.has_disparity(),
            IMU_STREAM: self.has_imu(),
            POINT_CLOUD_STREAM: self.has_point_cloud(),
        }
