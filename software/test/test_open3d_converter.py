from __future__ import annotations

import sys
from typing import Any

import numpy as np
import pytest

from tools_zed2i.infrastructure.converters.open3d_converter import (
    Open3DConversionError,
    Open3DConverter,
)


class FakePointCloudConverter:
    def pointcloud_to_xyz(self, pointcloud_message: Any) -> np.ndarray:
        return np.array(
            [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
            ],
            dtype=np.float64,
        )


def test_open3d_converter_validates_xyz_shape() -> None:
    converter = Open3DConverter(pointcloud_converter=FakePointCloudConverter())

    with pytest.raises(Open3DConversionError):
        converter.xyz_array_to_open3d(np.array([1.0, 2.0, 3.0]))

    with pytest.raises(Open3DConversionError):
        converter.xyz_array_to_open3d(np.array([[1.0, 2.0]]))


def test_open3d_converter_reports_missing_open3d(monkeypatch: pytest.MonkeyPatch) -> None:
    converter = Open3DConverter(pointcloud_converter=FakePointCloudConverter())

    monkeypatch.setitem(sys.modules, "open3d", None)

    with pytest.raises(Open3DConversionError) as error_info:
        converter.xyz_array_to_open3d(
            np.array(
                [
                    [1.0, 2.0, 3.0],
                ],
                dtype=np.float64,
            )
        )

    assert "Open3D is not installed" in str(error_info.value)
