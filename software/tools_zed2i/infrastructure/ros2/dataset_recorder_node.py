"""ROS 2 node for recording ZED2i datasets from live sensor snapshots.

This module composes the ZED2i acquisition node with a dataset recorder node.
The recorder periodically receives the latest sensor snapshot and writes it to
disk using the application-level dataset recording service.
"""

from __future__ import annotations

from pathlib import Path

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_srvs.srv import Trigger

from tools_zed2i.application.dataset.models.dataset_config import (
    DatasetRecordingConfig,
)
from tools_zed2i.application.dataset.services.snapshot_recorder import (
    SnapshotDatasetRecorder,
    SnapshotRecorderError,
)
from tools_zed2i.domain.snapshot import SensorSnapshot
from tools_zed2i.infrastructure.ros2.zed2i_node import Zed2iRosNode

NODE_NAME = "tools_zed2i_dataset_recorder_node"

DATASET_ROOT_PARAMETER = "dataset_root"
SEQUENCE_NAME_PARAMETER = "sequence_name"
RECORDING_PERIOD_PARAMETER = "recording_period_sec"
SAVE_LEFT_IMAGE_PARAMETER = "save_left_image"
SAVE_RIGHT_IMAGE_PARAMETER = "save_right_image"
SAVE_DISPARITY_PARAMETER = "save_disparity"
SAVE_POINT_CLOUD_PARAMETER = "save_point_cloud"
SAVE_METADATA_PARAMETER = "save_metadata"
RECORDING_ENABLED_PARAMETER = "recording_enabled"

DEFAULT_DATASET_ROOT = "datasets"
DEFAULT_SEQUENCE_NAME = "zed2i_sequence"
DEFAULT_RECORDING_PERIOD_SEC = 1.0
DEFAULT_RECORDING_ENABLED = True

SNAPSHOT_POLLING_PERIOD_SEC = 0.1

START_RECORDING_SERVICE = "start_recording"
STOP_RECORDING_SERVICE = "stop_recording"
RECORD_ONCE_SERVICE = "record_once"


