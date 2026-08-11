from __future__ import annotations

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    config_path = LaunchConfiguration("config_path")
    camera_model = LaunchConfiguration("camera_model")

    zed_wrapper_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("zed_wrapper"),
                    "launch",
                    "zed_camera.launch.py",
                ]
            )
        ),
        launch_arguments={
            "camera_model": camera_model,
        }.items(),
    )

    tools_zed2i_node = Node(
        package="tools_zed2i",
        executable="zed2i_node",
        name="tools_zed2i_node",
        output="screen",
        parameters=[
            {
                "config_path": config_path,
            }
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "camera_model",
                default_value="zed2i",
                description="ZED camera model.",
            ),
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
            zed_wrapper_launch,
            tools_zed2i_node,
        ]
    )