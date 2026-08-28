"""Configuration models for the ZED2i domain.

This module defines immutable configuration objects used by the application and
infrastructure layers. The data classes in this file represent domain-level
configuration state.

The ``from_yaml`` factory is kept for backward compatibility. In a stricter
hexagonal architecture, YAML loading should be moved to an infrastructure
adapter, while this module should keep only configuration models and validation
rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tools_zed2i.domain.snapshot import (
    DISPARITY_STREAM,
    IMU_STREAM,
    LEFT_IMAGE_STREAM,
    POINT_CLOUD_STREAM,
    RIGHT_IMAGE_STREAM,
)

DEFAULT_ACTIVE_PRESET = "full"
DEFAULT_DIAGNOSTICS_TOPIC = "/tools_zed2i/diagnostics"
DEFAULT_HARDWARE_ID = "zed2i"


@dataclass(frozen=True)
class TopicConfig:
    """Configuration for one input/output stream topic pair.

    Attributes:
        input_topic: Input topic consumed from the ZED2i source node.
        output_topic: Output topic published by tools_zed2i, when relay is
            enabled.
        message_type: ROS 2 message type identifier.
    """

    input_topic: str
    output_topic: str
    message_type: str


@dataclass(frozen=True)
class StreamSelectionConfig:
    """Configuration indicating which ZED2i streams are enabled."""

    left_image: bool
    right_image: bool
    disparity: bool
    imu: bool
    point_cloud: bool

    def as_dict(self) -> dict[str, bool]:
        """Return enabled/disabled stream flags indexed by stream name."""
        return {
            LEFT_IMAGE_STREAM: self.left_image,
            RIGHT_IMAGE_STREAM: self.right_image,
            DISPARITY_STREAM: self.disparity,
            IMU_STREAM: self.imu,
            POINT_CLOUD_STREAM: self.point_cloud,
        }

    def enabled_streams(self) -> list[str]:
        """Return the names of enabled streams."""
        return [
            stream_name
            for stream_name, enabled in self.as_dict().items()
            if enabled
        ]


@dataclass(frozen=True)
class FeatureConfig:
    """Feature flags for tools_zed2i runtime behavior."""

    relay_enabled: bool


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime configuration for the ZED2i adapter."""

    qos_profile: str
    diagnostics_period_sec: float
    expected_timeout_sec: float
    enable_intra_process: bool


@dataclass(frozen=True)
class DiagnosticsConfig:
    """Diagnostics publisher configuration."""

    enabled: bool
    topic: str
    hardware_id: str


@dataclass(frozen=True)
class Zed2iConfig:
    """Complete ZED2i configuration.

    Attributes:
        camera_model: ZED camera model name.
        camera_name: Logical camera name used by the source node.
        node_name: tools_zed2i ROS 2 node name.
        input_namespace: Namespace of the source ZED2i topics.
        output_namespace: Namespace used by tools_zed2i relay outputs.
        active_preset: Name of the active stream preset.
        stream_selection: Enabled/disabled stream flags.
        features: Runtime feature flags.
        topics: Topic configurations indexed by stream name.
        runtime: Runtime behavior configuration.
        diagnostics: Diagnostics behavior configuration.
    """

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
        """Create a configuration object from a YAML file.

        This method is kept for backward compatibility. Future refactoring
        should move YAML parsing to an infrastructure configuration loader.

        Args:
            config_path: Path to the YAML configuration file.

        Returns:
            Parsed and validated ``Zed2iConfig``.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            TypeError: If the configuration content has an invalid type.
            ValueError: If the configuration content is semantically invalid.
            KeyError: If a required key is missing.
        """
        path = Path(config_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with path.open("r", encoding="utf-8") as config_file:
            raw_config = yaml.safe_load(config_file)

        if not isinstance(raw_config, dict):
            raise TypeError(f"Invalid configuration file content: {path}")

        return Zed2iConfig.from_mapping(raw_config)

    @staticmethod
    def from_mapping(raw_config: dict[str, Any]) -> Zed2iConfig:
        """Create a configuration object from a raw mapping.

        Args:
            raw_config: Raw dictionary containing configuration sections.

        Returns:
            Parsed and validated ``Zed2iConfig``.
        """
        zed_config = raw_config["zed"]
        active_preset = raw_config.get("active_preset", DEFAULT_ACTIVE_PRESET)
        presets_config = raw_config["presets"]

        Zed2iConfig._validate_active_preset(
            active_preset=active_preset,
            presets_config=presets_config,
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
                    "topic": DEFAULT_DIAGNOSTICS_TOPIC,
                    "hardware_id": DEFAULT_HARDWARE_ID,
                },
            )
        )

        topics = Zed2iConfig._parse_topics(raw_config["topics"])

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
    def _parse_topics(
        topics_config: dict[str, dict[str, str]]
    ) -> dict[str, TopicConfig]:
        """Parse topic configuration entries."""
        return {
            name: TopicConfig(
                input_topic=value["input"],
                output_topic=value["output"],
                message_type=value["type"],
            )
            for name, value in topics_config.items()
        }

    @staticmethod
    def _validate_active_preset(
        active_preset: str,
        presets_config: dict[str, Any],
    ) -> None:
        """Validate whether the active preset exists."""
        if active_preset in presets_config:
            return

        available_presets = ", ".join(sorted(presets_config.keys()))
        raise ValueError(
            f"Invalid active preset '{active_preset}'. "
            f"Available presets: {available_presets}"
        )

    @staticmethod
    def _validate_enabled_streams_have_topics(
        stream_selection: StreamSelectionConfig,
        topics: dict[str, TopicConfig],
    ) -> None:
        """Validate that all enabled streams have topic definitions."""
        missing_topics = [
            stream_name
            for stream_name in stream_selection.enabled_streams()
            if stream_name not in topics
        ]

        if missing_topics:
            formatted_missing_topics = ", ".join(sorted(missing_topics))
            raise ValueError(
                "Missing topic configuration for enabled streams: "
                f"{formatted_missing_topics}"
            )
