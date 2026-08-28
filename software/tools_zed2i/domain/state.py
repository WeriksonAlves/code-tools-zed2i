"""Runtime state models for ZED2i stream health monitoring.

This module contains domain-level state containers used to estimate topic
health, stream frequency, stale data conditions, and adapter connection state.
It does not depend on ROS 2 primitives and can be tested without a running ROS
graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic

TOPIC_STATUS_NO_DATA = "NO_DATA"
TOPIC_STATUS_STALE = "STALE"
TOPIC_STATUS_OK = "OK"


@dataclass
class TopicHealth:
    """Runtime health state for a single data stream.

    Attributes:
        has_data: Indicates whether at least one message has been received.
        message_count: Number of received messages.
        first_receive_time_sec: Monotonic timestamp of the first message.
        last_receive_time_sec: Monotonic timestamp of the latest message.
    """

    has_data: bool = False
    message_count: int = 0
    first_receive_time_sec: float | None = None
    last_receive_time_sec: float | None = None

    def update(self) -> None:
        """Register the arrival of a new message."""
        current_time_sec = monotonic()

        if self.first_receive_time_sec is None:
            self.first_receive_time_sec = current_time_sec

        self.has_data = True
        self.message_count += 1
        self.last_receive_time_sec = current_time_sec

    def get_elapsed_time_sec(self) -> float | None:
        """Return elapsed time between the first and latest messages.

        Returns:
            Elapsed time in seconds, or ``None`` if fewer than one timestamp is
            available.
        """
        if self.first_receive_time_sec is None or self.last_receive_time_sec is None:
            return None

        return self.last_receive_time_sec - self.first_receive_time_sec

    def get_estimated_frequency_hz(self) -> float | None:
        """Estimate the stream frequency in hertz.

        The estimate uses the number of intervals between messages, which is
        ``message_count - 1``.

        Returns:
            Estimated frequency in hertz, or ``None`` if the estimate cannot be
            computed yet.
        """
        elapsed_time_sec = self.get_elapsed_time_sec()

        if elapsed_time_sec is None or elapsed_time_sec <= 0.0:
            return None

        if self.message_count <= 1:
            return None

        return (self.message_count - 1) / elapsed_time_sec

    def get_time_since_last_message_sec(self) -> float | None:
        """Return the time elapsed since the latest message.

        Returns:
            Time in seconds, or ``None`` if no message has been received.
        """
        if self.last_receive_time_sec is None:
            return None

        return monotonic() - self.last_receive_time_sec

    def is_stale(self, timeout_sec: float) -> bool:
        """Return whether the stream is stale according to a timeout.

        Args:
            timeout_sec: Maximum allowed age, in seconds, since the latest
                received message.

        Returns:
            ``True`` if the latest message is older than ``timeout_sec``.
        """
        time_since_last_message_sec = self.get_time_since_last_message_sec()

        if time_since_last_message_sec is None:
            return False

        return time_since_last_message_sec > timeout_sec

    def get_status(self, timeout_sec: float) -> str:
        """Return the symbolic health status for this stream."""
        if not self.has_data:
            return TOPIC_STATUS_NO_DATA

        if self.is_stale(timeout_sec):
            return TOPIC_STATUS_STALE

        return TOPIC_STATUS_OK


@dataclass
class Zed2iState:
    """Runtime state for a ZED2i adapter.

    Attributes:
        connected: Indicates whether the adapter is currently considered
            connected.
        last_error: Last registered error message, when available.
        topics: Per-stream health state indexed by stream name.
    """

    connected: bool = False
    last_error: str | None = None
    topics: dict[str, TopicHealth] = field(default_factory=dict)

    def register_topic(self, topic_name: str) -> None:
        """Register a stream in the health state if it does not exist."""
        if topic_name not in self.topics:
            self.topics[topic_name] = TopicHealth()

    def update_topic(self, topic_name: str) -> None:
        """Register a new message for a stream."""
        self.register_topic(topic_name)
        self.topics[topic_name].update()

    def set_error(self, error_message: str) -> None:
        """Set the adapter as disconnected and store the latest error."""
        self.last_error = error_message
        self.connected = False

    def set_connected(self) -> None:
        """Set the adapter as connected and clear the latest error."""
        self.connected = True
        self.last_error = None
