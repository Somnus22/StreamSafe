import time
import math
from typing import Dict, List, Any, Optional, Union
import streamlit as st
import base64
import io

def format_fps(fps: float) -> str:
    """Format FPS for display"""
    if fps >= 1:
        return f"{fps:.1f}"
    elif fps > 0:
        return f"{fps:.2f}"
    else:
        return "0.0"

def format_latency(latency_ms: float) -> str:
    """Format latency in milliseconds"""
    if latency_ms >= 1000:
        return f"{latency_ms/1000:.1f}s"
    else:
        return f"{latency_ms:.0f}ms"

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def format_bitrate(bitrate_bps: int) -> str:
    """Format bitrate for display"""
    if bitrate_bps >= 1_000_000:
        return f"{bitrate_bps/1_000_000:.1f} Mbps"
    elif bitrate_bps >= 1_000:
        return f"{bitrate_bps/1_000:.0f} Kbps"
    else:
        return f"{bitrate_bps} bps"

def calculate_eta(progress: float, elapsed_seconds: float) -> Optional[float]:
    """Calculate estimated time to completion"""
    if progress <= 0 or progress >= 100:
        return None
    
    rate = progress / elapsed_seconds
    remaining_progress = 100 - progress
    return remaining_progress / rate if rate > 0 else None

def format_eta(eta_seconds: Optional[float]) -> str:
    """Format ETA for display"""
    if eta_seconds is None or eta_seconds <= 0:
        return "Unknown"
    
    return format_duration(eta_seconds)

def get_detection_icon(detection_type: str) -> str:
    """Get emoji icon for detection type"""
    icons = {
        'license_plates': '🚗',
        'street_signs': '📍',
        'block_numbers': '🏠',
        'faces': '👤',
        'documents': '📄',
        'screens': '💻',
        'phones': '📱',
        'credit_cards': '💳'
    }
    return icons.get(detection_type, '🔍')

def get_status_color(status: str) -> str:
    """Get color for status indicators"""
    colors = {
        'online': '#10b981',
        'offline': '#6b7280',
        'active': '#10b981',
        'inactive': '#6b7280',
        'streaming': '#3b82f6',
        'processing': '#f59e0b',
        'completed': '#10b981',
        'failed': '#ef4444',
        'pending': '#6b7280',
        'cancelled': '#6b7280'
    }
    return colors.get(status.lower(), '#6b7280')

def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    emojis = {
        'online': '🟢',
        'offline': '⚫',
        'active': '🟢', 
        'inactive': '⚫',
        'streaming': '🔴',
        'processing': '🟡',
        'completed': '✅',
        'failed': '❌',
        'pending': '⏳',
        'cancelled': '⭕'
    }
    return emojis.get(status.lower(), '⚫')

def validate_detection_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Validate detection settings"""
    valid_settings = {}
    
    # Define valid detection types
    valid_types = [
        'license_plates', 'street_signs', 'block_numbers', 
        'faces', 'documents', 'screens', 'phones', 'credit_cards'
    ]
    
    for key, value in settings.items():
        if key in valid_types and isinstance(value, bool):
            valid_settings[key] = value
    
    # Set defaults for missing required settings
    defaults = {
        'license_plates': True,
        'street_signs': True,
        'block_numbers': False,
        'faces': True,
        'documents': True,
        'screens': False
    }
    
    for key, default_value in defaults.items():
        if key not in valid_settings:
            valid_settings[key] = default_value
    
    return valid_settings

def create_progress_bar_html(progress: float, color: str = "#8b5cf6", height: str = "8px") -> str:
    """Create custom progress bar HTML"""
    return f"""
    <div style="width: 100%; background: #374151; border-radius: 4px; height: {height}; overflow: hidden;">
        <div style="width: {progress}%; background: {color}; height: 100%; transition: width 0.3s ease; border-radius: 4px;"></div>
    </div>
    """

def create_metric_card(title: str, value: str, delta: Optional[str] = None, icon: str = "") -> str:
    """Create custom metric card HTML"""
    delta_html = ""
    if delta:
        delta_color = "#10b981" if not delta.startswith("-") else "#ef4444"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.8rem; margin-top: 0.25rem;">{delta}</div>'
    
    return f"""
    <div style="background: #1f2937; border-radius: 8px; padding: 1rem; border: 1px solid #374151;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem;">{icon}</span>
            <span style="color: #9ca3af; font-size: 0.85rem; text-transform: uppercase; font-weight: 600;">{title}</span>
        </div>
        <div style="color: white; font-size: 1.5rem; font-weight: 700;">{value}</div>
        {delta_html}
    </div>
    """

def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary"""
    return dictionary.get(key, default)

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_len = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_len] + ('.' + ext if ext else '')
    
    return filename

