from __future__ import annotations

from pathlib import Path

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

from tools_zed2i.application.dataset.dataset_config import DatasetRecordingConfig
from tools_zed2i.application.dataset.snapshot_recorder import (
    SnapshotDatasetRecorder,
    SnapshotRecorderError,
)
from tools_zed2i.domain.snapshot import SensorSnapshot
from tools_zed2i.infrastructure.ros2.zed2i_node import Zed2iRosNode


class Zed2iDatasetRecorderNode(Node):
    """ROS 2 node for periodically recording ZED2i sensor snapshots."""

    def __init__(self) -> None:
        super().__init__("tools_zed2i_dataset_recorder_node")

        self.declare_parameter("dataset_root", "datasets")
        self.declare_parameter("sequence_name", "zed2i_sequence")
        self.declare_parameter("recording_period_sec", 1.0)
        self.declare_parameter("save_left_image", True)
        self.declare_parameter("save_right_image", True)
        self.declare_parameter("save_disparity", True)
        self.declare_parameter("save_point_cloud", True)
        self.declare_parameter("save_metadata", True)
        self.declare_parameter("recording_enabled", True)

        dataset_root = Path(
            self.get_parameter("dataset_root").get_parameter_value().string_value
        )
        sequence_name = (
            self.get_parameter("sequence_name").get_parameter_value().string_value
        )
        recording_period_sec = (
            self.get_parameter("recording_period_sec")
            .get_parameter_value()
            .double_value
        )

        self._recording_enabled = (
            self.get_parameter("recording_enabled").get_parameter_value().bool_value
        )

        config = DatasetRecordingConfig(
            dataset_root=dataset_root,
            sequence_name=sequence_name,
            save_left_image=(
                self.get_parameter("save_left_image")
                .get_parameter_value()
                .bool_value
            ),
            save_right_image=(
                self.get_parameter("save_right_image")
                .get_parameter_value()
                .bool_value
            ),
            save_disparity=(
                self.get_parameter("save_disparity")
                .get_parameter_value()
                .bool_value
            ),
            save_point_cloud=(
                self.get_parameter("save_point_cloud")
                .get_parameter_value()
                .bool_value
            ),
            save_metadata=(
                self.get_parameter("save_metadata")
                .get_parameter_value()
                .bool_value
            ),
        )

        self._recorder = SnapshotDatasetRecorder(config=config)
        self._latest_snapshot: SensorSnapshot | None = None

        self._timer = self.create_timer(
            recording_period_sec,
            self._record_latest_snapshot,
        )

        service_prefix = self.get_fully_qualified_name()

        self._start_recording_service = self.create_service(
            Trigger,
            f"{service_prefix}/start_recording",
            self._handle_start_recording,
        )
        self._stop_recording_service = self.create_service(
            Trigger,
            f"{service_prefix}/stop_recording",
            self._handle_stop_recording,
        )
        self._record_once_service = self.create_service(
            Trigger,
            f"{service_prefix}/record_once",
            self._handle_record_once,
        )

        self.get_logger().info(
            "Dataset recorder node started. "
            f"dataset_root={dataset_root}, "
            f"sequence_name={sequence_name}, "
            f"recording_period_sec={recording_period_sec}, "
            f"recording_enabled={self._recording_enabled}"
        )

    def update_snapshot(self, snapshot: SensorSnapshot) -> None:
        """Update the latest snapshot to be recorded."""
        self._latest_snapshot = snapshot

    def _record_latest_snapshot(self) -> None:
        if not self._recording_enabled:
            return

        success, message = self._record_snapshot_if_available()

        if success:
            self.get_logger().info(message)
        else:
            self.get_logger().warn(message)

    def _record_snapshot_if_available(self) -> tuple[bool, str]:
        if self._latest_snapshot is None:
            return False, "No snapshot available to record yet."

        if not self._latest_snapshot.available_streams():
            return (
                False,
                "Snapshot is available, but no streams have been received yet.",
            )

        try:
            saved_paths = self._recorder.record_snapshot(self._latest_snapshot)

            return (
                True,
                (
                    "Recorded snapshot: "
                    f"left={saved_paths.left_image_path}, "
                    f"right={saved_paths.right_image_path}, "
                    f"disparity={saved_paths.disparity_path}, "
                    f"point_cloud={saved_paths.point_cloud_path}, "
                    f"metadata={saved_paths.metadata_path}"
                ),
            )
        except SnapshotRecorderError as exception:
            return False, str(exception)

    def _handle_start_recording(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
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
        del request

        success, message = self._record_snapshot_if_available()

        response.success = success
        response.message = message

        if success:
            self.get_logger().info(message)
        else:
            self.get_logger().warn(message)

        return response


def main() -> None:
    rclpy.init()

    zed_node = Zed2iRosNode()
    recorder_node = Zed2iDatasetRecorderNode()

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(zed_node)
    executor.add_node(recorder_node)

    snapshot_timer = recorder_node.create_timer(
        0.1,
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