class Zed2iDatasetRecorderNode(Node):
    """ROS 2 node for periodically recording ZED2i sensor snapshots.

    The node exposes services for starting, stopping, and manually triggering
    recording while keeping periodic recording available through a timer.
    """

    def __init__(self) -> None:
        """Initialize the dataset recorder node."""
        super().__init__(NODE_NAME)

        self._declare_parameters()

        recording_config = self._make_recording_config_from_parameters()
        recording_period_sec = self._get_double_parameter(
            RECORDING_PERIOD_PARAMETER,
        )
        self._recording_enabled = self._get_bool_parameter(
            RECORDING_ENABLED_PARAMETER,
        )

        self._recorder = SnapshotDatasetRecorder(config=recording_config)
        self._latest_snapshot: SensorSnapshot | None = None

        self._timer = self.create_timer(
            recording_period_sec,
            self._record_latest_snapshot,
        )

        self._create_services()
        self._log_startup(
            config=recording_config,
            recording_period_sec=recording_period_sec,
        )

    def update_snapshot(self, snapshot: SensorSnapshot) -> None:
        """Update the latest snapshot to be recorded.

        Args:
            snapshot: Latest sensor snapshot read from the ZED2i node.
        """
        self._latest_snapshot = snapshot

    def _declare_parameters(self) -> None:
        """Declare ROS 2 parameters used by the recorder node."""
        self.declare_parameter(DATASET_ROOT_PARAMETER, DEFAULT_DATASET_ROOT)
        self.declare_parameter(SEQUENCE_NAME_PARAMETER, DEFAULT_SEQUENCE_NAME)
        self.declare_parameter(
            RECORDING_PERIOD_PARAMETER,
            DEFAULT_RECORDING_PERIOD_SEC,
        )
        self.declare_parameter(SAVE_LEFT_IMAGE_PARAMETER, True)
        self.declare_parameter(SAVE_RIGHT_IMAGE_PARAMETER, True)
        self.declare_parameter(SAVE_DISPARITY_PARAMETER, True)
        self.declare_parameter(SAVE_POINT_CLOUD_PARAMETER, True)
        self.declare_parameter(SAVE_METADATA_PARAMETER, True)
        self.declare_parameter(
            RECORDING_ENABLED_PARAMETER,
            DEFAULT_RECORDING_ENABLED,
        )

    def _make_recording_config_from_parameters(self) -> DatasetRecordingConfig:
        """Create a dataset recording configuration from ROS parameters."""
        return DatasetRecordingConfig(
            dataset_root=Path(self._get_string_parameter(
                DATASET_ROOT_PARAMETER)),
            sequence_name=self._get_string_parameter(SEQUENCE_NAME_PARAMETER),
            save_left_image=self._get_bool_parameter(
                SAVE_LEFT_IMAGE_PARAMETER),
            save_right_image=self._get_bool_parameter(
                SAVE_RIGHT_IMAGE_PARAMETER),
            save_disparity=self._get_bool_parameter(SAVE_DISPARITY_PARAMETER),
            save_point_cloud=self._get_bool_parameter(
                SAVE_POINT_CLOUD_PARAMETER),
            save_metadata=self._get_bool_parameter(SAVE_METADATA_PARAMETER),
        )

    def _create_services(self) -> None:
        """Create start, stop, and record-once services."""
        service_prefix = self.get_fully_qualified_name()

        self._start_recording_service = self.create_service(
            Trigger,
            f"{service_prefix}/{START_RECORDING_SERVICE}",
            self._handle_start_recording,
        )
        self._stop_recording_service = self.create_service(
            Trigger,
            f"{service_prefix}/{STOP_RECORDING_SERVICE}",
            self._handle_stop_recording,
        )
        self._record_once_service = self.create_service(
            Trigger,
            f"{service_prefix}/{RECORD_ONCE_SERVICE}",
            self._handle_record_once,
        )

    def _record_latest_snapshot(self) -> None:
        """Record the latest snapshot when periodic recording is enabled."""
        if not self._recording_enabled:
            return

        success, message = self._record_snapshot_if_available()
        self._log_recording_result(success=success, message=message)

    def _record_snapshot_if_available(self) -> tuple[bool, str]:
        """Record the latest snapshot if it exists and contains streams."""
        if self._latest_snapshot is None:
            return False, "No snapshot available to record yet."

        if not self._latest_snapshot.available_streams():
            return (
                False,
                "Snapshot is available, but no ",
                "streams have been received yet.",
            )

        try:
            saved_paths = self._recorder.record_snapshot(self._latest_snapshot)
            return True, self._format_recorded_snapshot_message(saved_paths)
        except SnapshotRecorderError as exception:
            return False, str(exception)

    @staticmethod
    def _format_recorded_snapshot_message(saved_paths: object) -> str:
        """Format the output message for a recorded snapshot."""
        return (
            "Recorded snapshot: "
            f"left={saved_paths.left_image_path}, "
            f"right={saved_paths.right_image_path}, "
            f"disparity={saved_paths.disparity_path}, "
            f"point_cloud={saved_paths.point_cloud_path}, "
            f"metadata={saved_paths.metadata_path}"
        )

    def _handle_start_recording(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        """Handle the start-recording service request."""
        del request

        self._recording_enabled = True
        response.success = True
        response.message = "Dataset recording started."

        self.get_logger().info(response.message)

        return response

    def _handle_stop_recording(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        """Handle the stop-recording service request."""
        del request

        self._recording_enabled = False
        response.success = True
        response.message = "Dataset recording stopped."

        self.get_logger().info(response.message)

        return response

    def _handle_record_once(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        """Handle the record-once service request."""
        del request

        success, message = self._record_snapshot_if_available()

        response.success = success
        response.message = message

        self._log_recording_result(success=success, message=message)

        return response

    def _log_recording_result(self, success: bool, message: str) -> None:
        """Log a recording result."""
        if success:
            self.get_logger().info(message)
        else:
            self.get_logger().warning(message)

    def _log_startup(
        self,
        config: DatasetRecordingConfig,
        recording_period_sec: float,
    ) -> None:
        """Log recorder startup configuration."""
        self.get_logger().info(
            "Dataset recorder node started. "
            f"dataset_root={config.dataset_root}, "
            f"sequence_name={config.sequence_name}, "
            f"recording_period_sec={recording_period_sec}, "
            f"recording_enabled={self._recording_enabled}"
        )

    def _get_string_parameter(self, parameter_name: str) -> str:
        """Return a ROS parameter value as string."""
        return (
            self.get_parameter(parameter_name)
            .get_parameter_value()
            .string_value
        )

    def _get_bool_parameter(self, parameter_name: str) -> bool:
        """Return a ROS parameter value as boolean."""
        return (
            self.get_parameter(parameter_name)
            .get_parameter_value()
            .bool_value
        )

    def _get_double_parameter(self, parameter_name: str) -> float:
        """Return a ROS parameter value as float."""
        return (
            self.get_parameter(parameter_name)
            .get_parameter_value()
            .double_value
        )


def main() -> None:
    """Run the composed ZED2i dataset recorder nodes."""
    rclpy.init()

    zed_node = Zed2iRosNode()
    recorder_node = Zed2iDatasetRecorderNode()

    executor = MultiThreadedExecutor()
    executor.add_node(zed_node)
    executor.add_node(recorder_node)

    snapshot_timer = recorder_node.create_timer(
        SNAPSHOT_POLLING_PERIOD_SEC,
        lambda: recorder_node.update_snapshot(zed_node.get_sensor_snapshot()),
    )

    try:
        executor.spin()
    except KeyboardInterrupt:
        recorder_node.get_logger().info("Dataset recorder node interrupted.")
    finally:
        snapshot_timer.cancel()
        executor.shutdown()

        zed_node.destroy_node()
        recorder_node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
