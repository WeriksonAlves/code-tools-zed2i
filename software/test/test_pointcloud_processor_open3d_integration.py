from __future__ import annotations

import importlib.util

import numpy as np
import pytest

from tools_zed2i.application.pointcloud.pointcloud_processor import (
    Open3DPointCloudProcessor,
)

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("open3d") is None,
    reason="Open3D is not installed.",
)


def test_pointcloud_processor_downsamples_real_open3d_cloud() -> None:
    import open3d as o3d

    points = np.array(
        [
            [0.00, 0.00, 0.00],
            [0.01, 0.00, 0.00],
            [1.00, 1.00, 1.00],
        ],
        dtype=np.float64,
    )

    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    processor = Open3DPointCloudProcessor()

    downsampled_cloud = processor.voxel_downsample(
        point_cloud,
        voxel_size=0.05,
    )

    assert len(downsampled_cloud.points) <= len(point_cloud.points)


def test_pointcloud_processor_segments_real_plane() -> None:
    import open3d as o3d

    plane_points = np.array(
        [
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.5, 0.5, 1.0],
        ],
        dtype=np.float64,
    )

    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(plane_points)

    processor = Open3DPointCloudProcessor()

    result = processor.segment_plane(
        point_cloud,
        distance_threshold=0.01,
        ransac_n=3,
        num_iterations=100,
    )

    assert len(result.inlier_indices) == len(plane_points)
    assert len(result.inlier_cloud.points) == len(plane_points)
    assert len(result.outlier_cloud.points) == 0
