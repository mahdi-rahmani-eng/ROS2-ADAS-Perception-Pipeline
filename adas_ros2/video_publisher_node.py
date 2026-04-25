import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class VideoPublisherNode(Node):
    def __init__(self):
        super().__init__('video_publisher_node')

        self.publisher_ = self.create_publisher(Image, '/camera/image', 10)
        self.bridge = CvBridge()

        self.video_path = '/home/mahdi/videos/test.mp4'
        self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            self.get_logger().error(f'Could not open video: {self.video_path}')
            return

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 20.0

        self.timer = self.create_timer(1.0 / fps, self.publish_frame)

        self.get_logger().info(f'Video publisher started: {self.video_path}')
        self.get_logger().info('Publishing on topic: /camera/image')

    def publish_frame(self):
        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().info('Video finished. Restarting from beginning.')
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_frame'

        self.publisher_.publish(msg)

    def destroy_node(self):
        if hasattr(self, 'cap'):
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VideoPublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
