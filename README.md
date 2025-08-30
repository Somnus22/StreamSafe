# StreamSafe - AI-Powered Privacy Protection for Streamers

StreamSafe is a powerful frontend application built with Streamlit that automatically detects and blurs sensitive details in live video streams. This repository contains the complete frontend implementation, designed to integrate with a Python backend powered by OpenCV, PyTorch, and YOLO Ultralytics models.

## 🚀 Features

### Live Streaming

* **Real-time Privacy Protection** : Automatically detect and blur sensitive content during live streams
* **WebRTC Integration** : Low-latency video streaming with WebRTC support
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

### Installation Steps

1. **Clone the repository**

   <pre class="overflow-visible!" data-start="285" data-end="372"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>git </span><span>clone</span><span> https://github.com/Somnus22/StreamSafe.git
   </span><span>cd</span><span> StreamSafe
   </span></span></code></div></div></pre>
2. **Install dependencies**

   <pre class="overflow-visible!" data-start="406" data-end="455"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>pip install -r requirements.txt
   </span></span></code></div></div></pre>
3. **Run the application**

   <pre class="overflow-visible!" data-start="488" data-end="536"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>streamlit run streamlit_app.py
   </span></span></code></div></div></pre>

   This will launch the application in your default web browser.

## 🎮 Usage

**🚀 Quick Start:**

1. Click **"Start"** above
2. Allow camera access when prompted
3. Toggle privacy features in real-time
4. Watch AI blur sensitive information live!

**📱 For DroidCam:**

* Install DroidCam on phone + computer
* Connect via same WiFi network
* Use browser camera access (this interface)

### AI/ML Stack Integration

The backend implements:

* **OpenCV (cv2)** for video processing and frame manipulation
* **PyTorch** for deep learning model inference
* **YOLO Ultralytics** for object detection
* **WebRTC** for real-time video streaming

## 🙏 Acknowledgments & Attribution

This project builds upon excellent open source tools and resources from:
Roboflow, Ultralytics, and MorseTechLab
Link: https://huggingface.co/morsetechlab/yolov11-license-plate-detection