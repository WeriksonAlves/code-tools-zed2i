"""Domain layer for the tools_zed2i package.

This package contains technology-independent models, state containers, and
ports used by the ZED2i application layer.

The domain layer must remain independent from ROS 2, OpenCV, Open3D, file
systems, command-line interfaces, and other infrastructure concerns.
"""

from tools_zed2i.domain.config import (
    DiagnosticsConfig,
    FeatureConfig,
    RuntimeConfig,
    StreamSelectionConfig,
    TopicConfig,
    Zed2iConfig,
)
from tools_zed2i.domain.ports import Zed2iFrameReader, Zed2iLifecycle
from tools_zed2i.domain.snapshot import SensorSnapshot
from tools_zed2i.domain.state import TopicHealth, Zed2iState

__all__ = [
    "DiagnosticsConfig",
    "FeatureConfig",
    "RuntimeConfig",
    "SensorSnapshot",
    "StreamSelectionConfig",
    "TopicConfig",
    "TopicHealth",
    "Zed2iConfig",
    "Zed2iFrameReader",
    "Zed2iLifecycle",
    "Zed2iState",
]
