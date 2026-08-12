from time import sleep

from tools_zed2i.domain.state import TopicHealth, Zed2iState


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
    assert state.topics["imu"].first_receive_time_sec is not None


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


def test_topic_health_returns_no_data_before_first_message() -> None:
    health = TopicHealth()

    assert health.get_status(timeout_sec=1.0) == "NO_DATA"
    assert health.get_estimated_frequency_hz() is None
    assert health.get_time_since_last_message_sec() is None


def test_topic_health_returns_ok_after_update() -> None:
    health = TopicHealth()

    health.update()

    assert health.get_status(timeout_sec=1.0) == "OK"
    assert health.has_data is True
    assert health.message_count == 1


def test_topic_health_estimates_frequency_after_multiple_updates() -> None:
    health = TopicHealth()

    health.update()
    sleep(0.01)
    health.update()

    frequency_hz = health.get_estimated_frequency_hz()

    assert frequency_hz is not None
    assert frequency_hz > 0.0


def test_topic_health_detects_stale_stream() -> None:
    health = TopicHealth()

    health.update()
    sleep(0.02)

    assert health.get_status(timeout_sec=0.001) == "STALE"
