import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import streamlit as st

@dataclass
class LiveStreamState:
    """State management for live streaming functionality"""
    is_streaming: bool = False
    is_webcam_active: bool = False
    fps: float = 0.0
    latency: float = 0.0
    detection_count: int = 0
    stream_start_time: Optional[float] = None
    last_frame_time: Optional[float] = None
    frame_count: int = 0
    total_detections: int = 0
    
    # Performance metrics
    avg_processing_time: float = 0.0
    peak_memory_usage: float = 0.0
    dropped_frames: int = 0
    
    # Stream settings
    resolution: str = "720p"
    bitrate: int = 5
    enable_audio: bool = False
    
    # Detection settings
    detection_settings: Dict[str, bool] = field(default_factory=lambda: {
        'license_plates': True,
        'street_signs': True,
        'block_numbers': False,
        'faces': True,
        'documents': True,
        'screens': False
    })
    
    def start_stream(self):
        """Start the live stream"""
        self.is_streaming = True
        self.is_webcam_active = True
        self.stream_start_time = time.time()
        self.frame_count = 0
        self.detection_count = 0
        
        # Start performance monitoring
        self._start_performance_monitoring()
    
    def stop_stream(self):
        """Stop the live stream"""
        self.is_streaming = False
        self.is_webcam_active = False
        self.stream_start_time = None
        self.last_frame_time = None
        self.fps = 0.0
        self.latency = 0.0
    
    def update_frame_stats(self, processing_time: float = 0.0, detections_in_frame: int = 0):
        """Update frame-level statistics"""
        current_time = time.time()
        
        if self.last_frame_time:
            # Calculate FPS
            time_diff = current_time - self.last_frame_time
            if time_diff > 0:
                self.fps = 1.0 / time_diff
        
        self.last_frame_time = current_time
        self.frame_count += 1
        self.detection_count += detections_in_frame
        self.total_detections += detections_in_frame
        
        # Update average processing time
        if processing_time > 0:
            self.avg_processing_time = (
                (self.avg_processing_time * (self.frame_count - 1) + processing_time) / self.frame_count
            )
            # Latency is approximated by processing time
            self.latency = processing_time * 1000  # Convert to ms
    
    def get_stream_duration(self) -> float:
        """Get current stream duration in seconds"""
        if self.stream_start_time:
            return time.time() - self.stream_start_time
        return 0.0
    
    def get_average_fps(self) -> float:
        """Get average FPS since stream started"""
        duration = self.get_stream_duration()
        if duration > 0 and self.frame_count > 0:
            return self.frame_count / duration
        return 0.0
    
    def get_detections_per_second(self) -> float:
        """Get average detections per second"""
        duration = self.get_stream_duration()
        if duration > 0:
            return self.total_detections / duration
        return 0.0
    
    def update_detection_setting(self, setting: str, enabled: bool):
        """Update a specific detection setting"""
        if setting in self.detection_settings:
            self.detection_settings[setting] = enabled
    
    def get_enabled_detections(self) -> list:
        """Get list of currently enabled detection types"""
        return [key for key, value in self.detection_settings.items() if value]
    
    def _start_performance_monitoring(self):
        """Start background performance monitoring"""
        # This could be expanded to monitor system resources
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            'is_streaming': self.is_streaming,
            'is_webcam_active': self.is_webcam_active,
            'fps': self.fps,
            'latency': self.latency,
            'detection_count': self.detection_count,
            'frame_count': self.frame_count,
            'total_detections': self.total_detections,
            'stream_duration': self.get_stream_duration(),
            'avg_processing_time': self.avg_processing_time,
            'resolution': self.resolution,
            'bitrate': self.bitrate,
            'enable_audio': self.enable_audio,
            'detection_settings': self.detection_settings.copy()
        }

class WebRTCManager:
    """Manages WebRTC connections and streaming"""
    
    def __init__(self):
        self.is_connected = False
        self.peer_connection = None
        self.local_stream = None
        self.remote_stream = None
    
    def initialize_connection(self):
        """Initialize WebRTC peer connection"""
        # TODO: Implement WebRTC setup when backend is ready
        self.is_connected = True
        return True
    
    def start_local_stream(self):
        """Start local webcam stream"""
        # TODO: Implement local stream capture
        self.local_stream = "mock_stream"
        return self.local_stream
    
    def stop_local_stream(self):
        """Stop local webcam stream"""
        self.local_stream = None
    
    def send_frame(self, frame):
        """Send frame through WebRTC"""
        # TODO: Implement frame sending
        pass
    
    def receive_frame(self):
        """Receive processed frame"""
        # TODO: Implement frame receiving
        return None

class StreamMetrics:
    """Handles stream performance metrics"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history_size = 1000
    
    def add_metrics(self, fps: float, latency: float, detections: int, timestamp: float = None):
        """Add metrics point to history"""
        if timestamp is None:
            timestamp = time.time()
        
        metrics_point = {
            'timestamp': timestamp,
            'fps': fps,
            'latency': latency,
            'detections': detections
        }
        
        self.metrics_history.append(metrics_point)
        
        # Keep history size manageable
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
    
    def get_recent_metrics(self, seconds: int = 60):
        """Get metrics from last N seconds"""
        cutoff_time = time.time() - seconds
        return [m for m in self.metrics_history if m['timestamp'] >= cutoff_time]
    
    def get_average_metrics(self, seconds: int = 60):
        """Get average metrics over last N seconds"""
        recent = self.get_recent_metrics(seconds)
        if not recent:
            return {'fps': 0.0, 'latency': 0.0, 'detections': 0.0}
        
        return {
            'fps': sum(m['fps'] for m in recent) / len(recent),
            'latency': sum(m['latency'] for m in recent) / len(recent),
            'detections': sum(m['detections'] for m in recent) / len(recent)
        }

def use_live_stream():
    """Hook for managing live stream state in Streamlit"""
    
    # Initialize state if not exists
    if 'live_state' not in st.session_state:
        st.session_state.live_state = LiveStreamState()
    
    if 'webrtc_manager' not in st.session_state:
        st.session_state.webrtc_manager = WebRTCManager()
    
    if 'stream_metrics' not in st.session_state:
        st.session_state.stream_metrics = StreamMetrics()
    
    def start_stream():
        """Start streaming with all necessary setup"""
        st.session_state.live_state.start_stream()
        st.session_state.webrtc_manager.initialize_connection()
        st.session_state.webrtc_manager.start_local_stream()
        return True
    
    def stop_stream():
        """Stop streaming and cleanup"""
        st.session_state.live_state.stop_stream()
        st.session_state.webrtc_manager.stop_local_stream()
        return True
    
    def update_metrics(fps: float = 0.0, latency: float = 0.0, detections: int = 0):
        """Update streaming metrics"""
        st.session_state.live_state.update_frame_stats(latency/1000, detections)
        st.session_state.stream_metrics.add_metrics(fps, latency, detections)
    
    def get_state():
        """Get current live stream state"""
        return st.session_state.live_state
    
    def update_detection_settings(settings: Dict[str, bool]):
        """Update detection settings"""
        for key, value in settings.items():
            st.session_state.live_state.update_detection_setting(key, value)
    
    return {
        'state': st.session_state.live_state,
        'start_stream': start_stream,
        'stop_stream': stop_stream,
        'update_metrics': update_metrics,
        'get_state': get_state,
        'update_detection_settings': update_detection_settings,
        'webrtc_manager': st.session_state.webrtc_manager,
        'metrics': st.session_state.stream_metrics
    }