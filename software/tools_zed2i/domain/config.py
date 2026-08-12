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
class StreamSelectionConfig:
    left_image: bool
    right_image: bool
    disparity: bool
    imu: bool
    point_cloud: bool


@dataclass(frozen=True)
class FeatureConfig:
    relay_enabled: bool


@dataclass(frozen=True)
class RuntimeConfig:
    qos_profile: str
    diagnostics_period_sec: float
    expected_timeout_sec: float
    enable_intra_process: bool


@dataclass(frozen=True)
class DiagnosticsConfig:
    enabled: bool
    topic: str
    hardware_id: str


@dataclass(frozen=True)
class Zed2iConfig:
    camera_model: str
    camera_name: str
    node_name: str
    input_namespace: str
    output_namespace: str
    active_preset: str
    stream_selection: StreamSelectionConfig
    features: FeatureConfig
    topics: dict[str, TopicConfig]
    runtime: RuntimeConfig
    diagnostics: DiagnosticsConfig

    @staticmethod
    def from_yaml(config_path: str | Path) -> Zed2iConfig:
        path = Path(config_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with path.open("r", encoding="utf-8") as config_file:
            raw_config: dict[str, Any] = yaml.safe_load(config_file)

        zed_config = raw_config["zed"]
        active_preset = raw_config.get("active_preset", "full")
        presets_config = raw_config["presets"]

        if active_preset not in presets_config:
            available_presets = ", ".join(sorted(presets_config.keys()))
            raise ValueError(
                f"Invalid active preset '{active_preset}'. "
                f"Available presets: {available_presets}"
            )

        stream_selection = StreamSelectionConfig(
            **presets_config[active_preset]
        )
        feature_config = FeatureConfig(**raw_config["features"])
        runtime_config = RuntimeConfig(**raw_config["runtime"])
        diagnostics_config = DiagnosticsConfig(
            **raw_config.get(
                "diagnostics",
                {
                    "enabled": False,
                    "topic": "/tools_zed2i/diagnostics",
                    "hardware_id": "zed2i",
                },
            )
        )

        topics_config = raw_config["topics"]

        topics = {
            name: TopicConfig(
                input_topic=value["input"],
                output_topic=value["output"],
                message_type=value["type"],
            )
            for name, value in topics_config.items()
        }

        Zed2iConfig._validate_enabled_streams_have_topics(
            stream_selection=stream_selection,
            topics=topics,
        )

        return Zed2iConfig(
            camera_model=zed_config["camera_model"],
            camera_name=zed_config["camera_name"],
            node_name=zed_config["node_name"],
            input_namespace=zed_config["input_namespace"],
            output_namespace=zed_config["output_namespace"],
            active_preset=active_preset,
            stream_selection=stream_selection,
            features=feature_config,
            topics=topics,
            runtime=runtime_config,
            diagnostics=diagnostics_config,
        )

    @staticmethod
    def _validate_enabled_streams_have_topics(
        stream_selection: StreamSelectionConfig,
        topics: dict[str, TopicConfig],
    ) -> None:
        enabled_streams = {
            "left_image": stream_selection.left_image,
            "right_image": stream_selection.right_image,
            "disparity": stream_selection.disparity,
            "imu": stream_selection.imu,
            "point_cloud": stream_selection.point_cloud,
        }

        missing_topics = [
            stream_name
            for stream_name, enabled in enabled_streams.items()
            if enabled and stream_name not in topics
        ]

        if missing_topics:
            formatted_missing_topics = ", ".join(sorted(missing_topics))
            raise ValueError(
                "Missing topic configuration for enabled streams: "
                f"{formatted_missing_topics}"
            )
