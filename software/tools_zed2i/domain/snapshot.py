from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SensorSnapshot:
    """Immutable snapshot containing the latest available ZED2i stream messages."""

    left_image: Any | None = None
    right_image: Any | None = None
    disparity: Any | None = None
    imu: Any | None = None
    point_cloud: Any | None = None

    def has_left_image(self) -> bool:
        return self.left_image is not None

    def has_right_image(self) -> bool:
        return self.right_image is not None

    def has_disparity(self) -> bool:
        return self.disparity is not None

    def has_imu(self) -> bool:
        return self.imu is not None

    def has_point_cloud(self) -> bool:
        return self.point_cloud is not None

    def is_complete(self) -> bool:
        return all(
            [
                self.has_left_image(),
                self.has_right_image(),
                self.has_disparity(),
                self.has_imu(),
                self.has_point_cloud(),
            ]
        )

    def available_streams(self) -> list[str]:
        streams = []

        if self.has_left_image():
            streams.append("left_image")

        if self.has_right_image():
            streams.append("right_image")

        if self.has_disparity():
            streams.append("disparity")

        if self.has_imu():
            streams.append("imu")

        if self.has_point_cloud():
            streams.append("point_cloud")

        return streams