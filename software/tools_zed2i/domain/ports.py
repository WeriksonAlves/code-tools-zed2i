from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Zed2iFrameReader(ABC):
    @abstractmethod
    def get_latest_frame(self, stream_name: str) -> Any | None:
        raise NotImplementedError


class Zed2iLifecycle(ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError