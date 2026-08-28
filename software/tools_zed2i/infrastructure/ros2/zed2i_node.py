"""ROS 2 node adapter for ZED2i sensor streams.

This module provides the main ROS 2 adapter used by ``tools_zed2i``. The node
subscribes to configured ZED2i topics, stores the latest messages, optionally
relays them to output topics, and publishes stream diagnostics.

The node implements the ``Zed2iFrameReader`` domain port, allowing application
services to access sensor data without depending directly on ROS 2.
"""

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
from tools_zed2i.domain.snapshot import (
    DISPARITY_STREAM,
    IMU_STREAM,
    LEFT_IMAGE_STREAM,
    POINT_CLOUD_STREAM,
    RIGHT_IMAGE_STREAM,
    SensorSnapshot,
)
from tools_zed2i.domain.state import (
    TOPIC_STATUS_OK,
    TOPIC_STATUS_STALE,
    Zed2iState,
)

CONFIG_PATH_PARAMETER = "config_path"
CONFIG_LOADER_NODE_NAME = "zed2i_config_loader"

SENSOR_DATA_QOS_PROFILE = "sensor_data"
SENSOR_DATA_QOS_DEPTH = 5
DEFAULT_QOS_DEPTH = 10
DIAGNOSTICS_QOS_DEPTH = 10

MESSAGE_TYPES: dict[str, type] = {
    "sensor_msgs/msg/Image": Image,
    "sensor_msgs/msg/Imu": Imu,
    "sensor_msgs/msg/PointCloud2": PointCloud2,
    "stereo_msgs/msg/DisparityImage": DisparityImage,
}


