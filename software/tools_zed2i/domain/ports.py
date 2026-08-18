from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from tools_zed2i.domain.snapshot import SensorSnapshot


class Zed2iFrameReader(ABC):
    """Port for reading the latest available ZED2i stream messages."""

    @abstractmethod
    def get_latest_frame(self, stream_name: str) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    def get_sensor_snapshot(self) -> SensorSnapshot:
        raise NotImplementedError


class Zed2iLifecycle(ABC):
    """Port for controlling a ZED2i adapter lifecycle."""

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError
