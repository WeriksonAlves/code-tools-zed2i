from __future__ import annotations

import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from stereo_msgs.msg import DisparityImage


class ImageConversionError(RuntimeError):
    """Raised when a ROS image message cannot be converted."""


class RosImageConverter:
    """
    Utility class for converting ROS image messages to NumPy/OpenCV arrays.
    """

    def __init__(self) -> None:
        self._bridge = CvBridge()

    def image_to_cv2(
        self,
        image_message: Image,
        desired_encoding: str = "passthrough",
    ) -> np.ndarray:
        """
        Convert a sensor_msgs/Image message to an OpenCV-compatible array.
        """
        try:
            return self._bridge.imgmsg_to_cv2(
                image_message,
                desired_encoding=desired_encoding,
            )
        except Exception as exception:
            raise ImageConversionError(
                f"Failed to convert ROS Image message: {exception}"
            ) from exception

    def left_image_to_bgr(self, image_message: Image) -> np.ndarray:
        """Convert a left image message to BGR format."""
        return self.image_to_cv2(
            image_message=image_message,
            desired_encoding="bgr8",
        )

    def right_image_to_bgr(self, image_message: Image) -> np.ndarray:
        """Convert a right image message to BGR format."""
        return self.image_to_cv2(
            image_message=image_message,
            desired_encoding="bgr8",
        )

    def image_to_rgb(self, image_message: Image) -> np.ndarray:
        """Convert an image message to RGB format."""
        return self.image_to_cv2(
            image_message=image_message,
            desired_encoding="rgb8",
        )

    def image_to_mono(self, image_message: Image) -> np.ndarray:
        """Convert an image message to mono8 format."""
        return self.image_to_cv2(
            image_message=image_message,
            desired_encoding="mono8",
        )

    def disparity_to_array(
        self,
        disparity_message: DisparityImage,
    ) -> np.ndarray:
        """Convert a stereo_msgs/DisparityImage message to a NumPy array."""
        try:
            disparity_array = self._bridge.imgmsg_to_cv2(
                disparity_message.image,
                desired_encoding="passthrough",
            )
            return np.asarray(disparity_array)
        except Exception as exception:
            raise ImageConversionError(
                f"Failed to convert ROS DisparityImage message: {exception}"
            ) from exception