class Zed2iRosNode(Node, Zed2iFrameReader):
    """ROS 2 adapter node for configured ZED2i sensor streams.

    The node reads stream configuration from a YAML file, subscribes to enabled
    input topics, stores the latest received messages, and optionally
    republishes them to configured output topics.

    Args:
        config_path: Optional path to the ZED2i YAML configuration. When
            omitted, the path is read from the ROS parameter ``config_path``.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize the ZED2i ROS 2 node."""
        resolved_config_path = (
            config_path or _read_config_path_from_ros_parameter()
        )
        self._config = Zed2iConfig.from_yaml(resolved_config_path)

        super().__init__(self._config.node_name)

        self._state = Zed2iState()
        self._latest_messages: dict[str, Any] = {}
        self._callback_group = ReentrantCallbackGroup()
        self._qos = self._make_qos_profile()

        self._relay_publishers: dict[str, Any] = {}
        self._stream_subscriptions: list[Any] = []
        self._diagnostics_publisher: Any | None = None

        self.get_logger().info(
            f"Using stream preset: {self._config.active_preset}"
        )

        self._configure_diagnostics_publisher()
        self._configure_streams()
        self._configure_diagnostics_timer()

        self._state.set_connected()
        self.get_logger().info("ZED2i ROS node initialized successfully.")

    def get_latest_frame(self, stream_name: str) -> Any | None:
        """Return the latest received message for a given stream.

        Args:
            stream_name: Logical stream name.

        Returns:
            Latest received message, or ``None`` if no message was received.
        """
        return self._latest_messages.get(stream_name)

    def get_sensor_snapshot(self) -> SensorSnapshot:
        """Return an immutable snapshot with the latest stream messages."""
        return SensorSnapshot(
            left_image=self._latest_messages.get(LEFT_IMAGE_STREAM),
            right_image=self._latest_messages.get(RIGHT_IMAGE_STREAM),
            disparity=self._latest_messages.get(DISPARITY_STREAM),
            imu=self._latest_messages.get(IMU_STREAM),
            point_cloud=self._latest_messages.get(POINT_CLOUD_STREAM),
        )

    def _configure_diagnostics_publisher(self) -> None:
        """Configure diagnostics publishing when enabled."""
        if not self._config.diagnostics.enabled:
            return

        self._diagnostics_publisher = self.create_publisher(
            DiagnosticArray,
            self._config.diagnostics.topic,
            DIAGNOSTICS_QOS_DEPTH,
        )
        self.get_logger().info(
            f"Publishing diagnostics to {self._config.diagnostics.topic}."
        )

    def _configure_diagnostics_timer(self) -> None:
        """Create the periodic diagnostics timer."""
        self._diagnostics_timer = self.create_timer(
            self._config.runtime.diagnostics_period_sec,
            self._publish_diagnostics,
        )

    def _make_qos_profile(self) -> QoSProfile:
        """Create the QoS profile used by stream subscriptions and relays."""
        if self._config.runtime.qos_profile == SENSOR_DATA_QOS_PROFILE:
            return QoSProfile(
                reliability=ReliabilityPolicy.BEST_EFFORT,
                durability=DurabilityPolicy.VOLATILE,
                history=HistoryPolicy.KEEP_LAST,
                depth=SENSOR_DATA_QOS_DEPTH,
            )

        return QoSProfile(depth=DEFAULT_QOS_DEPTH)

    def _configure_streams(self) -> None:
        """Configure subscriptions and optional relay publishers."""
        for stream_name, enabled in self._config.stream_selection.as_dict(
        ).items():
            if not enabled:
                self.get_logger().debug(
                    f"Stream '{stream_name}' is disabled by configuration."
                )
                continue

            self._configure_stream(stream_name)

    def _configure_stream(self, stream_name: str) -> None:
        """Configure one enabled stream."""
        topic_config = self._config.topics.get(stream_name)

        if topic_config is None:
            raise KeyError(
                f"Stream '{stream_name}' is enabled, but no topic "
                "configuration was found in the YAML file."
            )

        message_class = self._get_message_class(
            message_type=topic_config.message_type,
            stream_name=stream_name,
        )

        if self._config.features.relay_enabled:
            self._relay_publishers[stream_name] = self.create_publisher(
                message_class,
                topic_config.output_topic,
                self._qos,
            )

        subscription = self.create_subscription(
            message_class,
            topic_config.input_topic,
            self._make_callback(stream_name),
            self._qos,
            callback_group=self._callback_group,
        )

        self._stream_subscriptions.append(subscription)
        self._state.register_topic(stream_name)

        self._log_stream_configuration(
            stream_name=stream_name,
            input_topic=topic_config.input_topic,
            output_topic=topic_config.output_topic,
        )

    def _get_message_class(self, message_type: str, stream_name: str) -> type:
        """Return the ROS message class for a configured message type."""
        message_class = MESSAGE_TYPES.get(message_type)

        if message_class is not None:
            return message_class

        supported_types = ", ".join(sorted(MESSAGE_TYPES.keys()))
        raise ValueError(
            f"Unsupported message type '{message_type}' "
            f"for stream '{stream_name}'. Supported types: {supported_types}"
        )

    def _log_stream_configuration(
        self,
        stream_name: str,
        input_topic: str,
        output_topic: str,
    ) -> None:
        """Log subscription and relay information for one stream."""
        self.get_logger().info(
            f"Subscribed to {input_topic} as stream '{stream_name}'."
        )

        if self._config.features.relay_enabled:
            self.get_logger().info(
                f"Relaying stream '{stream_name}' to {output_topic}."
            )

    def _make_callback(self, stream_name: str) -> Callable[[Any], None]:
        """Create a subscription callback for one stream."""

        def callback(message: Any) -> None:
            self._latest_messages[stream_name] = message
            self._state.update_topic(stream_name)

            publisher = self._relay_publishers.get(stream_name)
            if publisher is not None:
                publisher.publish(message)

        return callback

    def _publish_diagnostics(self) -> None:
        """Publish stream health diagnostics to logs and diagnostic topic."""
        diagnostic_statuses = []
        status_parts = []

        for stream_name, health in self._state.topics.items():
            stream_status = health.get_status(
                timeout_sec=self._config.runtime.expected_timeout_sec,
            )
            frequency_hz = health.get_estimated_frequency_hz()
            message_age_sec = health.get_time_since_last_message_sec()

            status_parts.append(
                self._format_stream_status(
                    stream_name=stream_name,
                    status=stream_status,
                    message_count=health.message_count,
                    frequency_hz=frequency_hz,
                    message_age_sec=message_age_sec,
                )
            )

            diagnostic_statuses.append(
                self._make_stream_diagnostic_status(
                    stream_name=stream_name,
                    status=stream_status,
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
        """Create one diagnostic status entry for a stream."""
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
                value=self._format_optional_float(frequency_hz),
            ),
            KeyValue(
                key="message_age_sec",
                value=self._format_optional_float(message_age_sec),
            ),
        ]

        return diagnostic_status

    @staticmethod
    def _format_stream_status(
        stream_name: str,
        status: str,
        message_count: int,
        frequency_hz: float | None,
        message_age_sec: float | None,
    ) -> str:
        """Format one stream health entry for log output."""
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

        return (
            f"{stream_name}={status}, "
            f"count={message_count}, "
            f"hz={frequency_text}, "
            f"age={message_age_text}"
        )

    @staticmethod
    def _format_optional_float(value: float | None) -> str:
        """Format an optional float value for diagnostics."""
        if value is None:
            return "N/A"

        return f"{value:.2f}"

    @staticmethod
    def _get_diagnostic_level(status: str) -> int:
        """Map internal stream status to ROS diagnostic level."""
        if status == TOPIC_STATUS_OK:
            return DiagnosticStatus.OK

        if status == TOPIC_STATUS_STALE:
            return DiagnosticStatus.WARN

        return DiagnosticStatus.ERROR

    def _publish_diagnostics_message(
        self,
        diagnostic_statuses: list[DiagnosticStatus],
    ) -> None:
        """Publish a ROS diagnostic array message."""
        diagnostics_message = DiagnosticArray()
        diagnostics_message.header.stamp = self.get_clock().now().to_msg()
        diagnostics_message.status = diagnostic_statuses

        if self._diagnostics_publisher is not None:
            self._diagnostics_publisher.publish(diagnostics_message)


def _read_config_path_from_ros_parameter() -> str:
    """Read the ZED2i configuration path from a temporary ROS 2 node.

    Returns:
        Configuration path read from the ROS parameter ``config_path``.

    Raises:
        RuntimeError: If the parameter is empty.
    """
    temporary_node = rclpy.create_node(CONFIG_LOADER_NODE_NAME)

    try:
        temporary_node.declare_parameter(CONFIG_PATH_PARAMETER, "")
        config_path = temporary_node.get_parameter(CONFIG_PATH_PARAMETER).value
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
    """Run the ZED2i ROS 2 node."""
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
