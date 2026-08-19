from __future__ import annotations

from typing import Any

from tools_zed2i.application.snapshot_converter import SnapshotConverter
from tools_zed2i.domain.snapshot import SensorSnapshot


class FakeImageConverter:
    def left_image_to_bgr(self, image_message: Any) -> str:
        return f"converted_left:{image_message}"

    def right_image_to_bgr(self, image_message: Any) -> str:
        return f"converted_right:{image_message}"

    def disparity_to_array(self, disparity_message: Any) -> str:
        return f"converted_disparity:{disparity_message}"


class FakePointCloudConverter:
    def pointcloud_to_xyz(self, pointcloud_message: Any) -> str:
        return f"converted_xyz:{pointcloud_message}"


def test_snapshot_converter_returns_empty_snapshot_when_no_images_are_available() -> None:
    converter = SnapshotConverter(
        image_converter=FakeImageConverter(),
        pointcloud_converter=FakePointCloudConverter(),
    )

    converted_snapshot = converter.convert_images_to_bgr(SensorSnapshot())

    assert converted_snapshot.is_empty() is True
    assert converted_snapshot.left_image is None
    assert converted_snapshot.right_image is None
    assert converted_snapshot.disparity is None


def test_snapshot_converter_converts_available_image_streams() -> None:
    converter = SnapshotConverter(
        image_converter=FakeImageConverter(),
        pointcloud_converter=FakePointCloudConverter(),
    )

    snapshot = SensorSnapshot(
        left_image="left_message",
        right_image="right_message",
        disparity="disparity_message",
    )

    converted_snapshot = converter.convert_images_to_bgr(snapshot)

    assert converted_snapshot.is_empty() is False
    assert converted_snapshot.left_image == "converted_left:left_message"
    assert converted_snapshot.right_image == "converted_right:right_message"
    assert converted_snapshot.disparity == "converted_disparity:disparity_message"


def test_snapshot_converter_ignores_missing_streams() -> None:
    converter = SnapshotConverter(
        image_converter=FakeImageConverter(),
        pointcloud_converter=FakePointCloudConverter(),
    )

    snapshot = SensorSnapshot(left_image="left_message")

    converted_snapshot = converter.convert_images_to_bgr(snapshot)

    assert converted_snapshot.left_image == "converted_left:left_message"
    assert converted_snapshot.right_image is None
    assert converted_snapshot.disparity is None


def test_snapshot_converter_converts_point_cloud_stream() -> None:
    converter = SnapshotConverter(
        image_converter=FakeImageConverter(),
        pointcloud_converter=FakePointCloudConverter(),
    )

    snapshot = SensorSnapshot(point_cloud="point_cloud_message")

    converted_snapshot = converter.convert_point_cloud_to_xyz(snapshot)

    assert converted_snapshot.is_empty() is False
    assert converted_snapshot.point_cloud_xyz == "converted_xyz:point_cloud_message"


def test_snapshot_converter_converts_all_available_streams() -> None:
    converter = SnapshotConverter(
        image_converter=FakeImageConverter(),
        pointcloud_converter=FakePointCloudConverter(),
    )

    snapshot = SensorSnapshot(
        left_image="left_message",
        right_image="right_message",
        disparity="disparity_message",
        point_cloud="point_cloud_message",
    )

    converted_snapshot = converter.convert_all_available(snapshot)

    assert converted_snapshot.left_image == "converted_left:left_message"
    assert converted_snapshot.right_image == "converted_right:right_message"
    assert converted_snapshot.disparity == "converted_disparity:disparity_message"
    assert converted_snapshot.point_cloud_xyz == "converted_xyz:point_cloud_message"
