from tools_zed2i.domain.snapshot import SensorSnapshot


def test_empty_snapshot_has_no_streams() -> None:
    snapshot = SensorSnapshot()

    assert snapshot.has_left_image() is False
    assert snapshot.has_right_image() is False
    assert snapshot.has_disparity() is False
    assert snapshot.has_imu() is False
    assert snapshot.has_point_cloud() is False
    assert snapshot.is_complete() is False
    assert snapshot.available_streams() == []


def test_snapshot_reports_available_streams() -> None:
    snapshot = SensorSnapshot(
        left_image=object(),
        imu=object(),
    )

    assert snapshot.has_left_image() is True
    assert snapshot.has_imu() is True
    assert snapshot.has_right_image() is False
    assert snapshot.has_disparity() is False
    assert snapshot.has_point_cloud() is False
    assert snapshot.is_complete() is False
    assert snapshot.available_streams() == ["left_image", "imu"]


def test_snapshot_reports_complete_state() -> None:
    snapshot = SensorSnapshot(
        left_image=object(),
        right_image=object(),
        disparity=object(),
        imu=object(),
        point_cloud=object(),
    )

    assert snapshot.is_complete() is True
    assert snapshot.available_streams() == [
        "left_image",
        "right_image",
        "disparity",
        "imu",
        "point_cloud",
    ]
