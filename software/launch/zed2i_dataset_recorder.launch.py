"""Launch file for the tools_zed2i dataset recorder node."""

from __future__ import annotations

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Generate the dataset recorder launch description."""
    config_path = LaunchConfiguration("config_path")
    dataset_root = LaunchConfiguration("dataset_root")
    sequence_name = LaunchConfiguration("sequence_name")
    recording_period_sec = LaunchConfiguration("recording_period_sec")
    recording_enabled = LaunchConfiguration("recording_enabled")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_path",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("tools_zed2i"),
                        "config",
                        "zed2i.yaml",
                    ]
                ),
                description="Path to the tools_zed2i YAML configuration file.",
            ),
            DeclareLaunchArgument(
                "dataset_root",
                default_value="datasets",
                description="Root directory for recorded datasets.",
            ),
            DeclareLaunchArgument(
                "sequence_name",
                default_value="zed2i_sequence",
                description="Dataset sequence name.",
            ),
            DeclareLaunchArgument(
                "recording_period_sec",
                default_value="1.0",
                description="Recording period in seconds.",
            ),
            DeclareLaunchArgument(
                "recording_enabled",
                default_value="true",
                description="Whether periodic dataset recording starts enabled.",
            ),
            Node(
                package="tools_zed2i",
                executable="zed2i_dataset_recorder_node",
                name="tools_zed2i_dataset_recorder_node",
                output="screen",
                parameters=[
                    {
                        "config_path": config_path,
                        "dataset_root": dataset_root,
                        "sequence_name": sequence_name,
                        "recording_period_sec": recording_period_sec,
                        "recording_enabled": recording_enabled,
                    }
                ],
            ),
        ]
    )
