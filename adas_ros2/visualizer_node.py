import cv2
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String
from std_msgs.msg import Float32
from cv_bridge import CvBridge


class VisualizerNode(Node):
    def __init__(self):
        super().__init__('visualizer_node')

        self.bridge = CvBridge()

        self.latest_detections = ''
        self.latest_alert = 'SAFE'
        self.latest_risk_score = 0.0

        self.output_path = '/home/mahdi/ros2_ws/adas_output.mp4'
        self.video_writer = None
        self.frame_count = 0

        self.image_subscriber = self.create_subscription(
            Image,
            '/camera/image',
            self.image_callback,
            10
        )

        self.detection_subscriber = self.create_subscription(
            String,
            '/detections',
            self.detection_callback,
            10
        )

        self.alert_subscriber = self.create_subscription(
            String,
            '/alert_level',
            self.alert_callback,
            10
        )

        self.score_subscriber = self.create_subscription(
            Float32,
            '/risk_score',
            self.score_callback,
            10
        )

        self.get_logger().info('Visualizer node started')
        self.get_logger().info('Saving output video to: /home/mahdi/ros2_ws/adas_output.mp4')

    def detection_callback(self, msg):
        self.latest_detections = msg.data

    def alert_callback(self, msg):
        self.latest_alert = msg.data

    def score_callback(self, msg):
        self.latest_risk_score = msg.data

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        frame = self.draw_detections(frame)
        frame = self.draw_alert(frame)

        if self.video_writer is None:
            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                self.output_path,
                fourcc,
                20.0,
                (width, height)
            )

        self.video_writer.write(frame)
        self.frame_count += 1

        if self.frame_count % 60 == 0:
            self.get_logger().info(
                f'Saved {self.frame_count} frames | Alert={self.latest_alert} | Risk={self.latest_risk_score:.1f}'
            )

    def draw_detections(self, frame):
        detections_data = self.latest_detections.strip()

        if not detections_data:
            return frame

        detections = detections_data.split('|')

        for detection in detections:
            parts = detection.split(',')

            if len(parts) < 6:
                continue

            class_name = parts[0]
            confidence = float(parts[1])
            x1 = int(parts[2])
            y1 = int(parts[3])
            x2 = int(parts[4])
            y2 = int(parts[5])

            label = f'{class_name} {confidence:.2f}'

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        return frame

    def draw_alert(self, frame):
        alert = self.latest_alert
        score = self.latest_risk_score

        if alert == 'SAFE':
            color = (0, 255, 0)
        elif alert == 'CAUTION':
            color = (0, 255, 255)
        else:
            color = (0, 0, 255)

        cv2.rectangle(frame, (20, 20), (500, 110), (0, 0, 0), -1)

        cv2.putText(
            frame,
            f'ADAS ALERT: {alert}',
            (35, 58),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2
        )

        cv2.putText(
            frame,
            f'Risk Score: {score:.1f}/100',
            (35, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

        return frame

    def destroy_node(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.get_logger().info(f'Output video saved: {self.output_path}')

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VisualizerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
