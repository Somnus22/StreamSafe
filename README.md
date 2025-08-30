# StreamSafe - AI-Powered Privacy Protection for Streamers

StreamSafe is a powerful frontend application built with Streamlit that automatically detects and blurs sensitive details in live video streams. This repository contains the complete frontend implementation, designed to integrate with a Python backend powered by OpenCV, PyTorch, and YOLO Ultralytics models.

## 🚀 Features

### Live Streaming

* **Real-time Privacy Protection** : Automatically detect and blur sensitive content during live streams
* **WebRTC Integration** : Low-latency video streaming with WebRTC support
* **Dual Feed Display** : Side-by-side view of original and privacy-protected streams
* **Live Metrics** : Real-time FPS, latency, and detection count monitoring

### Privacy Detection

* **License Plates** : Automatically blur vehicle license plates
* **Street Signs** : Detect and blur street name signs
* **Building Numbers** : Hide building numbers and addresses

### User Interface

* **Dark Theme** : Modern dark UI matching streaming aesthetics
* **Real-time Updates** : Live progress tracking and status updates
* **Intuitive Controls** : Easy-to-use streaming controls and settings

## 🛠️ Installation & Setup

### Prerequisites

* Python 3.8 or higher
* pip package manager


## 🎮 Usage

### Live Streaming

1. **Start Stream** : Click the "Start Stream" button to begin live video capture
2. **Configure Detection** : Toggle privacy detection options in real-time
3. **Monitor Performance** : View FPS, latency, and detection metrics in the sidebar


### AI/ML Stack Integration

The backend should implement:

* **OpenCV (cv2)** for video processing and frame manipulation
* **PyTorch** for deep learning model inference
* **YOLO Ultralytics** for object detection
* **WebRTC** for real-time video streaming
