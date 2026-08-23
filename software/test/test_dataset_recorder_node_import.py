from tools_zed2i.infrastructure.ros2.dataset_recorder_node import (
    Zed2iDatasetRecorderNode,
    main,
)


def test_dataset_recorder_node_imports() -> None:
    assert Zed2iDatasetRecorderNode is not None
    assert main is not None
