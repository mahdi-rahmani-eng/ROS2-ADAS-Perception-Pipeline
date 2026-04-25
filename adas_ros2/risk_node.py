import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from std_msgs.msg import Float32


class RiskNode(Node):
    def __init__(self):
        super().__init__('risk_node')

        self.subscription = self.create_subscription(
            String,
            '/detections',
            self.detection_callback,
            10
        )

        self.alert_publisher = self.create_publisher(String, '/alert_level', 10)
        self.score_publisher = self.create_publisher(Float32, '/risk_score', 10)

        self.frame_count = 0

        self.get_logger().info('Risk node started')
        self.get_logger().info('Subscribing: /detections')
        self.get_logger().info('Publishing: /alert_level and /risk_score')

    def compute_object_risk(self, class_name, confidence, area_ratio, bottom_norm):
        risk = 0.0

        # Confidence contribution
        risk += confidence * 35.0

        # Apparent object size contribution
        risk += min(area_ratio * 450.0, 35.0)

        # Lower image position means object is likely closer
        risk += bottom_norm * 20.0

        # Class-specific weights
        if class_name == 'person':
            risk += 20.0
        elif class_name in ['truck', 'bus']:
            risk += 12.0
        elif class_name in ['car', 'motorcycle', 'bicycle']:
            risk += 8.0

        return min(risk, 100.0)

    def risk_to_alert(self, risk_score):
        if risk_score >= 65.0:
            return 'WARNING'
        elif risk_score >= 35.0:
            return 'CAUTION'
        else:
            return 'SAFE'

    def detection_callback(self, msg):
        detections_data = msg.data.strip()

        max_risk = 0.0

        if detections_data:
            detections = detections_data.split('|')

            for detection in detections:
                parts = detection.split(',')

                if len(parts) < 9:
                    continue

                class_name = parts[0]
                confidence = float(parts[1])
                area_ratio = float(parts[6])
                bottom_norm = float(parts[8])

                object_risk = self.compute_object_risk(
                    class_name,
                    confidence,
                    area_ratio,
                    bottom_norm
                )

                if object_risk > max_risk:
                    max_risk = object_risk

        alert = self.risk_to_alert(max_risk)

        alert_msg = String()
        alert_msg.data = alert

        score_msg = Float32()
        score_msg.data = float(max_risk)

        self.alert_publisher.publish(alert_msg)
        self.score_publisher.publish(score_msg)

        self.frame_count += 1

        if self.frame_count % 30 == 0:
            self.get_logger().info(
                f'Frame {self.frame_count}: risk_score={max_risk:.1f}, alert={alert}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = RiskNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
