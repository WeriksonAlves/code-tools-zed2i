from __future__ import annotations

from typing import Any

import pytest

from tools_zed2i.application.mapping_pipeline import (
    MappingPipelineError,
    MappingPreprocessingConfig,
    MappingPreprocessingPipeline,
)
from tools_zed2i.application.pointcloud_processor import PlaneSegmentationResult
from tools_zed2i.domain.snapshot import SensorSnapshot


class FakeOpen3DConverter:
    def pointcloud_message_to_open3d(self, pointcloud_message: Any) -> str:
        return f"open3d:{pointcloud_message}"


class FakePointCloudProcessor:
    def preprocess_for_mapping(
        self,
        point_cloud: Any,
        voxel_size: float,
        nb_neighbors: int,
        std_ratio: float,
    ) -> str:
        return (
            f"preprocessed:{point_cloud}:"
            f"{voxel_size}:{nb_neighbors}:{std_ratio}"
        )

    def segment_plane(
        self,
        point_cloud: Any,
        distance_threshold: float,
        ransac_n: int,
        num_iterations: int,
    ) -> PlaneSegmentationResult:
        return PlaneSegmentationResult(
            plane_model=(0.0, 0.0, 1.0, -1.0),
            inlier_indices=[0, 1, 2],
            inlier_cloud=f"inliers:{point_cloud}",
            outlier_cloud=f"outliers:{point_cloud}",
        )


def test_mapping_pipeline_runs_from_snapshot() -> None:
    pipeline = MappingPreprocessingPipeline(
        open3d_converter=FakeOpen3DConverter(),
        pointcloud_processor=FakePointCloudProcessor(),
    )

    snapshot = SensorSnapshot(point_cloud="pointcloud_message")

    result = pipeline.run_from_snapshot(snapshot)

    assert result.raw_cloud == "open3d:pointcloud_message"
    assert result.preprocessed_cloud == (
        "preprocessed:open3d:pointcloud_message:0.05:30:2.0"
    )
    assert result.has_plane_segmentation() is False


def test_mapping_pipeline_rejects_snapshot_without_point_cloud() -> None:
    pipeline = MappingPreprocessingPipeline(
        open3d_converter=FakeOpen3DConverter(),
        pointcloud_processor=FakePointCloudProcessor(),
    )

    with pytest.raises(MappingPipelineError):
        pipeline.run_from_snapshot(SensorSnapshot())


def test_mapping_pipeline_runs_from_pointcloud_message() -> None:
    pipeline = MappingPreprocessingPipeline(
        open3d_converter=FakeOpen3DConverter(),
        pointcloud_processor=FakePointCloudProcessor(),
    )

    result = pipeline.run_from_pointcloud_message("pointcloud_message")

    assert result.raw_cloud == "open3d:pointcloud_message"
    assert result.preprocessed_cloud == (
        "preprocessed:open3d:pointcloud_message:0.05:30:2.0"
    )


def test_mapping_pipeline_runs_from_open3d_cloud() -> None:
    pipeline = MappingPreprocessingPipeline(
        open3d_converter=FakeOpen3DConverter(),
        pointcloud_processor=FakePointCloudProcessor(),
    )

    result = pipeline.run_from_open3d_cloud("open3d_cloud")

    assert result.raw_cloud == "open3d_cloud"
    assert result.preprocessed_cloud == (
        "preprocessed:open3d_cloud:0.05:30:2.0"
    )


def test_mapping_pipeline_uses_custom_config() -> None:
    pipeline = MappingPreprocessingPipeline(
        open3d_converter=FakeOpen3DConverter(),
        pointcloud_processor=FakePointCloudProcessor(),
    )

    config = MappingPreprocessingConfig(
        voxel_size=0.10,
        nb_neighbors=20,
        std_ratio=1.5,
    )

    result = pipeline.run_from_pointcloud_message(
        pointcloud_message="pointcloud_message",
        config=config,
    )

    assert result.preprocessed_cloud == (
        "preprocessed:open3d:pointcloud_message:0.1:20:1.5"
    )


def test_mapping_pipeline_runs_plane_segmentation_when_enabled() -> None:
    pipeline = MappingPreprocessingPipeline(
        open3d_converter=FakeOpen3DConverter(),
        pointcloud_processor=FakePointCloudProcessor(),
    )

    config = MappingPreprocessingConfig(enable_plane_segmentation=True)

    result = pipeline.run_from_pointcloud_message(
        pointcloud_message="pointcloud_message",
        config=config,
    )

    assert result.has_plane_segmentation() is True
    assert result.plane_segmentation is not None
    assert result.plane_segmentation.plane_model == (0.0, 0.0, 1.0, -1.0)
    assert result.plane_segmentation.inlier_indices == [0, 1, 2]
