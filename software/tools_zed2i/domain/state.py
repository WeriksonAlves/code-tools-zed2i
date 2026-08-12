from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic


@dataclass
class TopicHealth:
    has_data: bool = False
    message_count: int = 0
    first_receive_time_sec: float | None = None
    last_receive_time_sec: float | None = None

    def update(self) -> None:
        current_time_sec = monotonic()

        if self.first_receive_time_sec is None:
            self.first_receive_time_sec = current_time_sec

        self.has_data = True
        self.message_count += 1
        self.last_receive_time_sec = current_time_sec

    def get_elapsed_time_sec(self) -> float | None:
        if self.first_receive_time_sec is None or self.last_receive_time_sec is None:
            return None

        return self.last_receive_time_sec - self.first_receive_time_sec

    def get_estimated_frequency_hz(self) -> float | None:
        elapsed_time_sec = self.get_elapsed_time_sec()

        if elapsed_time_sec is None or elapsed_time_sec <= 0.0:
            return None

        if self.message_count <= 1:
            return None

        return (self.message_count - 1) / elapsed_time_sec

    def get_time_since_last_message_sec(self) -> float | None:
        if self.last_receive_time_sec is None:
            return None

        return monotonic() - self.last_receive_time_sec

    def is_stale(self, timeout_sec: float) -> bool:
        time_since_last_message_sec = self.get_time_since_last_message_sec()

        if time_since_last_message_sec is None:
            return False

        return time_since_last_message_sec > timeout_sec

    def get_status(self, timeout_sec: float) -> str:
        if not self.has_data:
            return "NO_DATA"

        if self.is_stale(timeout_sec):
            return "STALE"

        return "OK"


@dataclass
class Zed2iState:
    connected: bool = False
    last_error: str | None = None
    topics: dict[str, TopicHealth] = field(default_factory=dict)

    def register_topic(self, topic_name: str) -> None:
        if topic_name not in self.topics:
            self.topics[topic_name] = TopicHealth()

    def update_topic(self, topic_name: str) -> None:
        self.register_topic(topic_name)
        self.topics[topic_name].update()

    def set_error(self, error_message: str) -> None:
        self.last_error = error_message
        self.connected = False

    def set_connected(self) -> None:
        self.connected = True
        self.last_error = None
