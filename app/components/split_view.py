import streamlit as st

def create_split_view(original_content=None, processed_content=None, original_online=False, processed_online=False):
    """Create a split view layout for original and processed video feeds"""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Original Feed
        st.markdown(f"""
        <div style="background: #1f2937; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #374151;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: white;">Original Feed</h3>
                <span style="background: {'#10b981' if original_online else '#374151'}; color: {'#ffffff' if original_online else '#9ca3af'}; padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.75rem; text-transform: uppercase; font-weight: 600;">{'Online' if original_online else 'Offline'}</span>
            </div>
        """, unsafe_allow_html=True)
        
        if original_content:
            st.write(original_content)
        else:
            st.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; background: #111827; border: 2px dashed #374151; border-radius: 8px; color: #9ca3af;">
                <div style="font-size: 3rem; color: #6b7280; margin-bottom: 1rem;">▶</div>
                <div>Click "Start Stream" to begin</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Privacy Protected Feed
        st.markdown(f"""
        <div style="background: #1f2937; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #374151;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: white;">Privacy Protected</h3>
                <span style="background: {'#10b981' if processed_online else '#374151'}; color: {'#ffffff' if processed_online else '#9ca3af'}; padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.75rem; text-transform: uppercase; font-weight: 600;">{'Online' if processed_online else 'Offline'}</span>
            </div>
        """, unsafe_allow_html=True)
        
        if processed_content:
            st.write(processed_content)
        else:
            st.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; background: #111827; border: 2px dashed #374151; border-radius: 8px; color: #9ca3af;">
                <div style="font-size: 3rem; color: #6b7280; margin-bottom: 1rem;">▶</div>
                <div>Processed feed will appear here</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def create_comparison_view(original_frame, processed_frame, show_diff=False):
    """Create a comparison view with optional difference highlighting"""
    
    if show_diff:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("**Original**")
            if original_frame is not None:
                st.image(original_frame, use_column_width=True)
        
        with col2:
            st.markdown("**Privacy Protected**")
            if processed_frame is not None:
                st.image(processed_frame, use_column_width=True)
        
        with col3:
            st.markdown("**Difference**")
            # TODO: Implement difference calculation when backend is ready
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; height: 200px; background: #111827; border: 2px dashed #374151; border-radius: 8px; color: #9ca3af;">
                <div>Diff view coming soon</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        create_split_view(
            original_content=original_frame if original_frame is not None else None,
            processed_content=processed_frame if processed_frame is not None else None,
            original_online=original_frame is not None,
            processed_online=processed_frame is not None
        )

def create_tabbed_view():
    """Create a tabbed interface for different views"""
    
    tab1, tab2, tab3 = st.tabs(["📹 Live Stream", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        return "live_stream"
    
    with tab2:
        return "analytics"
    
    with tab3:
        return "settings"

def create_sidebar_layout():
    """Create the sidebar layout for controls and stats"""
    
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🛡️</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: white;">StreamSafe</div>
            <div style="font-size: 0.9rem; color: #9ca3af;">Live Privacy Protection</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("🎬 Start Stream", use_container_width=True):
            return "start_stream"
        
        if st.button("⏹️ Stop Stream", use_container_width=True):
            return "stop_stream"
        
        if st.button("📸 Screenshot", use_container_width=True):
            return "screenshot"
        
        st.markdown("---")
        
        return None

def create_floating_controls(is_streaming=False):
    """Create floating action controls"""
    
    st.markdown("""
    <div style="position: fixed; bottom: 2rem; right: 2rem; z-index: 1000;">
        <div style="display: flex; flex-direction: column; gap: 1rem;">
    """, unsafe_allow_html=True)
    
    # Floating start/stop button
    if is_streaming:
        if st.button("⏹️", key="floating_stop", help="Stop Stream"):
            return "stop_stream"
    else:
        if st.button("🎬", key="floating_start", help="Start Stream"):
            return "start_stream"
    
    # Floating settings button
    if st.button("⚙️", key="floating_settings", help="Settings"):
        return "settings"
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return None