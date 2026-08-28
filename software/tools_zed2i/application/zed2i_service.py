"""Application service for accessing ZED2i stream data."""

from __future__ import annotations

from typing import Any

from tools_zed2i.domain.ports import Zed2iFrameReader
from tools_zed2i.domain.snapshot import (
    DISPARITY_STREAM,
    IMU_STREAM,
    LEFT_IMAGE_STREAM,
    POINT_CLOUD_STREAM,
    RIGHT_IMAGE_STREAM,
    SensorSnapshot,
)


class Zed2iService:
    """Application service for accessing the latest ZED2i sensor streams.

    This service depends on the ``Zed2iFrameReader`` port and is independent of
    the concrete acquisition mechanism. The frame reader may be implemented by
    a ROS 2 node, a dataset replay adapter, a simulator, or a test double.
    """

    def __init__(self, frame_reader: Zed2iFrameReader) -> None:
        """Initialize the service.

        Args:
            frame_reader: Adapter implementing the ZED2i frame reader port.
        """
        self._frame_reader = frame_reader

    def get_left_image(self) -> Any | None:
        """Return the latest left image payload, when available."""
        return self._frame_reader.get_latest_frame(LEFT_IMAGE_STREAM)

    def get_right_image(self) -> Any | None:
        """Return the latest right image payload, when available."""
        return self._frame_reader.get_latest_frame(RIGHT_IMAGE_STREAM)

    def get_disparity(self) -> Any | None:
        """Return the latest disparity payload, when available."""
        return self._frame_reader.get_latest_frame(DISPARITY_STREAM)

    def get_imu(self) -> Any | None:
        """Return the latest IMU payload, when available."""
        return self._frame_reader.get_latest_frame(IMU_STREAM)

    def get_point_cloud(self) -> Any | None:
        """Return the latest point cloud payload, when available."""
        return self._frame_reader.get_latest_frame(POINT_CLOUD_STREAM)

    def get_sensor_snapshot(self) -> SensorSnapshot:
        """Return a snapshot containing the latest available stream payloads.
        """
        return self._frame_reader.get_sensor_snapshot()
