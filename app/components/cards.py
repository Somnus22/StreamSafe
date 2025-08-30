import streamlit as st

def privacy_detection_card(detection_settings):
    """Create the privacy detection settings card"""
    
    st.markdown("""
    <div style="background: #1f2937; border-radius: 12px; padding: 1.5rem; border: 1px solid #374151;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h3 style="margin: 0; color: white; font-size: 1.2rem;">Privacy Detection</h3>
            <span style="background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">AI-Powered</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detection options
    options = [
        {
            'key': 'license_plates',
            'icon': '🚗',
            'title': 'License Plates',
            'description': 'Hide vehicle license plates',
            'enabled': detection_settings.get('license_plates', True)
        },
        {
            'key': 'street_signs', 
            'icon': '📍',
            'title': 'Street Signs',
            'description': 'Blur street name signs',
            'enabled': detection_settings.get('street_signs', True)
        },
        {
            'key': 'block_numbers',
            'icon': '🏠', 
            'title': 'Block Numbers',
            'description': 'Hide building numbers',
            'enabled': detection_settings.get('block_numbers', False)
        }
    ]
    
    updated_settings = {}
    
    for option in options:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem 0;">
                <span style="font-size: 1.2rem; color: #8b5cf6;">{option['icon']}</span>
                <div>
                    <h4 style="margin: 0; color: white; font-size: 1rem;">{option['title']}</h4>
                    <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.85rem;">{option['description']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            updated_settings[option['key']] = st.toggle(
                "",
                value=option['enabled'],
                key=f"detection_{option['key']}",
                label_visibility="collapsed"
            )
    
    st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 1.5rem; font-size: 0.85rem;">
        Detection settings can be adjusted during live streaming
    </div>
    """, unsafe_allow_html=True)
    
    return updated_settings

def stream_controls_card(is_streaming=False, webcam_active=False):
    """Create the stream controls card"""
    
    st.markdown("""
    <div style="background: #1f2937; border-radius: 12px; padding: 1.5rem; border: 1px solid #374151;">
        <h3 style="margin: 0 0 1rem 0; color: white;">Stream Controls</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Control buttons
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if is_streaming:
            stream_button = st.button(
                "⏹️ Stop Stream", 
                key="stop_stream",
                type="primary",
                use_container_width=True
            )
        else:
            stream_button = st.button(
                "🎬 Start Stream", 
                key="start_stream",
                type="primary", 
                use_container_width=True
            )
    
    with col2:
        external_button = st.button(
            "🔗 External",
            key="external_stream",
            use_container_width=True
        )
    
    # Webcam status
    status_text = "📹 Webcam Active" if webcam_active else "📹 Webcam Inactive"
    status_color = "#10b981" if webcam_active else "#9ca3af"
    
    st.markdown(f"""
    <div style="text-align: center; color: {status_color}; margin-top: 1rem; font-size: 0.9rem;">
        {status_text}
    </div>
    """, unsafe_allow_html=True)
    
    return {
        'stream_button_clicked': stream_button,
        'external_button_clicked': external_button,
        'is_streaming': is_streaming
    }

def video_feed_card(title, is_online=False, placeholder_text="Click \"Start Stream\" to begin"):
    """Create a video feed display card"""
    
    status_badge = "online-badge" if is_online else "offline-badge" 
    status_text = "Online" if is_online else "Offline"
    
    st.markdown(f"""
    <div style="background: #1f2937; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #374151;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: white;">{title}</h3>
            <span class="{status_badge}" style="background: {'#10b981' if is_online else '#374151'}; color: {'#ffffff' if is_online else '#9ca3af'}; padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.75rem; text-transform: uppercase; font-weight: 600;">{status_text}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if not is_online:
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; background: #111827; border: 2px dashed #374151; border-radius: 8px; color: #9ca3af;">
            <div style="font-size: 3rem; color: #6b7280; margin-bottom: 1rem;">▶</div>
            <div>{placeholder_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def stats_card(fps=0.0, latency=0, detections=0, is_live=False):
    """Create a stats display card"""
    
    status_color = "#10b981" if is_live else "#6b7280"
    status_text = "🟢 Live" if is_live else "⚫ Offline"
    
    st.markdown(f"""
    <div style="background: #1f2937; border-radius: 12px; padding: 1.5rem; border: 1px solid #374151; margin-bottom: 1rem;">
        <h3 style="margin: 0 0 1rem 0; color: white; font-size: 1.1rem;">📊 Stream Stats</h3>
        
        <div style="display: grid; grid-template-columns: 1fr; gap: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #374151;">
                <span style="color: #9ca3af;">Status</span>
                <span style="color: {status_color}; font-weight: 600;">{status_text}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #374151;">
                <span style="color: #9ca3af;">FPS</span>
                <span style="color: white; font-weight: 600;">{fps:.1f}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #374151;">
                <span style="color: #9ca3af;">Latency</span>
                <span style="color: white; font-weight: 600;">{latency:.0f}ms</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0;">
                <span style="color: #9ca3af;">Detections</span>
                <span style="color: white; font-weight: 600;">{detections}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def settings_card():
    """Create a settings configuration card"""
    
    st.markdown("""
    <div style="background: #1f2937; border-radius: 12px; padding: 1.5rem; border: 1px solid #374151;">
        <h3 style="margin: 0 0 1rem 0; color: white; font-size: 1.1rem;">🔧 Quick Settings</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings options
    quality = st.selectbox(
        "Stream Quality",
        options=["720p", "1080p", "4K"],
        index=0,
        key="stream_quality"
    )
    
    bitrate = st.slider(
        "Bitrate (Mbps)",
        min_value=1,
        max_value=10, 
        value=5,
        key="stream_bitrate"
    )
    
    enable_audio = st.checkbox(
        "Enable Audio",
        value=False,
        key="enable_audio"
    )
    
    reset_clicked = st.button(
        "Reset Settings",
        key="reset_settings",
        use_container_width=True
    )
    
    return {
        'quality': quality,
        'bitrate': bitrate,
        'enable_audio': enable_audio,
        'reset_clicked': reset_clicked
    }