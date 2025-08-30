import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Union
import streamlit as st
from dataclasses import asdict
import base64
import io

class StreamSafeAPI:
    """API client for StreamSafe backend services"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    return {'data': await response.text(), 'status': response.status}
        except Exception as e:
            return {'error': str(e), 'status': 500}
    
    # Upload and Processing APIs
    async def upload_video(self, file_data: bytes, filename: str, detection_settings: Dict[str, bool]) -> Dict[str, Any]:
        """Upload video for processing"""
        data = aiohttp.FormData()
        data.add_field('file', file_data, filename=filename)
        data.add_field('detection_settings', json.dumps(detection_settings))
        
        return await self._make_request('POST', '/api/upload', data=data)
    
    async def start_video_processing(self, job_id: str, detection_settings: Dict[str, bool]) -> Dict[str, Any]:
        """Start processing uploaded video"""
        payload = {
            'job_id': job_id,
            'detection_settings': detection_settings
        }
        return await self._make_request('POST', '/api/process/start', json=payload)
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get processing job status"""
        return await self._make_request('GET', f'/api/jobs/{job_id}/status')
    
    async def get_job_progress(self, job_id: str) -> Dict[str, Any]:
        """Get detailed job progress"""
        return await self._make_request('GET', f'/api/jobs/{job_id}/progress')
    
    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel processing job"""
        return await self._make_request('POST', f'/api/jobs/{job_id}/cancel')
    
    async def download_processed_video(self, job_id: str) -> Dict[str, Any]:
        """Download processed video"""
        return await self._make_request('GET', f'/api/jobs/{job_id}/download')
    
    # Live Streaming APIs
    async def start_live_stream(self, detection_settings: Dict[str, bool], stream_config: Dict[str, Any]) -> Dict[str, Any]:
        """Start live stream processing"""
        payload = {
            'detection_settings': detection_settings,
            'stream_config': stream_config
        }
        return await self._make_request('POST', '/api/live/start', json=payload)
    
    async def stop_live_stream(self, stream_id: str) -> Dict[str, Any]:
        """Stop live stream processing"""
        return await self._make_request('POST', f'/api/live/{stream_id}/stop')
    
    async def get_live_stream_status(self, stream_id: str) -> Dict[str, Any]:
        """Get live stream status"""
        return await self._make_request('GET', f'/api/live/{stream_id}/status')
    
    async def update_live_detection_settings(self, stream_id: str, detection_settings: Dict[str, bool]) -> Dict[str, Any]:
        """Update detection settings during live stream"""
        payload = {'detection_settings': detection_settings}
        return await self._make_request('PUT', f'/api/live/{stream_id}/settings', json=payload)
    
    async def get_live_metrics(self, stream_id: str) -> Dict[str, Any]:
        """Get live stream metrics"""
        return await self._make_request('GET', f'/api/live/{stream_id}/metrics')
    
    # WebRTC APIs
    async def create_webrtc_offer(self, offer_sdp: str, detection_settings: Dict[str, bool]) -> Dict[str, Any]:
        """Create WebRTC offer for live streaming"""
        payload = {
            'offer_sdp': offer_sdp,
            'detection_settings': detection_settings
        }
        return await self._make_request('POST', '/api/webrtc/offer', json=payload)
    
    async def handle_webrtc_answer(self, session_id: str, answer_sdp: str) -> Dict[str, Any]:
        """Handle WebRTC answer"""
        payload = {'answer_sdp': answer_sdp}
        return await self._make_request('POST', f'/api/webrtc/{session_id}/answer', json=payload)
    
    async def add_ice_candidate(self, session_id: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Add ICE candidate"""
        return await self._make_request('POST', f'/api/webrtc/{session_id}/ice', json=candidate)
    
    # System APIs
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        return await self._make_request('GET', '/api/system/health')
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get available AI models"""
        return await self._make_request('GET', '/api/models')
    
    async def get_detection_capabilities(self) -> Dict[str, Any]:
        """Get supported detection types"""
        return await self._make_request('GET', '/api/detection/capabilities')
    
    async def close(self):
        """Close API session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Synchronous wrapper functions for Streamlit compatibility
class StreamSafeAPISync:
    """Synchronous wrapper for StreamSafeAPI"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.api = StreamSafeAPI(base_url)
    
    def _run_async(self, coro):
        """Run async function in sync context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def upload_video(self, file_data: bytes, filename: str, detection_settings: Dict[str, bool]) -> Dict[str, Any]:
        return self._run_async(self.api.upload_video(file_data, filename, detection_settings))
    
    def start_video_processing(self, job_id: str, detection_settings: Dict[str, bool]) -> Dict[str, Any]:
        return self._run_async(self.api.start_video_processing(job_id, detection_settings))
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        return self._run_async(self.api.get_job_status(job_id))
    
    def get_job_progress(self, job_id: str) -> Dict[str, Any]:
        return self._run_async(self.api.get_job_progress(job_id))
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        return self._run_async(self.api.cancel_job(job_id))
    
    def start_live_stream(self, detection_settings: Dict[str, bool], stream_config: Dict[str, Any]) -> Dict[str, Any]:
        return self._run_async(self.api.start_live_stream(detection_settings, stream_config))
    
    def stop_live_stream(self, stream_id: str) -> Dict[str, Any]:
        return self._run_async(self.api.stop_live_stream(stream_id))
    
    def get_live_metrics(self, stream_id: str) -> Dict[str, Any]:
        return self._run_async(self.api.get_live_metrics(stream_id))
    
    def update_live_detection_settings(self, stream_id: str, detection_settings: Dict[str, bool]) -> Dict[str, Any]:
        return self._run_async(self.api.update_live_detection_settings(stream_id, detection_settings))
    
    def get_system_health(self) -> Dict[str, Any]:
        return self._run_async(self.api.get_system_health())

