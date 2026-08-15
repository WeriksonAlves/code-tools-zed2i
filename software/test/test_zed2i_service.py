from typing import Any

from tools_zed2i.application.zed2i_service import Zed2iService
from tools_zed2i.domain.ports import Zed2iFrameReader
from tools_zed2i.domain.snapshot import SensorSnapshot


class FakeFrameReader(Zed2iFrameReader):
    def __init__(self) -> None:
        self._frames: dict[str, Any] = {
            "left_image": "left_frame",
            "right_image": "right_frame",
            "disparity": "disparity_frame",
            "imu": "imu_frame",
            "point_cloud": "point_cloud_frame",
        }

    def get_latest_frame(self, stream_name: str) -> Any | None:
        return self._frames.get(stream_name)

    def get_sensor_snapshot(self) -> SensorSnapshot:
        return SensorSnapshot(
            left_image=self._frames["left_image"],
            right_image=self._frames["right_image"],
            disparity=self._frames["disparity"],
            imu=self._frames["imu"],
            point_cloud=self._frames["point_cloud"],
        )


def test_zed2i_service_returns_individual_frames() -> None:
    service = Zed2iService(frame_reader=FakeFrameReader())

    assert service.get_left_image() == "left_frame"
    assert service.get_right_image() == "right_frame"
    assert service.get_disparity() == "disparity_frame"
    assert service.get_imu() == "imu_frame"
    assert service.get_point_cloud() == "point_cloud_frame"


def test_zed2i_service_returns_sensor_snapshot() -> None:
    service = Zed2iService(frame_reader=FakeFrameReader())

    snapshot = service.get_sensor_snapshot()

    assert snapshot.left_image == "left_frame"
    assert snapshot.right_image == "right_frame"
    assert snapshot.disparity == "disparity_frame"
    assert snapshot.imu == "imu_frame"
    assert snapshot.point_cloud == "point_cloud_frame"
    assert snapshot.is_complete() is True
