from pathlib import Path

import pytest
import yaml

from tools_zed2i.domain.config import Zed2iConfig


def test_load_zed2i_config_from_yaml(tmp_path: Path) -> None:
    config_data = {
        "zed": {
            "camera_model": "zed2i",
            "camera_name": "zed",
            "node_name": "tools_zed2i_node",
            "input_namespace": "/zed/zed_node",
            "output_namespace": "/tools_zed2i",
        },
        "features": {
            "left_image": True,
            "right_image": True,
            "disparity": True,
            "imu": True,
            "point_cloud": True,
            "relay_enabled": True,
        },
        "topics": {
            "left_image": {
                "input": "/zed/zed_node/left/image_rect_color",
                "output": "/tools_zed2i/left/image_rect_color",
                "type": "sensor_msgs/msg/Image",
            }
        },
        "runtime": {
            "qos_profile": "sensor_data",
            "diagnostics_period_sec": 1.0,
            "expected_timeout_sec": 2.0,
            "enable_intra_process": True,
        },
    }

    config_path = tmp_path / "zed2i.yaml"

    with config_path.open("w", encoding="utf-8") as config_file:
        yaml.safe_dump(config_data, config_file)

    config = Zed2iConfig.from_yaml(config_path)

    assert config.camera_model == "zed2i"
    assert config.camera_name == "zed"
    assert config.node_name == "tools_zed2i_node"
    assert config.features.left_image is True
    assert config.features.relay_enabled is True
    assert config.topics["left_image"].input_topic == (
        "/zed/zed_node/left/image_rect_color"
    )
    assert config.runtime.qos_profile == "sensor_data"


def test_load_zed2i_config_raises_for_missing_file(tmp_path: Path) -> None:
    missing_config_path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        Zed2iConfig.from_yaml(missing_config_path)
