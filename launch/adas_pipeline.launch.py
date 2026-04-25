from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='adas_ros2',
            executable='video_publisher',
            name='video_publisher_node',
            output='screen'
        ),

        Node(
            package='adas_ros2',
            executable='detector',
            name='detector_node',
            output='screen'
        ),

        Node(
            package='adas_ros2',
            executable='risk',
            name='risk_node',
            output='screen'
        ),

        Node(
            package='adas_ros2',
            executable='visualizer',
            name='visualizer_node',
            output='screen'
        ),
    ])
