from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'adas_ros2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mahdi',
    maintainer_email='mahdi@example.com',
    description='ROS2 ADAS perception pipeline with video publishing, object detection, ROI filtering, risk scoring, alerting, and visualization',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'video_publisher = adas_ros2.video_publisher_node:main',
            'detector = adas_ros2.detector_node:main',
            'risk = adas_ros2.risk_node:main',
            'visualizer = adas_ros2.visualizer_node:main',
        ],
    },
)
