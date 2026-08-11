from __future__ import annotations

from typing import Any

from tools_zed2i.domain.ports import Zed2iFrameReader


class Zed2iService:
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

    def get_sensor_snapshot(self) -> dict[str, Any | None]:
        return {
            "left_image": self.get_left_image(),
            "right_image": self.get_right_image(),
            "disparity": self.get_disparity(),
            "imu": self.get_imu(),
            "point_cloud": self.get_point_cloud(),
        }