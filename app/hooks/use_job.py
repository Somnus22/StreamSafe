import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import streamlit as st

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(Enum):
    VIDEO_UPLOAD = "video_upload"
    VIDEO_PROCESSING = "video_processing"
    BATCH_PROCESSING = "batch_processing"
    MODEL_TRAINING = "model_training"
    EXPORT = "export"

@dataclass
class Job:
    """Represents a background processing job"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: JobType = JobType.VIDEO_PROCESSING
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    
    # Job-specific data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Progress tracking
    total_frames: int = 0
    processed_frames: int = 0
    current_stage: str = ""
    estimated_completion: Optional[float] = None
    
    def start(self):
        """Mark job as started"""
        self.status = JobStatus.RUNNING
        self.started_at = time.time()
    
    def complete(self, output_data: Dict[str, Any] = None):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED
        self.completed_at = time.time()
        self.progress = 100.0
        if output_data:
            self.output_data.update(output_data)
    
    def fail(self, error_message: str):
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.completed_at = time.time()
        self.error_message = error_message
    
    def cancel(self):
        """Cancel the job"""
        self.status = JobStatus.CANCELLED
        self.completed_at = time.time()
    
    def update_progress(self, progress: float, current_stage: str = "", processed_frames: int = None):
        """Update job progress"""
        self.progress = max(0.0, min(100.0, progress))
        if current_stage:
            self.current_stage = current_stage
        if processed_frames is not None:
            self.processed_frames = processed_frames
            
        # Estimate completion time
        if self.started_at and self.progress > 0:
            elapsed = time.time() - self.started_at
            estimated_total = (elapsed / self.progress) * 100
            self.estimated_completion = self.started_at + estimated_total
    
    def get_duration(self) -> float:
        """Get job duration in seconds"""
        if self.started_at:
            end_time = self.completed_at or time.time()
            return end_time - self.started_at
        return 0.0
    
    def get_eta_seconds(self) -> Optional[float]:
        """Get estimated time to completion in seconds"""
        if self.estimated_completion and self.status == JobStatus.RUNNING:
            eta = self.estimated_completion - time.time()
            return max(0, eta)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'status': self.status.value,
            'progress': self.progress,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'duration': self.get_duration(),
            'error_message': self.error_message,
            'total_frames': self.total_frames,
            'processed_frames': self.processed_frames,
            'current_stage': self.current_stage,
            'eta_seconds': self.get_eta_seconds(),
            'input_data': self.input_data,
            'output_data': self.output_data,
            'metadata': self.metadata
        }

class JobQueue:
    """Manages job queue and execution"""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.job_history: List[str] = []
        self.max_history = 100
    
    def add_job(self, job: Job) -> str:
        """Add job to queue"""
        self.jobs[job.id] = job
        self.job_history.append(job.id)
        
        # Keep history manageable
        if len(self.job_history) > self.max_history:
            old_job_id = self.job_history.pop(0)
            if old_job_id in self.jobs and self.jobs[old_job_id].status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                del self.jobs[old_job_id]
        
        return job.id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get all jobs with specific status"""
        return [job for job in self.jobs.values() if job.status == status]
    
    def get_active_jobs(self) -> List[Job]:
        """Get all running jobs"""
        return self.get_jobs_by_status(JobStatus.RUNNING)
    
    def get_pending_jobs(self) -> List[Job]:
        """Get all pending jobs"""
        return self.get_jobs_by_status(JobStatus.PENDING)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        job = self.get_job(job_id)
        if job and job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            job.cancel()
            return True
        return False
    
    def cleanup_completed_jobs(self, max_age_hours: int = 24):
        """Remove old completed jobs"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        jobs_to_remove = []
        
        for job_id, job in self.jobs.items():
            if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] 
                and job.completed_at and job.completed_at < cutoff_time):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            if job_id in self.job_history:
                self.job_history.remove(job_id)

def create_video_processing_job(
    file_path: str,
    detection_settings: Dict[str, bool],
    output_format: str = "mp4",
    quality: str = "high"
) -> Job:
    """Create a video processing job"""
    
    job = Job(
        type=JobType.VIDEO_PROCESSING,
        input_data={
            'file_path': file_path,
            'detection_settings': detection_settings,
            'output_format': output_format,
            'quality': quality
        },
        metadata={
            'file_name': file_path.split('/')[-1] if '/' in file_path else file_path,
            'created_by': 'streamlit_app'
        }
    )
    
    return job

def create_batch_processing_job(
    file_paths: List[str],
    detection_settings: Dict[str, bool],
    output_format: str = "mp4"
) -> Job:
    """Create a batch processing job"""
    
    job = Job(
        type=JobType.BATCH_PROCESSING,
        input_data={
            'file_paths': file_paths,
            'detection_settings': detection_settings,
            'output_format': output_format
        },
        metadata={
            'file_count': len(file_paths),
            'created_by': 'streamlit_app'
        }
    )
    
    return job

def use_job_queue():
    """Hook for managing job queue in Streamlit"""
    
    # Initialize job queue if not exists
    if 'job_queue' not in st.session_state:
        st.session_state.job_queue = JobQueue()
    
    def submit_job(job: Job) -> str:
        """Submit a new job"""
        return st.session_state.job_queue.add_job(job)
    
    def get_job_status(job_id: str) -> Optional[JobStatus]:
        """Get job status"""
        job = st.session_state.job_queue.get_job(job_id)
        return job.status if job else None
    
    def get_job_progress(job_id: str) -> float:
        """Get job progress"""
        job = st.session_state.job_queue.get_job(job_id)
        return job.progress if job else 0.0
    
    def cancel_job(job_id: str) -> bool:
        """Cancel a job"""
        return st.session_state.job_queue.cancel_job(job_id)
    
    def get_all_jobs() -> List[Job]:
        """Get all jobs"""
        return list(st.session_state.job_queue.jobs.values())
    
    def get_active_jobs() -> List[Job]:
        """Get active jobs"""
        return st.session_state.job_queue.get_active_jobs()
    
    def cleanup_old_jobs(max_age_hours: int = 24):
        """Clean up old completed jobs"""
        st.session_state.job_queue.cleanup_completed_jobs(max_age_hours)
    
    def poll_job_updates(job_id: str) -> Optional[Dict[str, Any]]:
        """Poll for job updates (to be called periodically)"""
        job = st.session_state.job_queue.get_job(job_id)
        if job:
            # TODO: This would integrate with actual backend polling
            # For now, just return current job state
            return job.to_dict()
        return None
    
    def simulate_job_progress(job_id: str):
        """Simulate job progress for testing (remove when backend is ready)"""
        job = st.session_state.job_queue.get_job(job_id)
        if job and job.status == JobStatus.PENDING:
            job.start()
        elif job and job.status == JobStatus.RUNNING:
            # Simulate progress
            if job.progress < 100:
                job.update_progress(
                    progress=min(100, job.progress + 5),
                    current_stage="Processing frames...",
                    processed_frames=int(job.progress * job.total_frames / 100) if job.total_frames > 0 else None
                )
            else:
                job.complete({'output_path': '/path/to/processed/video.mp4'})
    
    return {
        'queue': st.session_state.job_queue,
        'submit_job': submit_job,
        'get_job_status': get_job_status,
        'get_job_progress': get_job_progress,
        'cancel_job': cancel_job,
        'get_all_jobs': get_all_jobs,
        'get_active_jobs': get_active_jobs,
        'cleanup_old_jobs': cleanup_old_jobs,
        'poll_job_updates': poll_job_updates,
        'simulate_job_progress': simulate_job_progress,  # Remove when backend ready
        'create_video_job': create_video_processing_job,
        'create_batch_job': create_batch_processing_job
    }