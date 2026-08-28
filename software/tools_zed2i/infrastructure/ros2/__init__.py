"""ROS 2 infrastructure adapters for tools_zed2i.

This package contains ROS 2 nodes responsible for acquiring ZED2i sensor
streams, relaying configured topics, publishing diagnostics, and recording
datasets from live snapshots.

The ROS 2 layer is an infrastructure adapter. It should depend on the domain
and application layers, but domain/application modules should not depend on
ROS 2.
"""

from tools_zed2i.infrastructure.ros2.dataset_recorder_node import (
    Zed2iDatasetRecorderNode,
)
from tools_zed2i.infrastructure.ros2.zed2i_node import Zed2iRosNode

__all__ = [
    "Zed2iDatasetRecorderNode",
    "Zed2iRosNode",
]