# Mock API for development (when backend isn't ready)
class MockStreamSafeAPI:
    """Mock API for frontend development"""
    
    def __init__(self):
        self.mock_jobs = {}
        self.mock_streams = {}
        import uuid
        self.uuid = uuid
    
    def upload_video(self, file_data: bytes, filename: str, detection_settings: Dict[str, bool]) -> Dict[str, Any]:
        job_id = str(self.uuid.uuid4())
        self.mock_jobs[job_id] = {
            'status': 'uploaded',
            'progress': 0,
            'filename': filename,
            'detection_settings': detection_settings
        }
        return {'job_id': job_id, 'status': 'success'}
    
    def start_video_processing(self, job_id: str, detection_settings: Dict[str, bool]) -> Dict[str, Any]:
        if job_id in self.mock_jobs:
            self.mock_jobs[job_id]['status'] = 'processing'
            return {'status': 'started', 'job_id': job_id}
        return {'error': 'Job not found'}
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        if job_id in self.mock_jobs:
            job = self.mock_jobs[job_id]
            # Simulate progress
            if job['status'] == 'processing' and job['progress'] < 100:
                job['progress'] = min(100, job['progress'] + 10)
                if job['progress'] >= 100:
                    job['status'] = 'completed'
            
            return {
                'job_id': job_id,
                'status': job['status'],
                'progress': job['progress']
            }
        return {'error': 'Job not found'}
    
    def get_job_progress(self, job_id: str) -> Dict[str, Any]:
        status = self.get_job_status(job_id)
        if 'error' not in status:
            status.update({
                'current_stage': 'Processing frames' if status['status'] == 'processing' else 'Complete',
                'processed_frames': int(status['progress'] * 1000 / 100),
                'total_frames': 1000,
                'eta_seconds': max(0, (100 - status['progress']) * 2) if status['status'] == 'processing' else 0
            })
        return status
    
    def start_live_stream(self, detection_settings: Dict[str, bool], stream_config: Dict[str, Any]) -> Dict[str, Any]:
        stream_id = str(self.uuid.uuid4())
        self.mock_streams[stream_id] = {
            'status': 'active',
            'detection_settings': detection_settings,
            'stream_config': stream_config,
            'fps': 30.0,
            'latency': 50.0,
            'detections': 0
        }
        return {'stream_id': stream_id, 'status': 'started'}
    
    def stop_live_stream(self, stream_id: str) -> Dict[str, Any]:
        if stream_id in self.mock_streams:
            self.mock_streams[stream_id]['status'] = 'stopped'
            return {'status': 'stopped'}
        return {'error': 'Stream not found'}
    
    def get_live_metrics(self, stream_id: str) -> Dict[str, Any]:
        if stream_id in self.mock_streams:
            stream = self.mock_streams[stream_id]
            # Simulate changing metrics
            import random
            return {
                'stream_id': stream_id,
                'fps': round(stream['fps'] + random.uniform(-2, 2), 1),
                'latency': round(stream['latency'] + random.uniform(-10, 10), 1),
                'detections': stream['detections'] + random.randint(0, 5),
                'status': stream['status']
            }
        return {'error': 'Stream not found'}
    
    def get_system_health(self) -> Dict[str, Any]:
        return {
            'status': 'healthy',
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'gpu_usage': 23.1,
            'active_streams': len([s for s in self.mock_streams.values() if s['status'] == 'active']),
            'active_jobs': len([j for j in self.mock_jobs.values() if j['status'] == 'processing'])
        }

# Helper functions
def get_api_client(use_mock: bool = True) -> Union[StreamSafeAPISync, MockStreamSafeAPI]:
    """Get appropriate API client"""
    if use_mock or st.secrets.get("USE_MOCK_API", True):
        return MockStreamSafeAPI()
    else:
        base_url = st.secrets.get("STREAMSAFE_API_URL", "http://localhost:8000")
        return StreamSafeAPISync(base_url)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def validate_video_file(file_data: bytes, filename: str) -> Dict[str, Any]:
    """Validate uploaded video file"""
    # Check file size (limit to 100MB for demo)
    max_size = 100 * 1024 * 1024
    if len(file_data) > max_size:
        return {'valid': False, 'error': f'File too large. Maximum size is {format_file_size(max_size)}'}
    
    # Check file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    if not any(filename.lower().endswith(ext) for ext in valid_extensions):
        return {'valid': False, 'error': f'Invalid file type. Supported: {", ".join(valid_extensions)}'}
    
    return {'valid': True, 'size': len(file_data), 'formatted_size': format_file_size(len(file_data))}

def create_detection_payload(detection_settings: Dict[str, bool]) -> Dict[str, Any]:
    """Create detection settings payload for API"""
    return {
        'license_plates': detection_settings.get('license_plates', True),
        'street_signs': detection_settings.get('street_signs', True), 
        'block_numbers': detection_settings.get('block_numbers', False),
        'faces': detection_settings.get('faces', True),
        'documents': detection_settings.get('documents', True),
        'screens': detection_settings.get('screens', False)
    }