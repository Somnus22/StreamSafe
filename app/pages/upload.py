import streamlit as st
import time
from app.hooks.use_job import use_job_queue, create_video_processing_job, JobStatus
from app.lib.api import get_api_client, validate_video_file, format_file_size
from app.lib.utils import format_duration, format_eta, create_progress_bar_html, get_status_emoji
from app.components.cards import privacy_detection_card

def render_upload_page():
    """Render the video upload and processing page"""
    
    # Page header
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: white; margin-bottom: 0.5rem;">📁 Video Upload & Processing</h1>
        <p style="color: #9ca3af; margin: 0;">Upload videos to apply privacy protection automatically</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get job management hooks and API client
    job_manager = use_job_queue()
    api_client = get_api_client()
    
    # Upload section
    upload_section()
    
    st.markdown("---")
    
    # Detection settings
    st.markdown("### 🔍 Privacy Detection Settings")
    detection_settings = privacy_detection_card(
        st.session_state.get('upload_detection_settings', {
            'license_plates': True,
            'street_signs': True,
            'block_numbers': False,
            'faces': True,
            'documents': True,
            'screens': False
        })
    )
    st.session_state.upload_detection_settings = detection_settings
    
    st.markdown("---")
    
    # Processing queue
    render_processing_queue(job_manager)

def upload_section():
    """Render file upload section"""
    
    st.markdown("### 📤 Upload Video")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'],
        help="Maximum file size: 100MB",
        key="video_uploader"
    )
    
    if uploaded_file is not None:
        # Validate file
        file_data = uploaded_file.read()
        validation = validate_video_file(file_data, uploaded_file.name)
        
        if not validation['valid']:
            st.error(f"❌ {validation['error']}")
            return
        
        # Display file info
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.metric("📄 Filename", uploaded_file.name)
        with col2:
            st.metric("📊 File Size", validation['formatted_size'])
        with col3:
            st.metric("🎬 Type", uploaded_file.type or "video")
        
        # Process button
        col_process, col_cancel = st.columns([3, 1])
        
        with col_process:
            if st.button("🚀 Start Processing", type="primary", use_container_width=True):
                process_video_upload(uploaded_file.name, file_data)
        
        with col_cancel:
            if st.button("❌ Cancel", use_container_width=True):
                st.experimental_rerun()

def process_video_upload(filename: str, file_data: bytes):
    """Process uploaded video file"""
    
    try:
        # Get API client and detection settings
        api_client = get_api_client()
        detection_settings = st.session_state.get('upload_detection_settings', {})
        
        # Create processing job
        job = create_video_processing_job(
            file_path=filename,
            detection_settings=detection_settings,
            output_format="mp4",
            quality="high"
        )
        
        # Submit job
        job_manager = use_job_queue()
        job_id = job_manager['submit_job'](job)
        
        # Start backend processing (mock for now)
        if hasattr(api_client, 'upload_video'):
            # Real API call would go here
            result = api_client.upload_video(file_data, filename, detection_settings)
            if 'error' in result:
                st.error(f"Upload failed: {result['error']}")
                return
        
        st.success(f"✅ Video uploaded successfully! Job ID: {job_id[:8]}...")
        st.info("📊 Processing started. Check the queue below for progress.")
        
        # Clear the uploader
        if "video_uploader" in st.session_state:
            del st.session_state.video_uploader
        
        time.sleep(1)
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"❌ Processing failed: {str(e)}")

def render_processing_queue(job_manager):
    """Render the processing job queue"""
    
    st.markdown("### 📋 Processing Queue")
    
    # Get all jobs
    all_jobs = job_manager['get_all_jobs']()
    
    if not all_jobs:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #6b7280; background: #1f2937; border-radius: 12px; border: 2px dashed #374151;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">No jobs in queue</div>
            <div style="font-size: 0.9rem;">Upload a video to start processing</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Sort jobs by creation time (newest first)
    sorted_jobs = sorted(all_jobs, key=lambda j: j.created_at, reverse=True)
    
    # Tabs for different job statuses
    active_jobs = [j for j in sorted_jobs if j.status == JobStatus.RUNNING]
    completed_jobs = [j for j in sorted_jobs if j.status == JobStatus.COMPLETED]
    failed_jobs = [j for j in sorted_jobs if j.status in [JobStatus.FAILED, JobStatus.CANCELLED]]
    
    tab1, tab2, tab3 = st.tabs([
        f"🔄 Active ({len(active_jobs)})",
        f"✅ Completed ({len(completed_jobs)})", 
        f"❌ Failed ({len(failed_jobs)})"
    ])
    
    with tab1:
        if active_jobs:
            for job in active_jobs:
                render_job_card(job, job_manager)
                # Simulate progress for demo
                job_manager['simulate_job_progress'](job.id)
        else:
            st.info("No active processing jobs")
    
    with tab2:
        if completed_jobs:
            for job in completed_jobs:
                render_job_card(job, job_manager)
        else:
            st.info("No completed jobs")
    
    with tab3:
        if failed_jobs:
            for job in failed_jobs:
                render_job_card(job, job_manager)
        else:
            st.info("No failed jobs")
    
    # Auto-refresh for active jobs
    if active_jobs:
        time.sleep(2)
        st.experimental_rerun()

