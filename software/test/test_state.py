from tools_zed2i.domain.state import Zed2iState


def test_register_topic_creates_topic_health() -> None:
    state = Zed2iState()

    state.register_topic("left_image")

    assert "left_image" in state.topics
    assert state.topics["left_image"].has_data is False
    assert state.topics["left_image"].message_count == 0


def test_update_topic_sets_data_flag_and_increments_count() -> None:
    state = Zed2iState()

    state.update_topic("imu")
    state.update_topic("imu")

    assert state.topics["imu"].has_data is True
    assert state.topics["imu"].message_count == 2
    assert state.topics["imu"].last_receive_time_sec is not None


def test_set_connected_clears_previous_error() -> None:
    state = Zed2iState()
    state.set_error("Connection failed")

    state.set_connected()

    assert state.connected is True
    assert state.last_error is None


def test_set_error_marks_state_as_disconnected() -> None:
    state = Zed2iState()
    state.set_connected()

    state.set_error("Sensor timeout")

    assert state.connected is False
    assert state.last_error == "Sensor timeout"
