from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tools_zed2i.domain.snapshot import SensorSnapshot
from tools_zed2i.infrastructure.converters.image_converter import RosImageConverter


@dataclass(frozen=True)
class ConvertedImageSnapshot:
    """Converted image snapshot with NumPy/OpenCV-compatible arrays."""

    left_image: np.ndarray | None = None
    right_image: np.ndarray | None = None
    disparity: np.ndarray | None = None

    def is_empty(self) -> bool:
        return (
            self.left_image is None
            and self.right_image is None
            and self.disparity is None
        )


class SnapshotConverter:
    """Application-level converter for selected snapshot streams."""

    def __init__(self, image_converter: RosImageConverter | None = None
                 ) -> None:
        self._image_converter = image_converter or RosImageConverter()

    def convert_images_to_bgr(
        self,
        snapshot: SensorSnapshot,
    ) -> ConvertedImageSnapshot:
        """
        Convert available image streams in a sensor snapshot to BGR arrays.
        """
        left_image = None
        right_image = None
        disparity = None

        if snapshot.left_image is not None:
            left_image = self._image_converter.left_image_to_bgr(
                snapshot.left_image)

        if snapshot.right_image is not None:
            right_image = self._image_converter.right_image_to_bgr(
                snapshot.right_image)

        if snapshot.disparity is not None:
            disparity = self._image_converter.disparity_to_array(
                snapshot.disparity)

        return ConvertedImageSnapshot(
            left_image=left_image,
            right_image=right_image,
            disparity=disparity,
        )
