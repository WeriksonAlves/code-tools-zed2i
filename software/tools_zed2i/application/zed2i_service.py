from __future__ import annotations

from typing import Any

from tools_zed2i.domain.ports import Zed2iFrameReader
from tools_zed2i.domain.snapshot import SensorSnapshot


class Zed2iService:
    """Application service for accessing ZED2i sensor streams."""

    def __init__(self, frame_reader: Zed2iFrameReader) -> None:
        self._frame_reader = frame_reader

    def get_left_image(self) -> Any | None:
        return self._frame_reader.get_latest_frame("left_image")

    def get_right_image(self) -> Any | None:
        return self._frame_reader.get_latest_frame("right_image")

    def get_disparity(self) -> Any | None:
        return self._frame_reader.get_latest_frame("disparity")

    def get_imu(self) -> Any | None:
        return self._frame_reader.get_latest_frame("imu")

    def get_point_cloud(self) -> Any | None:
        return self._frame_reader.get_latest_frame("point_cloud")

    def get_sensor_snapshot(self) -> SensorSnapshot:
        return self._frame_reader.get_sensor_snapshot()
