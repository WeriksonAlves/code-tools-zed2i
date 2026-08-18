from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import rclpy
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from sensor_msgs.msg import Image, Imu, PointCloud2
from stereo_msgs.msg import DisparityImage

from tools_zed2i.domain.config import Zed2iConfig
from tools_zed2i.domain.ports import Zed2iFrameReader
from tools_zed2i.domain.snapshot import SensorSnapshot
from tools_zed2i.domain.state import Zed2iState

MESSAGE_TYPES: dict[str, type] = {
    "sensor_msgs/msg/Image": Image,
    "sensor_msgs/msg/Imu": Imu,
    "sensor_msgs/msg/PointCloud2": PointCloud2,
    "stereo_msgs/msg/DisparityImage": DisparityImage,
}


class Zed2iRosNode(Node, Zed2iFrameReader):
    """ROS 2 adapter node for ZED2i sensor streams."""

    def __init__(self, config_path: str | Path) -> None:
        self._config = Zed2iConfig.from_yaml(config_path)

        super().__init__(self._config.node_name)

        self.get_logger().info(
            f"Using stream preset: {self._config.active_preset}"
        )

        self._state = Zed2iState()
        self._latest_messages: dict[str, Any] = {}
        self._callback_group = ReentrantCallbackGroup()
        self._qos = self._make_qos_profile()

        self._relay_publishers: dict[str, Any] = {}
        self._stream_subscriptions: list[Any] = []
        self._diagnostics_publisher = None

        if self._config.diagnostics.enabled:
            self._diagnostics_publisher = self.create_publisher(
                DiagnosticArray,
                self._config.diagnostics.topic,
                10,
            )
            self.get_logger().info(
                f"Publishing diagnostics to {self._config.diagnostics.topic}."
            )

        self._configure_streams()

        self._diagnostics_timer = self.create_timer(
            self._config.runtime.diagnostics_period_sec,
            self._publish_diagnostics,
        )

        self._state.set_connected()
        self.get_logger().info("ZED2i ROS node initialized successfully.")

    def get_latest_frame(self, stream_name: str) -> Any | None:
        """Return the latest received message for a given stream."""
        return self._latest_messages.get(stream_name)

    def get_sensor_snapshot(self) -> SensorSnapshot:
        """
        Return an immutable snapshot with the latest received stream messages.
        """
        return SensorSnapshot(
            left_image=self._latest_messages.get("left_image"),
            right_image=self._latest_messages.get("right_image"),
            disparity=self._latest_messages.get("disparity"),
            imu=self._latest_messages.get("imu"),
            point_cloud=self._latest_messages.get("point_cloud"),
        )

    def _make_qos_profile(self) -> QoSProfile:
        if self._config.runtime.qos_profile == "sensor_data":
            return QoSProfile(
                reliability=ReliabilityPolicy.BEST_EFFORT,
                durability=DurabilityPolicy.VOLATILE,
                history=HistoryPolicy.KEEP_LAST,
                depth=5,
            )

        return QoSProfile(depth=10)

    def _configure_streams(self) -> None:
        feature_flags = {
            "left_image": self._config.stream_selection.left_image,
            "right_image": self._config.stream_selection.right_image,
            "disparity": self._config.stream_selection.disparity,
            "imu": self._config.stream_selection.imu,
            "point_cloud": self._config.stream_selection.point_cloud,
        }

        for stream_name, enabled in feature_flags.items():
            if not enabled:
                self.get_logger().debug(
                    f"Stream '{stream_name}' is disabled by configuration."
                )
                continue

            topic_config = self._config.topics.get(stream_name)

            if topic_config is None:
                raise KeyError(
                    f"Stream '{stream_name}' is enabled, but no topic "
                    "configuration was found in the YAML file."
                )

            message_class = MESSAGE_TYPES.get(topic_config.message_type)

            if message_class is None:
                supported_types = ", ".join(sorted(MESSAGE_TYPES.keys()))
                raise ValueError(
                    f"Unsupported message type '{topic_config.message_type}' "
                    f"for stream '{stream_name}'. Supported types: {supported_types}"
                )

            if self._config.features.relay_enabled:
                self._relay_publishers[stream_name] = self.create_publisher(
                    message_class,
                    topic_config.output_topic,
                    self._qos,
                )

            callback = self._make_callback(stream_name)

            subscription = self.create_subscription(
                message_class,
                topic_config.input_topic,
                callback,
                self._qos,
                callback_group=self._callback_group,
            )

            self._stream_subscriptions.append(subscription)
            self._state.register_topic(stream_name)

            self.get_logger().info(
                f"Subscribed to {topic_config.input_topic} "
                f"as stream '{stream_name}'."
            )

            if self._config.features.relay_enabled:
                self.get_logger().info(
                    f"Relaying stream '{stream_name}' "
                    f"to {topic_config.output_topic}."
                )

    def _make_callback(self, stream_name: str) -> Callable[[Any], None]:
        def callback(message: Any) -> None:
            self._latest_messages[stream_name] = message
            self._state.update_topic(stream_name)

            publisher = self._relay_publishers.get(stream_name)
            if publisher is not None:
                publisher.publish(message)

        return callback

    def _publish_diagnostics(self) -> None:
        status_parts = []
        diagnostic_statuses = []

        for stream_name, health in self._state.topics.items():
            status = health.get_status(
                timeout_sec=self._config.runtime.expected_timeout_sec,
            )

            frequency_hz = health.get_estimated_frequency_hz()
            message_age_sec = health.get_time_since_last_message_sec()

            frequency_text = (
                f"{frequency_hz:.2f}"
                if frequency_hz is not None
                else "N/A"
            )

            message_age_text = (
                f"{message_age_sec:.2f}s"
                if message_age_sec is not None
                else "N/A"
            )

            status_parts.append(
                f"{stream_name}={status}, "
                f"count={health.message_count}, "
                f"hz={frequency_text}, "
                f"age={message_age_text}"
            )

            diagnostic_statuses.append(
                self._make_stream_diagnostic_status(
                    stream_name=stream_name,
                    status=status,
                    message_count=health.message_count,
                    frequency_hz=frequency_hz,
                    message_age_sec=message_age_sec,
                )
            )

        if not status_parts:
            self.get_logger().warning(
                "ZED2i diagnostics: no streams configured."
            )
            return

        diagnostics = " | ".join(status_parts)
        self.get_logger().info(f"ZED2i diagnostics: {diagnostics}")

        if self._diagnostics_publisher is not None:
            self._publish_diagnostics_message(diagnostic_statuses)

    def _make_stream_diagnostic_status(
        self,
        stream_name: str,
        status: str,
        message_count: int,
        frequency_hz: float | None,
        message_age_sec: float | None,
    ) -> DiagnosticStatus:
        diagnostic_status = DiagnosticStatus()
        diagnostic_status.name = f"tools_zed2i/{stream_name}"
        diagnostic_status.hardware_id = self._config.diagnostics.hardware_id
        diagnostic_status.message = status
        diagnostic_status.level = self._get_diagnostic_level(status)

        diagnostic_status.values = [
            KeyValue(key="stream_name", value=stream_name),
            KeyValue(key="status", value=status),
            KeyValue(key="message_count", value=str(message_count)),
            KeyValue(
                key="estimated_frequency_hz",
                value=(
                    f"{frequency_hz:.2f}"
                    if frequency_hz is not None
                    else "N/A"
                ),
            ),
            KeyValue(
                key="message_age_sec",
                value=(
                    f"{message_age_sec:.2f}"
                    if message_age_sec is not None
                    else "N/A"
                ),
            ),
        ]

        return diagnostic_status

    @staticmethod
    def _get_diagnostic_level(status: str) -> int:
        if status == "OK":
            return DiagnosticStatus.OK

        if status == "STALE":
            return DiagnosticStatus.WARN

        return DiagnosticStatus.ERROR

    def _publish_diagnostics_message(
        self,
        diagnostic_statuses: list[DiagnosticStatus],
    ) -> None:
        diagnostics_message = DiagnosticArray()
        diagnostics_message.header.stamp = self.get_clock().now().to_msg()
        diagnostics_message.status = diagnostic_statuses

        if self._diagnostics_publisher is not None:
            self._diagnostics_publisher.publish(diagnostics_message)


def _read_config_path_from_ros_parameter() -> str:
    temporary_node = rclpy.create_node("zed2i_config_loader")

    try:
        temporary_node.declare_parameter("config_path", "")
        config_path = temporary_node.get_parameter("config_path").value
    finally:
        temporary_node.destroy_node()

    if not config_path:
        raise RuntimeError(
            "Parameter 'config_path' must be provided. Example: "
            "ros2 run tools_zed2i zed2i_node --ros-args "
            "-p config_path:=/path/to/zed2i.yaml"
        )

    return str(config_path)


def main() -> None:
    rclpy.init()

    node: Zed2iRosNode | None = None

    try:
        config_path = _read_config_path_from_ros_parameter()
        node = Zed2iRosNode(config_path=config_path)
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
