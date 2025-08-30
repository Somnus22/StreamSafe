import streamlit as st

# Page config MUST be first
st.set_page_config(
    page_title="StreamSafe - Live Privacy Protection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import time
import subprocess
import sys
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av

# Import our privacy processing logic
from privacy_processor import StreamSafeProcessor

# Install requirements
@st.cache_resource
def install_requirements():
    packages = ["opencv-python>=4.8.1", "easyocr>=1.6.2", "ultralytics>=8.0.196"]
    for package in packages:
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, 
                "--quiet", "--disable-pip-version-check"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

install_requirements()

class StreamSafeVideoProcessor(VideoProcessorBase):
    """Streamlit WebRTC video processor"""
    
    def __init__(self):
        self.processor = StreamSafeProcessor()
        self.detection_enabled = {
            'license_plates': False,
            'street_signs': False,
            'block_numbers': False
        }
    
    def update_detection_settings(self, settings):
        """Update detection settings from Streamlit session state"""
        self.detection_enabled = settings.copy()
    
    def recv(self, frame):
        """Process each frame with privacy protections"""
        img = frame.to_ndarray(format="bgr24")
        processed_img = self.processor.process_frame(img, self.detection_enabled)
        return av.VideoFrame.from_ndarray(processed_img, format="bgr24")

@st.cache_resource
def get_processor():
    """Create global processor instance"""
    return StreamSafeVideoProcessor()

class LiveStreamState:
    """Mock live stream state"""
    def __init__(self):
        self.is_streaming = False
        self.fps = 0.0
        self.latency = 0
        self.detection_count = 0
    
    def start_stream(self):
        self.is_streaming = True

def load_css():
    """Load custom CSS styling"""
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
    
    .video-container, .control-section, .detection-card {
        background: #1f2937;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #374151;
    }
    
    .ai-powered-badge {
        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Video player size control */
    video {
        max-width: 480px !important;
        max-height: 360px !important;
        width: 480px !important;
        height: 360px !important;
    }
    
    /* WebRTC video container */
    .stVideo > video {
        max-width: 480px !important;
        max-height: 360px !important;
        width: 480px !important;
        height: 360px !important;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    load_css()
    
    # Initialize session state
    if 'live_state' not in st.session_state:
        st.session_state.live_state = LiveStreamState()
    
    if 'detection_settings' not in st.session_state:
        st.session_state.detection_settings = {
            'license_plates': False,
            'street_signs': False,
            'block_numbers': False
        }
    
    processor = get_processor()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <div class="logo-section">
            <div style="font-size: 2rem; color: #8b5cf6;">🛡️</div>
            <div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #ffffff; margin: 0;">StreamSafe</div>
                <div style="font-size: 0.9rem; color: #9ca3af; margin: 0;">Live Privacy Protection with Ultra-Robust Detection</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 8px; color: #10b981; font-weight: 500;">
            <span>🟢</span>
            <span>Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Video Stream Section - Using columns to center and control size
    st.markdown("""
    <div class="video-container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: white;">🔴 Live Privacy-Protected Stream</h3>
            <span class="ai-powered-badge">AI-Powered</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Update processor with current settings
    processor.update_detection_settings(st.session_state.detection_settings)
    
    # Center the video player using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:  # Video player in center column
        # WebRTC streamer with smaller size
        webrtc_ctx = webrtc_streamer(
            key="privacy_protected_feed",
            video_processor_factory=lambda: processor,
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
            media_stream_constraints={
                "video": {
                    "width": {"ideal": 640, "max": 640},
                    "height": {"ideal": 480, "max": 480}
                }, 
                "audio": False
            },
            async_processing=True,
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Stream Controls
    st.markdown("""<div class="control-section"><h3 style="margin: 0 0 1rem 0; color: white;">Stream Controls</h3>""", unsafe_allow_html=True)
    
    col_start, col_external = st.columns([4, 1])
    
    with col_start:
        if st.button("🎬 Start Stream", key="start_stream", help="Start live streaming"):
            st.session_state.live_state.start_stream()
            st.success("✅ Stream started! Toggle privacy features below to see real-time effects.")
    
    with col_external:
        if st.button("🔗 External", key="external", help="External stream settings"):
            st.info("External streaming options coming soon!")
    
    webcam_status = "📹 Webcam Active - Privacy Protection ON" if webrtc_ctx.state.playing else "📹 Click Start Stream to begin"
    st.markdown(f"""<div style="text-align: center; color: #9ca3af; margin-top: 1rem; font-size: 0.9rem;">{webcam_status}</div></div>""", unsafe_allow_html=True)
    
    # Privacy Detection Controls
    st.markdown("""
    <div class="detection-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <div style="font-size: 1.2rem; font-weight: 600; color: #ffffff;">Privacy Detection Controls</div>
            <div class="ai-powered-badge">Ultra-Robust AI</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Detection options
    detection_options = [
        {
            'key': 'license_plates',
            'icon': '🚗',
            'title': 'License Plates',
            'description': 'YOLO-based vehicle license plate detection'
        },
        {
            'key': 'street_signs',
            'icon': '📍',
            'title': 'Street Signs',
            'description': 'Singapore street sign detection'
        },
        {
            'key': 'block_numbers',
            'icon': '🏠',
            'title': 'Block Numbers',
            'description': 'EasyOCR Singapore block number detection'
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
            new_value = st.toggle(
                "",
                value=st.session_state.detection_settings[option['key']],
                key=f"toggle_{option['key']}",
                label_visibility="collapsed"
            )
            
            if new_value != st.session_state.detection_settings[option['key']]:
                st.session_state.detection_settings[option['key']] = new_value
                processor.update_detection_settings(st.session_state.detection_settings)
                
                status = "enabled" if new_value else "disabled"
                st.toast(f"🛡️ {option['title']} {status}", icon="✅" if new_value else "⚪")
    
    st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 1.5rem; font-size: 0.85rem;">
        ⚡ Detection settings update in real-time - toggle during streaming to see immediate effects!
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📱 How to Use StreamSafe")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🚀 Quick Start:**
        1. Click **"Start"** above
        2. Allow camera access when prompted
        3. Toggle privacy features in real-time
        4. Watch AI blur sensitive information live!
        
        **📱 For DroidCam:**
        - Install DroidCam on phone + computer
        - Connect via same WiFi network
        - Use browser camera access (this interface)
        """)
    
    with col2:
        st.markdown("""
        **🛡️ Privacy Features:**
        - **🚗 License Plates**
        - **🛑 Street Signs**
        - **🏠 Block Numbers**
        
        **⚡ Performance:**
        - Singapore-specific optimizations
        """)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Stream Status")
        
        if webrtc_ctx.state.playing:
            st.success("🟢 Stream Active")
            st.metric("Camera", "Live")
        else:
            st.info("⚫ Stream Inactive")  
            st.metric("Camera", "Offline")
        
        st.markdown("---")
        st.markdown("### 🛡️ Active Protections")
        
        active_protections = []
        if st.session_state.detection_settings['license_plates']:
            active_protections.append("🚗 License Plates (YOLO)")
        if st.session_state.detection_settings['street_signs']:
            active_protections.append("📍 Street Signs (HSV)")
        if st.session_state.detection_settings['block_numbers']:
            active_protections.append("🏠 Block Numbers (OCR)")
        
        if active_protections:
            for protection in active_protections:
                st.write(f"✅ {protection}")
            st.info(f"🔥 {len(active_protections)} AI protection(s) active!")
        else:
            st.write("⚪ No protections active")
            st.info("Toggle features above to enable AI privacy protection")
        
        st.markdown("---")
        st.markdown("### 🔧 Performance Info")
        st.write("**🎯 Detection Rates:**")
        st.write("• License Plates: Real-time")
        st.write("• Street Signs: Every 15 frames")  
        st.write("• Block Numbers: Every 30 frames")
        
        if st.button("🔄 Reset All Settings", help="Turn off all privacy protections"):
            st.session_state.detection_settings = {
                'license_plates': False,
                'street_signs': False,
                'block_numbers': False
            }
            processor.update_detection_settings(st.session_state.detection_settings)
            st.rerun()

if __name__ == "__main__":
    main()