def render_job_card(job, job_manager):
    """Render individual job card"""
    
    # Job status styling
    status_color = {
        JobStatus.PENDING: "#6b7280",
        JobStatus.RUNNING: "#f59e0b", 
        JobStatus.COMPLETED: "#10b981",
        JobStatus.FAILED: "#ef4444",
        JobStatus.CANCELLED: "#6b7280"
    }.get(job.status, "#6b7280")
    
    status_emoji = get_status_emoji(job.status.value)
    
    # Calculate timing info
    duration = job.get_duration()
    eta = job.get_eta_seconds()
    
    # Job card HTML
    st.markdown(f"""
    <div style="background: #1f2937; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border-left: 4px solid {status_color};">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.1rem;">{status_emoji}</span>
                    <h4 style="margin: 0; color: white;">{job.input_data.get('file_path', 'Unknown File')}</h4>
                </div>
                <div style="color: #9ca3af; font-size: 0.85rem;">
                    Job ID: {job.id[:8]}... • Created: {time.strftime('%H:%M:%S', time.localtime(job.created_at))}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="background: {status_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.75rem; text-transform: uppercase; font-weight: 600;">
                    {job.status.value}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar for running jobs
    if job.status == JobStatus.RUNNING:
        progress_html = create_progress_bar_html(job.progress, "#f59e0b", "12px")
        st.markdown(progress_html, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f"**Progress:** {job.progress:.1f}%")
        with col2:
            st.markdown(f"**Stage:** {job.current_stage or 'Processing'}")
        with col3:
            if eta:
                st.markdown(f"**ETA:** {format_eta(eta)}")
    
    # Job details
    with st.expander(f"📊 Job Details - {job.id[:8]}"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Input Settings:**")
            st.json({
                'detection_settings': job.input_data.get('detection_settings', {}),
                'output_format': job.input_data.get('output_format', 'mp4'),
                'quality': job.input_data.get('quality', 'high')
            })
        
        with col2:
            st.markdown("**Job Statistics:**")
            stats = {
                'Duration': format_duration(duration) if duration > 0 else 'N/A',
                'Total Frames': job.total_frames or 'Unknown',
                'Processed Frames': job.processed_frames or 0,
                'Status': job.status.value.title()
            }
            
            if job.error_message:
                stats['Error'] = job.error_message
            
            if job.output_data:
                stats['Output Path'] = job.output_data.get('output_path', 'N/A')
            
            for key, value in stats.items():
                st.markdown(f"**{key}:** {value}")
    
    # Action buttons
    col_actions = st.columns([1, 1, 1, 2])
    
    with col_actions[0]:
        if job.status == JobStatus.RUNNING:
            if st.button(f"⏹️ Cancel", key=f"cancel_{job.id}"):
                job_manager['cancel_job'](job.id)
                st.experimental_rerun()
    
    with col_actions[1]:
        if job.status == JobStatus.COMPLETED and job.output_data:
            if st.button(f"💾 Download", key=f"download_{job.id}"):
                st.info("Download functionality will be integrated with backend")
    
    with col_actions[2]:
        if st.button(f"🗑️ Remove", key=f"remove_{job.id}"):
            # Remove job from queue
            if job.id in job_manager['queue'].jobs:
                del job_manager['queue'].jobs[job.id]
            st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_batch_upload():
    """Render batch upload functionality"""
    
    st.markdown("### 📁 Batch Upload")
    
    uploaded_files = st.file_uploader(
        "Choose multiple video files",
        type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'],
        accept_multiple_files=True,
        help="Select multiple video files to process in batch",
        key="batch_uploader"
    )
    
    if uploaded_files:
        st.markdown(f"**Selected Files:** {len(uploaded_files)}")
        
        total_size = 0
        valid_files = []
        
        for file in uploaded_files:
            file_data = file.read()
            validation = validate_video_file(file_data, file.name)
            
            if validation['valid']:
                valid_files.append((file.name, file_data))
                total_size += validation['size']
            else:
                st.warning(f"⚠️ {file.name}: {validation['error']}")
        
        if valid_files:
            st.info(f"✅ {len(valid_files)} valid files, Total size: {format_file_size(total_size)}")
            
            if st.button("🚀 Process All Files", type="primary"):
                process_batch_upload(valid_files)

def process_batch_upload(files):
    """Process batch upload"""
    
    job_manager = use_job_queue()
    detection_settings = st.session_state.get('upload_detection_settings', {})
    
    for filename, file_data in files:
        job = create_video_processing_job(
            file_path=filename,
            detection_settings=detection_settings
        )
        job_manager['submit_job'](job)
    
    st.success(f"✅ {len(files)} files queued for processing!")
    time.sleep(1)
    st.experimental_rerun()

# Main page render function
if __name__ == "__main__":
    render_upload_page()