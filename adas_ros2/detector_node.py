import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

from ultralytics import YOLO


class DetectorNode(Node):
    def __init__(self):
        super().__init__('detector_node')

        self.bridge = CvBridge()
        self.model = YOLO('yolov8n.pt')

        self.frame_count = 0

        self.subscription = self.create_subscription(
            Image,
            '/camera/image',
            self.image_callback,
            10
        )

        self.publisher_ = self.create_publisher(String, '/detections', 10)

        self.get_logger().info('YOLO detector node started')
        self.get_logger().info('ROI filtering enabled')
        self.get_logger().info('Subscribing: /camera/image')
        self.get_logger().info('Publishing: /detections')

    def is_relevant_roi(self, class_name, x1, y1, x2, y2, frame_width, frame_height):
        road_users = ['person', 'car', 'truck', 'bus', 'motorcycle', 'bicycle']

        if class_name not in road_users:
            return False

        center_x = (x1 + x2) / 2.0
        bottom_y = y2

        cx_norm = center_x / frame_width
        bottom_norm = bottom_y / frame_height

        # Central road zone: ignore objects far left/right
        inside_horizontal_roi = 0.20 <= cx_norm <= 0.80

        # Lower image zone: objects closer to road/ego vehicle
        inside_vertical_roi = bottom_norm >= 0.35

        return inside_horizontal_roi and inside_vertical_roi

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        frame_height, frame_width = frame.shape[:2]

        results = self.model(frame, verbose=False)

        detection_list = []
        total_detections = 0
        kept_detections = 0

        for result in results:
            for box in result.boxes:
                total_detections += 1

                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls_id]

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                x1 = int(x1)
                y1 = int(y1)
                x2 = int(x2)
                y2 = int(y2)

                if conf < 0.25:
                    continue

                if not self.is_relevant_roi(class_name, x1, y1, x2, y2, frame_width, frame_height):
                    continue

                kept_detections += 1

                box_area = max(0, x2 - x1) * max(0, y2 - y1)
                frame_area = frame_width * frame_height
                area_ratio = box_area / frame_area

                center_x = (x1 + x2) / 2.0
                bottom_y = y2

                cx_norm = center_x / frame_width
                bottom_norm = bottom_y / frame_height

                detection_text = (
                    f'{class_name},'
                    f'{conf:.2f},'
                    f'{x1},'
                    f'{y1},'
                    f'{x2},'
                    f'{y2},'
                    f'{area_ratio:.4f},'
                    f'{cx_norm:.4f},'
                    f'{bottom_norm:.4f}'
                )

                detection_list.append(detection_text)

        out_msg = String()
        out_msg.data = '|'.join(detection_list)
        self.publisher_.publish(out_msg)

        self.frame_count += 1

        if self.frame_count % 30 == 0:
            self.get_logger().info(
                f'Frame {self.frame_count}: total={total_detections}, kept_in_roi={kept_detections}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = DetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
