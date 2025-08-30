import streamlit as st
import time
import cv2
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import numpy as np

# Import our custom components
from app.components.cards import privacy_detection_card, stream_controls_card
from app.components.split_view import create_split_view
from app.hooks.use_live import LiveStreamState
from app.lib.utils import format_fps, format_latency

# Page config
st.set_page_config(
    page_title="StreamSafe - Live Privacy Protection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    st.markdown("""
    <style>
   
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    .main-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 2rem;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo {
        font-size: 2rem;
        color: #8b5cf6;
    }
    
    .app-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 0.9rem;
        color: #9ca3af;
        margin: 0;
    }
    
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid #10b981;
        border-radius: 8px;
        color: #10b981;
        font-weight: 500;
    }
    
    .video-container {
        background: #1f2937;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #374151;
    }
    
    .video-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 300px;
        background: #111827;
        border: 2px dashed #374151;
        border-radius: 8px;
        color: #9ca3af;
    }
    
    .play-button {
        font-size: 3rem;
        color: #6b7280;
        margin-bottom: 1rem;
    }
    
    .offline-badge {
        background: #374151;
        color: #9ca3af;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    .online-badge {
        background: #10b981;
        color: #ffffff;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    .control-section {
        background: #1f2937;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #374151;
    }
    
    .start-stream-btn {
        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .start-stream-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3);
    }
    
    .external-btn {
        background: #374151;
        color: white;
        border: none;
        padding: 1rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        margin-left: 1rem;
    }
    
    .webcam-status {
        text-align: center;
        color: #9ca3af;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    
    .detection-card {
        background: #1f2937;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #374151;
    }
    
    .detection-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .detection-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    .ai-powered-badge {
        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .detection-option {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #374151;
    }
    
    .detection-option:last-child {
        border-bottom: none;
    }
    
    .option-info {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .option-icon {
        font-size: 1.2rem;
        color: #8b5cf6;
    }
    
    .option-text h4 {
        margin: 0;
        color: #ffffff;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .option-text p {
        margin: 0.25rem 0 0 0;
        color: #9ca3af;
        font-size: 0.85rem;
    }
    
    .toggle-switch {
        position: relative;
        width: 48px;
        height: 24px;
        background: #374151;
        border-radius: 12px;
        cursor: pointer;
    }
    
    .toggle-switch.active {
        background: #8b5cf6;
    }
    
    .toggle-switch::after {
        content: '';
        position: absolute;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: white;
        top: 2px;
        left: 2px;
        transition: transform 0.3s ease;
    }
    
    .toggle-switch.active::after {
        transform: translateX(24px);
    }
    
    .detection-note {
        text-align: center;
        color: #6b7280;
        margin-top: 1.5rem;
        font-size: 0.85rem;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Video processor for WebRTC
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.detection_enabled = {
            'license_plates': True,
            'street_signs': True,
            'block_numbers': False
        }
    
    def recv(self, frame):
        # This is where the backend CV2/YOLO processing will be integrated
        img = frame.to_ndarray(format="bgr24")
        

        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    # Load CSS
    load_css()
    
    # Initialize session state
    if 'live_state' not in st.session_state:
        st.session_state.live_state = LiveStreamState()
    
    if 'detection_settings' not in st.session_state:
        st.session_state.detection_settings = {
            'license_plates': True,
            'street_signs': True,
            'block_numbers': False
        }
    
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="logo-section">
            <div class="logo">🛡️</div>
            <div>
                <div class="app-title">StreamSafe</div>
                <div class="app-subtitle">Live Privacy Protection</div>
            </div>
        </div>
        <div class="status-indicator">
            <span>🟢</span>
            <span>Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Original Feed
        st.markdown("""
        <div class="video-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: white;">Original Feed</h3>
                <span class="offline-badge">Offline</span>
            </div>
        """, unsafe_allow_html=True)
        
        # WebRTC streamer for original feed
        webrtc_ctx = webrtc_streamer(
            key="original_feed",
            video_processor_factory=VideoProcessor,
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Privacy Protected Feed
        st.markdown("""
        <div class="video-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: white;">Privacy Protected</h3>
                <span class="online-badge">Online</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Processed feed placeholder (will show processed video when backend is integrated)
        st.markdown("""
        <div class="video-placeholder">
            <div class="play-button">▶</div>
            <div>Processed feed will appear here</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Stream Controls
    st.markdown("""
    <div class="control-section">
        <h3 style="margin: 0 0 1rem 0; color: white;">Stream Controls</h3>
    """, unsafe_allow_html=True)
    
    col_start, col_external = st.columns([4, 1])
    
    with col_start:
        if st.button("🎬 Start Stream", key="start_stream", help="Start live streaming"):
            st.session_state.live_state.start_stream()
            st.success("Stream started!")
    
    with col_external:
        if st.button("🔗 External", key="external", help="External stream settings"):
            st.info("External streaming options coming soon!")
    
    st.markdown("""
    <div class="webcam-status">📹 Webcam Inactive</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Privacy Detection Settings
    st.markdown("""
    <div class="detection-card">
        <div class="detection-header">
            <div class="detection-title">Privacy Detection</div>
            <div class="ai-powered-badge">AI-Powered</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Detection options
    detection_options = [
        {
            'key': 'license_plates',
            'icon': '🚗',
            'title': 'License Plates',
            'description': 'Hide vehicle license plates'
        },
        {
            'key': 'street_signs',
            'icon': '📍',
            'title': 'Street Signs',
            'description': 'Blur street name signs'
        },
        {
            'key': 'block_numbers',
            'icon': '🏠',
            'title': 'Block Numbers',
            'description': 'Hide building numbers'
        }
    ]
    
    for option in detection_options:
        col_info, col_toggle = st.columns([3, 1])
        
        with col_info:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.2rem;">{option['icon']}</span>
                <div>
                    <div style="color: white; font-weight: 600; margin: 0;">{option['title']}</div>
                    <div style="color: #9ca3af; font-size: 0.85rem; margin: 0;">{option['description']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_toggle:
            st.session_state.detection_settings[option['key']] = st.toggle(
                "",
                value=st.session_state.detection_settings[option['key']],
                key=f"toggle_{option['key']}",
                label_visibility="collapsed"
            )
    
    st.markdown("""
    <div class="detection-note">
        Detection settings can be adjusted during live streaming
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats sidebar (optional)
    with st.sidebar:
        st.header("📊 Stream Stats")
        
        if st.session_state.live_state.is_streaming:
            st.metric("Status", "🟢 Live")
            st.metric("FPS", f"{st.session_state.live_state.fps:.1f}")
            st.metric("Latency", f"{st.session_state.live_state.latency:.0f}ms")
            st.metric("Detections", st.session_state.live_state.detection_count)
        else:
            st.metric("Status", "⚫ Offline")
            st.metric("FPS", "0.0")
            st.metric("Latency", "0ms")
            st.metric("Detections", "0")
        
        st.markdown("---")
        st.markdown("### 🔧 Quick Settings")
        
        quality = st.selectbox("Stream Quality", ["720p", "1080p", "4K"], index=0)
        bitrate = st.slider("Bitrate (Mbps)", 1, 10, 5)
        
        if st.button("Reset Settings"):
            st.session_state.detection_settings = {
                'license_plates': True,
                'street_signs': True,
                'block_numbers': False
            }
            st.experimental_rerun()

if __name__ == "__main__":
    main()