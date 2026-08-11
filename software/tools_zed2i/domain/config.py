from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class TopicConfig:
    input_topic: str
    output_topic: str
    message_type: str


@dataclass(frozen=True)
class FeatureConfig:
    left_image: bool
    right_image: bool
    disparity: bool
    imu: bool
    point_cloud: bool
    relay_enabled: bool


@dataclass(frozen=True)
class RuntimeConfig:
    qos_profile: str
    diagnostics_period_sec: float
    expected_timeout_sec: float
    enable_intra_process: bool


@dataclass(frozen=True)
class Zed2iConfig:
    camera_model: str
    camera_name: str
    node_name: str
    input_namespace: str
    output_namespace: str
    features: FeatureConfig
    topics: dict[str, TopicConfig]
    runtime: RuntimeConfig

    @staticmethod
    def from_yaml(config_path: str | Path) -> Zed2iConfig:
        path = Path(config_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with path.open("r", encoding="utf-8") as config_file:
            raw_config: dict[str, Any] = yaml.safe_load(config_file)

        zed_config = raw_config["zed"]
        feature_config = raw_config["features"]
        runtime_config = raw_config["runtime"]
        topics_config = raw_config["topics"]

        topics = {
            name: TopicConfig(
                input_topic=value["input"],
                output_topic=value["output"],
                message_type=value["type"],
            )
            for name, value in topics_config.items()
        }

        return Zed2iConfig(
            camera_model=zed_config["camera_model"],
            camera_name=zed_config["camera_name"],
            node_name=zed_config["node_name"],
            input_namespace=zed_config["input_namespace"],
            output_namespace=zed_config["output_namespace"],
            features=FeatureConfig(**feature_config),
            topics=topics,
            runtime=RuntimeConfig(**runtime_config),
        )