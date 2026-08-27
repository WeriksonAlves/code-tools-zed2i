from __future__ import annotations

from typing import Any

import pytest

from tools_zed2i.application.pointcloud import (
    Open3DPointCloudProcessor,
    PlaneSegmentationResult,
    PointCloudProcessingError,
)


class FakeOpen3DPointCloud:
    def __init__(self, name: str = "cloud") -> None:
        self.name = name
        self.operations: list[str] = []

    def voxel_down_sample(self, voxel_size: float) -> FakeOpen3DPointCloud:
        result = FakeOpen3DPointCloud(name=f"{self.name}_voxel")
        result.operations = [*self.operations, f"voxel:{voxel_size}"]
        return result

    def remove_statistical_outlier(
        self,
        nb_neighbors: int,
        std_ratio: float,
    ) -> tuple[FakeOpen3DPointCloud, list[int]]:
        result = FakeOpen3DPointCloud(name=f"{self.name}_sor")
        result.operations = [
            *self.operations,
            f"sor:{nb_neighbors}:{std_ratio}",
        ]
        return result, [0, 1]

    def remove_radius_outlier(
        self,
        nb_points: int,
        radius: float,
    ) -> tuple[FakeOpen3DPointCloud, list[int]]:
        result = FakeOpen3DPointCloud(name=f"{self.name}_ror")
        result.operations = [
            *self.operations,
            f"ror:{nb_points}:{radius}",
        ]
        return result, [0, 1]

    def segment_plane(
        self,
        distance_threshold: float,
        ransac_n: int,
        num_iterations: int,
    ) -> tuple[tuple[float, float, float, float], list[int]]:
        self.operations.append(
            f"plane:{distance_threshold}:{ransac_n}:{num_iterations}"
        )
        return (0.0, 0.0, 1.0, -1.5), [0, 1, 2]

    def select_by_index(
        self,
        indices: list[int],
        invert: bool = False,
    ) -> FakeOpen3DPointCloud:
        suffix = "outliers" if invert else "inliers"
        result = FakeOpen3DPointCloud(name=f"{self.name}_{suffix}")
        result.operations = [*self.operations, f"select:{indices}:{invert}"]
        return result


class FailingPointCloud:
    def voxel_down_sample(self, voxel_size: float) -> Any:
        raise RuntimeError("forced failure")


def test_pointcloud_processor_voxel_downsamples_cloud() -> None:
    processor = Open3DPointCloudProcessor()
    point_cloud = FakeOpen3DPointCloud()

    result = processor.voxel_downsample(point_cloud, voxel_size=0.05)

    assert result.name == "cloud_voxel"
    assert result.operations == ["voxel:0.05"]


def test_pointcloud_processor_removes_statistical_outliers() -> None:
    processor = Open3DPointCloudProcessor()
    point_cloud = FakeOpen3DPointCloud()

    result = processor.remove_statistical_outliers(
        point_cloud,
        nb_neighbors=30,
        std_ratio=2.0,
    )

    assert result.name == "cloud_sor"
    assert result.operations == ["sor:30:2.0"]


def test_pointcloud_processor_removes_radius_outliers() -> None:
    processor = Open3DPointCloudProcessor()
    point_cloud = FakeOpen3DPointCloud()

    result = processor.remove_radius_outliers(
        point_cloud,
        nb_points=16,
        radius=0.1,
    )

    assert result.name == "cloud_ror"
    assert result.operations == ["ror:16:0.1"]


def test_pointcloud_processor_segments_plane() -> None:
    processor = Open3DPointCloudProcessor()
    point_cloud = FakeOpen3DPointCloud()

    result = processor.segment_plane(
        point_cloud,
        distance_threshold=0.05,
        ransac_n=3,
        num_iterations=1000,
    )

    assert isinstance(result, PlaneSegmentationResult)
    assert result.plane_model == (0.0, 0.0, 1.0, -1.5)
    assert result.inlier_indices == [0, 1, 2]
    assert result.inlier_cloud.name == "cloud_inliers"
    assert result.outlier_cloud.name == "cloud_outliers"


def test_pointcloud_processor_preprocesses_for_mapping() -> None:
    processor = Open3DPointCloudProcessor()
    point_cloud = FakeOpen3DPointCloud()

    result = processor.preprocess_for_mapping(
        point_cloud,
        voxel_size=0.05,
        nb_neighbors=30,
        std_ratio=2.0,
    )

    assert result.name == "cloud_voxel_sor"
    assert result.operations == ["voxel:0.05", "sor:30:2.0"]


@pytest.mark.parametrize(
    ("method_name", "kwargs"),
    [
        ("voxel_downsample", {"voxel_size": 0.0}),
        ("remove_statistical_outliers", {"nb_neighbors": 0}),
        ("remove_statistical_outliers", {"std_ratio": 0.0}),
        ("remove_radius_outliers", {"nb_points": 0}),
        ("remove_radius_outliers", {"radius": 0.0}),
        ("segment_plane", {"distance_threshold": 0.0}),
        ("segment_plane", {"ransac_n": 0}),
        ("segment_plane", {"num_iterations": 0}),
    ],
)
def test_pointcloud_processor_rejects_invalid_parameters(
    method_name: str,
    kwargs: dict[str, float | int],
) -> None:
    processor = Open3DPointCloudProcessor()
    point_cloud = FakeOpen3DPointCloud()

    method = getattr(processor, method_name)

    with pytest.raises(PointCloudProcessingError):
        method(point_cloud, **kwargs)


def test_pointcloud_processor_wraps_processing_errors() -> None:
    processor = Open3DPointCloudProcessor()

    with pytest.raises(PointCloudProcessingError) as error_info:
        processor.voxel_downsample(FailingPointCloud(), voxel_size=0.05)

    assert "Failed to downsample point cloud" in str(error_info.value)
