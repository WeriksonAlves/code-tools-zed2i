from pathlib import Path
from typing import Any

import pytest
import yaml

from tools_zed2i.domain.config import Zed2iConfig


def _make_config_data(active_preset: str = "mapping") -> dict[str, Any]:
    return {
        "zed": {
            "camera_model": "zed2i",
            "camera_name": "zed",
            "node_name": "tools_zed2i_node",
            "input_namespace": "/zed/zed_node",
            "output_namespace": "/tools_zed2i",
        },
        "active_preset": active_preset,
        "features": {
            "relay_enabled": True,
        },
        "presets": {
            "minimal": {
                "left_image": True,
                "right_image": False,
                "disparity": False,
                "imu": True,
                "point_cloud": False,
            },
            "mapping": {
                "left_image": True,
                "right_image": True,
                "disparity": True,
                "imu": True,
                "point_cloud": True,
            },
        },
        "topics": {
            "left_image": {
                "input": "/zed/zed_node/left/image_rect_color",
                "output": "/tools_zed2i/left/image_rect_color",
                "type": "sensor_msgs/msg/Image",
            },
            "right_image": {
                "input": "/zed/zed_node/right/image_rect_color",
                "output": "/tools_zed2i/right/image_rect_color",
                "type": "sensor_msgs/msg/Image",
            },
            "disparity": {
                "input": "/zed/zed_node/disparity/disparity_image",
                "output": "/tools_zed2i/disparity/disparity_image",
                "type": "stereo_msgs/msg/DisparityImage",
            },
            "imu": {
                "input": "/zed/zed_node/imu/data",
                "output": "/tools_zed2i/imu/data",
                "type": "sensor_msgs/msg/Imu",
            },
            "point_cloud": {
                "input": "/zed/zed_node/point_cloud/cloud_registered",
                "output": "/tools_zed2i/point_cloud/cloud_registered",
                "type": "sensor_msgs/msg/PointCloud2",
            },
        },
        "runtime": {
            "qos_profile": "sensor_data",
            "diagnostics_period_sec": 1.0,
            "expected_timeout_sec": 2.0,
            "enable_intra_process": True,
        },
    }


def _write_config(tmp_path: Path, config_data: dict[str, Any]) -> Path:
    config_path = tmp_path / "zed2i.yaml"

    with config_path.open("w", encoding="utf-8") as config_file:
        yaml.safe_dump(config_data, config_file)

    return config_path


def test_load_zed2i_config_from_yaml(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, _make_config_data())

    config = Zed2iConfig.from_yaml(config_path)

    assert config.camera_model == "zed2i"
    assert config.camera_name == "zed"
    assert config.node_name == "tools_zed2i_node"
    assert config.active_preset == "mapping"
    assert config.features.relay_enabled is True
    assert config.stream_selection.left_image is True
    assert config.stream_selection.right_image is True
    assert config.stream_selection.disparity is True
    assert config.stream_selection.imu is True
    assert config.stream_selection.point_cloud is True
    assert config.topics["left_image"].input_topic == (
        "/zed/zed_node/left/image_rect_color"
    )
    assert config.runtime.qos_profile == "sensor_data"


def test_load_zed2i_config_with_minimal_preset(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, _make_config_data(active_preset="minimal"))

    config = Zed2iConfig.from_yaml(config_path)

    assert config.active_preset == "minimal"
    assert config.stream_selection.left_image is True
    assert config.stream_selection.right_image is False
    assert config.stream_selection.disparity is False
    assert config.stream_selection.imu is True
    assert config.stream_selection.point_cloud is False


def test_load_zed2i_config_raises_for_missing_file(tmp_path: Path) -> None:
    missing_config_path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        Zed2iConfig.from_yaml(missing_config_path)


def test_load_zed2i_config_raises_for_invalid_preset(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _make_config_data(active_preset="invalid_preset"),
    )

    with pytest.raises(ValueError, match="Invalid active preset"):
        Zed2iConfig.from_yaml(config_path)


def test_load_zed2i_config_raises_for_missing_enabled_topic(
    tmp_path: Path,
) -> None:
    config_data = _make_config_data(active_preset="mapping")
    del config_data["topics"]["point_cloud"]

    config_path = _write_config(tmp_path, config_data)

    with pytest.raises(ValueError, match="Missing topic configuration"):
        Zed2iConfig.from_yaml(config_path)