from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic


@dataclass
class TopicHealth:
    has_data: bool = False
    message_count: int = 0
    last_timestamp_sec: float | None = None
    last_receive_time_sec: float | None = None

    def update(self) -> None:
        self.has_data = True
        self.message_count += 1
        self.last_receive_time_sec = monotonic()


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