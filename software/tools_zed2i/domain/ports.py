"""Domain ports for ZED2i adapters.

Ports define contracts that must be implemented by infrastructure adapters.
They allow the application layer to depend on abstractions instead of concrete
technologies such as ROS 2 nodes, hardware drivers, or file-system components.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from tools_zed2i.domain.snapshot import SensorSnapshot


class Zed2iFrameReader(ABC):
    """Port for reading the latest available ZED2i stream payloads."""

    @abstractmethod
    def get_latest_frame(self, stream_name: str) -> Any | None:
        """Return the latest payload for a stream.

        Args:
            stream_name: Logical stream name, such as ``left_image``,
                ``right_image``, ``imu``, or ``point_cloud``.

        Returns:
            Latest stream payload, or ``None`` if no payload is available.
        """
        raise NotImplementedError

    @abstractmethod
    def get_sensor_snapshot(self) -> SensorSnapshot:
        """Return an immutable snapshot with the latest available streams."""
        raise NotImplementedError


class Zed2iLifecycle(ABC):
    """Port for controlling the lifecycle of a ZED2i adapter."""

    @abstractmethod
    def start(self) -> None:
        """Start the adapter."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Stop the adapter and release associated resources."""
        raise NotImplementedError
