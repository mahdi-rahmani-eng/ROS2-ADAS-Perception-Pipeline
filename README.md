# ROS2-Based ADAS Perception Pipeline

A modular **ROS2-based Advanced Driver Assistance System (ADAS) perception pipeline** built with **ROS2 Humble**, **Python**, **OpenCV**, **YOLOv8**, and **cv_bridge**.

This project converts a monocular video-based ADAS pipeline into a ROS2 node-based architecture. The system reads a driving video, publishes frames as ROS2 image messages, detects road users, filters relevant objects, computes a numerical risk score, generates ADAS alert levels, and saves an annotated output video.

---

## Project Overview

The main goal of this project is to demonstrate how a computer-vision-based ADAS pipeline can be structured as a modular ROS2 system.

Instead of running the full pipeline as a single Python script, the system is divided into independent ROS2 nodes:

- video frame publishing
- YOLOv8-based object detection
- ROI-based relevance filtering
- numerical risk scoring
- ADAS alert generation
- annotated output video visualization

This structure makes the system closer to real robotic and autonomous driving software architectures.

---

## System Architecture

```text
Input Driving Video
        |
        v
video_publisher_node
        |
        v
/camera/image
        |
        v
detector_node
        |
        v
/detections
        |
        v
risk_node
        |
        +--------------------+
        |                    |
        v                    v
/alert_level            /risk_score
        |                    |
        +---------+----------+
                  |
                  v
          visualizer_node
                  |
                  v
          adas_output.mp4
ROS2 Nodes
1. video_publisher_node

Reads a driving video from file and publishes each frame as a ROS2 image message.

Publishes:

/camera/image

Message type:

sensor_msgs/Image
2. detector_node

Subscribes to video frames and runs YOLOv8 object detection.

It detects road users such as:

cars
persons
trucks
buses
motorcycles
bicycles

It also applies ROI-based filtering to keep objects that are more relevant to the ego vehicle and road area.

Subscribes:

/camera/image

Publishes:

/detections

Message type:

std_msgs/String

The detection message includes:

class_name, confidence, x1, y1, x2, y2, area_ratio, cx_norm, bottom_norm
3. risk_node

Subscribes to filtered detections and computes a numerical risk score from 0 to 100.

The risk score is based on:

object confidence
object size in the image
object vertical position
object class
road-user relevance

Subscribes:

/detections

Publishes:

/risk_score
/alert_level

Message types:

std_msgs/Float32
std_msgs/String

Alert levels:

SAFE
CAUTION
WARNING
4. visualizer_node

Subscribes to the camera frames, detections, risk score, and alert level.

It draws:

bounding boxes
class labels
confidence scores
ADAS alert level
numerical risk score

The final annotated video is saved as:

adas_output.mp4
ROS2 Topics
Topic	Message Type	Description
/camera/image	sensor_msgs/Image	Published video frames
/detections	std_msgs/String	YOLOv8 detections after ROI filtering
/risk_score	std_msgs/Float32	Numerical risk score from 0 to 100
/alert_level	std_msgs/String	ADAS alert level: SAFE, CAUTION, WARNING
/rosout	ROS2 logging	ROS2 node logs
/parameter_events	ROS2 system topic	ROS2 parameter events
Repository Structure
ROS2-ADAS-Perception-Pipeline/
│
├── adas_ros2/
│   ├── __init__.py
│   ├── video_publisher_node.py
│   ├── detector_node.py
│   ├── risk_node.py
│   └── visualizer_node.py
│
├── launch/
│   └── adas_pipeline.launch.py
│
├── resource/
│   └── adas_ros2
│
├── test/
│   ├── test_copyright.py
│   ├── test_flake8.py
│   └── test_pep257.py
│
├── package.xml
├── setup.py
├── setup.cfg
├── .gitignore
└── README.md
Technologies Used
ROS2 Humble
Ubuntu 22.04 / WSL2
Python 3
OpenCV
YOLOv8
Ultralytics
cv_bridge
rclpy
NumPy
Installation
1. Install ROS2 Humble

This project was developed and tested with:

Ubuntu 22.04
ROS2 Humble

Source ROS2:

source /opt/ros/humble/setup.bash
2. Create a ROS2 workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
3. Clone this repository
git clone https://github.com/mahdi-rahmani-eng/ROS2-ADAS-Perception-Pipeline.git adas_ros2
4. Install dependencies
sudo apt update
sudo apt install python3-pip python3-opencv ros-humble-cv-bridge -y

Install Python dependencies:

python3 -m pip install --user ultralytics numpy opencv-python
5. Build the ROS2 package
cd ~/ros2_ws
colcon build --packages-select adas_ros2
source install/setup.bash

Check available executables:

ros2 pkg executables adas_ros2

Expected output:

adas_ros2 detector
adas_ros2 risk
adas_ros2 video_publisher
adas_ros2 visualizer
Input Video

The current implementation expects the input driving video at:

/home/mahdi/videos/test.mp4

Create the folder:

mkdir -p ~/videos

Copy your driving video into:

~/videos/test.mp4
Running the Pipeline

Run the full ROS2 ADAS pipeline with one command:

source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch adas_ros2 adas_pipeline.launch.py

This launches:

video_publisher_node
detector_node
risk_node
visualizer_node
Checking ROS2 Topics

In another terminal:

source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 topic list

Expected topics:

/camera/image
/detections
/alert_level
/risk_score
/parameter_events
/rosout

Check alert output:

ros2 topic echo /alert_level

Example output:

data: CAUTION
---
data: WARNING
---

Check numerical risk score:

ros2 topic echo /risk_score

Example output:

data: 62.5
---
data: 78.3
---
Output

The annotated output video is saved as:

~/ros2_ws/adas_output.mp4

The output video includes:

detected road users
bounding boxes
class labels
confidence scores
ADAS alert level
numerical risk score
Demo Video

The annotated demo video is available in the GitHub Releases section.

Release page:

https://github.com/mahdi-rahmani-eng/ROS2-ADAS-Perception-Pipeline/releases/tag/v1.0-demo

Demo video SHA256 checksum:

166549c5cff936caccc76c457a98b5fd802bc233ea9c53e771396dd832352ca4
Current Features
Modular ROS2 node-based architecture
Video publishing as ROS2 image topic
YOLOv8 object detection
ROI-based filtering for road-relevant objects
Numerical risk scoring from 0 to 100
ADAS alert generation
Alert levels: SAFE, CAUTION, WARNING
Annotated video output generation
Launch file for running the full pipeline with one command
Example Use Case

This project can be used as a prototype for monocular camera-based ADAS perception experiments.

Possible use cases include:

forward collision warning prototypes
road-user detection experiments
risk-aware perception pipelines
ROS2 learning projects for autonomous driving
computer vision portfolio projects
Limitations

This project is a research and portfolio prototype. It is not intended for real vehicle deployment.

Current limitations include:

monocular video input only
no real depth estimation
no sensor fusion
no real-time vehicle control
no camera calibration module
no tracking module in the current ROS2 version
simplified risk scoring logic
no real-world safety validation
Future Improvements

Planned or possible improvements:

add object tracking
add primary target selection
add time-to-collision proxy
add distance/headway estimation
add CSV logging of detections and risk scores
add ROS bag support
add RViz visualization
add parameter files for thresholds
add Docker support
integrate with a real camera topic
improve risk scoring with temporal smoothing
CV / Portfolio Summary

This project demonstrates practical experience with:

ROS2 package development
Python-based ROS2 nodes
computer vision pipeline design
YOLOv8 object detection
OpenCV video processing
ROS2 topic-based communication
ADAS perception architecture
modular software design for autonomous driving applications
Author

Mahdi Rahmani

GitHub:

https://github.com/mahdi-rahmani-eng
License

This project is released under the MIT License.