def encode_image_for_display(image_bytes: bytes, format: str = "PNG") -> str:
    """Encode image bytes for HTML display"""
    encoded = base64.b64encode(image_bytes).decode()
    return f"data:image/{format.lower()};base64,{encoded}"

def create_download_link(data: bytes, filename: str, text: str = "Download") -> str:
    """Create download link for binary data"""
    encoded = base64.b64encode(data).decode()
    href = f"data:application/octet-stream;base64,{encoded}"
    return f'<a href="{href}" download="{filename}" style="color: #8b5cf6; text-decoration: none; font-weight: 600;">{text}</a>'

def format_detection_count(count: int) -> str:
    """Format detection count for display"""
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count/1_000:.1f}K"
    else:
        return str(count)

def calculate_processing_speed(frames_processed: int, elapsed_seconds: float) -> float:
    """Calculate processing speed in FPS"""
    if elapsed_seconds <= 0:
        return 0.0
    return frames_processed / elapsed_seconds

def estimate_processing_time(total_frames: int, current_fps: float) -> float:
    """Estimate total processing time"""
    if current_fps <= 0:
        return 0.0
    return total_frames / current_fps

def get_quality_settings(quality: str) -> Dict[str, Any]:
    """Get quality settings for video processing"""
    settings = {
        'low': {
            'resolution': '480p',
            'bitrate': 1000000,  # 1 Mbps
            'fps': 24
        },
        'medium': {
            'resolution': '720p', 
            'bitrate': 3000000,  # 3 Mbps
            'fps': 30
        },
        'high': {
            'resolution': '1080p',
            'bitrate': 8000000,  # 8 Mbps
            'fps': 30
        },
        'ultra': {
            'resolution': '4K',
            'bitrate': 20000000,  # 20 Mbps
            'fps': 30
        }
    }
    return settings.get(quality.lower(), settings['medium'])

def create_alert_html(message: str, alert_type: str = "info") -> str:
    """Create custom alert HTML"""
    colors = {
        'info': {'bg': '#1e40af', 'border': '#3b82f6', 'text': '#dbeafe'},
        'success': {'bg': '#166534', 'border': '#22c55e', 'text': '#dcfce7'},
        'warning': {'bg': '#d97706', 'border': '#f59e0b', 'text': '#fef3c7'},
        'error': {'bg': '#dc2626', 'border': '#ef4444', 'text': '#fecaca'}
    }
    
    color = colors.get(alert_type, colors['info'])
    
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    icon = icons.get(alert_type, '!')
    
    return f"""
    <div style="
        background: {color['bg']};
        border-left: 4px solid {color['border']};
        color: {color['text']};
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    ">
        <span style="font-size: 1.2rem;">{icon}</span>
        <span>{message}</span>
    </div>
    """

def debounce(func, delay: float = 0.5):
    """Simple debounce decorator for Streamlit"""
    last_called = [0.0]
    
    def wrapper(*args, **kwargs):
        now = time.time()
        if now - last_called[0] >= delay:
            last_called[0] = now
            return func(*args, **kwargs)
        return None
    
    return wrapper

class StreamlitCache:
    """Simple cache for Streamlit session state"""
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get cached value"""
        return st.session_state.get(f"cache_{key}", default)
    
    @staticmethod
    def set(key: str, value: Any, ttl: float = 3600) -> None:
        """Set cached value with TTL"""
        st.session_state[f"cache_{key}"] = value
        st.session_state[f"cache_{key}_expires"] = time.time() + ttl
    
    @staticmethod
    def is_expired(key: str) -> bool:
        """Check if cached value is expired"""
        expires_key = f"cache_{key}_expires"
        if expires_key not in st.session_state:
            return True
        return time.time() > st.session_state[expires_key]
    
    @staticmethod
    def clear(key: str = None) -> None:
        """Clear cache (specific key or all)"""
        if key:
            keys_to_remove = [f"cache_{key}", f"cache_{key}_expires"]
            for k in keys_to_remove:
                if k in st.session_state:
                    del st.session_state[k]
        else:
            # Clear all cache keys
            cache_keys = [k for k in st.session_state.keys() if k.startswith("cache_")]
            for k in cache_keys:
                del st.session_state[k]