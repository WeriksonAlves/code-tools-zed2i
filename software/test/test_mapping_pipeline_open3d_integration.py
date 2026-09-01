from __future__ import annotations

import importlib.util

import numpy as np
import pytest
from tools_zed2i.application.mapping.preprocessing_pipeline import (
    MappingPreprocessingConfig,
    MappingPreprocessingPipeline,
)

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("open3d") is None,
    reason="Open3D is not installed.",
)


def test_mapping_pipeline_processes_real_open3d_cloud() -> None:
    import open3d as o3d

    points = np.array(
        [
            [0.00, 0.00, 0.00],
            [0.01, 0.00, 0.00],
            [0.02, 0.00, 0.00],
            [1.00, 1.00, 1.00],
            [1.01, 1.00, 1.00],
        ],
        dtype=np.float64,
    )

    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    pipeline = MappingPreprocessingPipeline()

    result = pipeline.run_from_open3d_cloud(
        point_cloud=point_cloud,
        config=MappingPreprocessingConfig(
            voxel_size=0.05,
            nb_neighbors=2,
            std_ratio=2.0,
        ),
    )

    assert len(result.preprocessed_cloud.points) <= len(point_cloud.points)
    assert result.has_plane_segmentation() is False


def test_mapping_pipeline_segments_plane_on_real_open3d_cloud() -> None:
    import open3d as o3d

    points = np.array(
        [
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.5, 0.5, 1.0],
            [0.2, 0.8, 1.0],
        ],
        dtype=np.float64,
    )

    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    pipeline = MappingPreprocessingPipeline()

    result = pipeline.run_from_open3d_cloud(
        point_cloud=point_cloud,
        config=MappingPreprocessingConfig(
            voxel_size=0.01,
            nb_neighbors=2,
            std_ratio=3.0,
            enable_plane_segmentation=True,
            plane_distance_threshold=0.01,
            plane_ransac_n=3,
            plane_num_iterations=100,
        ),
    )

    assert result.has_plane_segmentation() is True
    assert result.plane_segmentation is not None
    assert len(result.plane_segmentation.inlier_indices) >= 3
