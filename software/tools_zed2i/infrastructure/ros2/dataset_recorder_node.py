from __future__ import annotations

from pathlib import Path

import rclpy
from rclpy.node import Node

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

        self.get_logger().info(
            "Dataset recorder node started. "
            f"dataset_root={dataset_root}, "
            f"sequence_name={sequence_name}, "
            f"recording_period_sec={recording_period_sec}"
        )

    def update_snapshot(self, snapshot: SensorSnapshot) -> None:
        """Update the latest snapshot to be recorded."""
        self._latest_snapshot = snapshot

    def _record_latest_snapshot(self) -> None:
        if self._latest_snapshot is None:
            self.get_logger().warn("No snapshot available to record yet.")
            return

        if not self._latest_snapshot.available_streams():
            self.get_logger().warn(
                "Snapshot is available, but no streams have been received yet."
            )
            return

        try:
            saved_paths = self._recorder.record_snapshot(self._latest_snapshot)
            self.get_logger().info(
                "Recorded snapshot: "
                f"left={saved_paths.left_image_path}, "
                f"right={saved_paths.right_image_path}, "
                f"disparity={saved_paths.disparity_path}, "
                f"point_cloud={saved_paths.point_cloud_path}, "
                f"metadata={saved_paths.metadata_path}"
            )
        except SnapshotRecorderError as exception:
            self.get_logger().error(str(exception))


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
