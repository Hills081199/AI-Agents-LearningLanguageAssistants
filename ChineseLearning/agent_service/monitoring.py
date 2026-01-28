import time
import psutil
import threading
from typing import Dict, Any
from collections import deque
from datetime import datetime, timedelta

class PerformanceMonitor:
    """Monitor system performance and request metrics."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.request_times = deque(maxlen=max_history)
        self.request_counts = {}
        self.error_counts = {}
        self.start_time = time.time()
        self._lock = threading.Lock()
    
    def record_request(self, endpoint: str, duration: float, success: bool = True):
        """Record a request with its duration and success status."""
        with self._lock:
            self.request_times.append({
                'timestamp': datetime.now(),
                'endpoint': endpoint,
                'duration': duration,
                'success': success
            })
            
            # Update counts
            key = f"{endpoint}_{success}"
            self.request_counts[key] = self.request_counts.get(key, 0) + 1
            
            if not success:
                self.error_counts[endpoint] = self.error_counts.get(endpoint, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            if not self.request_times:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'success_rate': 100,
                    'requests_per_minute': 0,
                    'system_cpu': psutil.cpu_percent(),
                    'system_memory': psutil.virtual_memory().percent
                }
            
            # Calculate metrics
            total_requests = len(self.request_times)
            successful_requests = sum(1 for r in self.request_times if r['success'])
            avg_response_time = sum(r['duration'] for r in self.request_times) / total_requests
            success_rate = (successful_requests / total_requests) * 100
            
            # Calculate requests per minute (last minute)
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            recent_requests = [r for r in self.request_times if r['timestamp'] > one_minute_ago]
            requests_per_minute = len(recent_requests)
            
            return {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'avg_response_time': round(avg_response_time, 2),
                'success_rate': round(success_rate, 2),
                'requests_per_minute': requests_per_minute,
                'system_cpu': psutil.cpu_percent(),
                'system_memory': psutil.virtual_memory().percent,
                'uptime_seconds': round(time.time() - self.start_time, 2),
                'error_counts': dict(self.error_counts)
            }
    
    def get_slow_requests(self, threshold: float = 5.0) -> list:
        """Get requests slower than threshold."""
        with self._lock:
            return [
                {
                    'timestamp': r['timestamp'].isoformat(),
                    'endpoint': r['endpoint'],
                    'duration': r['duration']
                }
                for r in self.request_times 
                if r['duration'] > threshold
            ]

# Global performance monitor
perf_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        endpoint = func.__name__
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            perf_monitor.record_request(endpoint, duration, success=True)
            return result
        except Exception as e:
            duration = time.time() - start_time
            perf_monitor.record_request(endpoint, duration, success=False)
            raise e
    
    return wrapper

# System health check
def check_system_health() -> Dict[str, Any]:
    """Check system health status."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    health_status = "healthy"
    issues = []
    
    if cpu_percent > 80:
        health_status = "warning"
        issues.append(f"High CPU usage: {cpu_percent}%")
    
    if memory.percent > 85:
        health_status = "warning"
        issues.append(f"High memory usage: {memory.percent}%")
    
    if disk.percent > 90:
        health_status = "critical"
        issues.append(f"Low disk space: {disk.percent}% used")
    
    return {
        'status': health_status,
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent,
        'issues': issues,
        'uptime': time.time() - perf_monitor.start_time
    }

# Cache performance monitoring
def get_cache_stats() -> Dict[str, Any]:
    """Get cache performance statistics."""
    from cache import cache_manager
    
    return {
        'cache_stats': cache_manager.get_stats(),
        'cache_hit_rate': calculate_cache_hit_rate()
    }

def calculate_cache_hit_rate() -> float:
    """Calculate cache hit rate from recent requests."""
    with perf_monitor._lock:
        if not perf_monitor.request_times:
            return 0.0
        
        # Simple heuristic: if response time < 1 second, likely cache hit
        fast_requests = sum(1 for r in perf_monitor.request_times if r['duration'] < 1.0)
        return (fast_requests / len(perf_monitor.request_times)) * 100
